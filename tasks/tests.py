import io
import json
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import time
import logging
from tqdm import tqdm

# Global error counter
log_buffer = io.StringIO()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(log_buffer)])
logger = logging.getLogger(__name__)

basis_file = "config/basis.config"

with open(basis_file) as json_file:
    basis_settings = json.load(json_file)

url = f"http://{basis_settings['couch']['host']}:{basis_settings['couch']['port']}"
DB = f"{url}/{basis_settings['couch']['database']}"
username = f"{basis_settings['couch']['user']}"
password = f"{basis_settings['couch']['passwd']}"
database = f"{basis_settings['couch']['database']}"

DB_BASE = f"{url}/"
DB = f"{url}/{database}"

# Function to ensure the database exists
def ensure_database_exists(database_name):
    if database_name != f"{database}":
        database_name = f"{database}_{database_name}"

    address = f"{DB_BASE}{database_name}"

    try:
        response = requests.get(address, auth=HTTPBasicAuth(username, password))

        if response.status_code == 404:
            create_db_response = requests.put(address, auth=HTTPBasicAuth(username, password))

            if create_db_response.status_code == 201:
                logger.info(f"Database '{database_name}' created successfully.")
            else:
                logger.error(f"Failed to create database '{database_name}': {create_db_response.status_code} - {create_db_response.text}")
        elif response.status_code == 200:
            logger.info(f"Database '{database_name}' already exists.")
        else:
            logger.error(f"Error connecting to the database '{database_name}': {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while connecting to '{database_name}': {str(e)}")
        return False
    
    return True

# Initialize setup
def initialize_setup():
    db_list = [f"{database}", "active"]
    for db in db_list:
        ensure_database_exists(db)

# Fetch entries from the database
def fetch_entries(batch_size=9000):
    all_docs_url = f"{DB}/_all_docs?include_docs=true&limit={batch_size}"
    last_key = None
    all_documents = []

    while True:
        url = all_docs_url
        if last_key:
            url += f"&startkey={last_key}"

        response = requests.get(url, auth=HTTPBasicAuth(username, password))
        if response.status_code == 200:
            data = response.json()
            rows = data.get('rows', [])
            documents = [row['doc'] for row in rows]
            all_documents.extend(documents)

            if len(rows) < batch_size:
                break

            last_key = f'"{rows[-1]["id"]}"'

        else:
            logger.error(f"Error fetching documents: {response.status_code} - {response.text}")
            break

    return all_documents

# Filter entries into active and archive lists
def filter_entries():
    documents = fetch_entries()
    if not documents:
        logger.warning("No documents found.")
        return [], []

    active_documents = []
    archive_documents = []
    
    eight_days_ago = datetime.now() - timedelta(days=8)

    for doc in tqdm(documents, desc="Filtering entries", unit="doc"):
        date_ordered_timestamp = doc.get('date_ordered')
        if date_ordered_timestamp:
            date_ordered = datetime.fromtimestamp(date_ordered_timestamp)

            if date_ordered > eight_days_ago:
                active_documents.append(doc)
            else:
                archive_documents.append(doc)

    return active_documents, archive_documents

# Update patient records and increment error count on failures
def update_patient_records(archive_documents):
    global error_misc, error_fetch, error_update, patient_update
    patient_db_base_url = f"{DB_BASE}{database}_patients/"

    patient_update = 0
    error_update = 0
    error_fetch = 0
    error_misc = 0

    for doc in tqdm(archive_documents, desc="Updating patient status", unit="doc"):
        patient_id = doc.get('patient_id')
        if not patient_id:
            logger.warning(f"No patient ID found for document: {doc.get('_id')}")
            error_misc += 1
            continue

        patient_url = f"{patient_db_base_url}{patient_id}"
        
        try:
            response = requests.get(patient_url, auth=HTTPBasicAuth(username, password))

            if response.status_code == 200:
                patient_doc = response.json()
                patient_doc["archived"] = True 

                save_response = requests.put(patient_url, json=patient_doc, auth=HTTPBasicAuth(username, password))

                if save_response.status_code in [200, 201]:
                    logger.info(f"Patient '{patient_id}' updated successfully.")
                    patient_update += 1
                else:
                    logger.error(f"Failed to update patient '{patient_id}': {save_response.status_code} - {save_response.text}")
                    error_update += 1

            else:
                # logger.error(f"Failed to fetch patient '{patient_id}': {response.status_code} - {response.text}")
                error_fetch += 1

        except requests.exceptions.RequestException as e:
            logger.error(f"Error occurred while updating patient '{patient_id}': {str(e)}")
            error_update += 1

    return patient_update

# Save active documents and increment error count on failures
def save_active_entries(active_documents):
    global error_misc
    if not active_documents:
        logger.info("No active documents to save.")
        return

    active_db = f"{DB_BASE}{database}_active"
    
    if not ensure_database_exists("active"):
        logger.error("Failed to ensure 'active' database exists.")
        error_misc += 1
        return
    
    for doc in tqdm(active_documents, desc="Saving active entries", unit="doc"):
        if '_rev' in doc:
            del doc['_rev']
        
        doc_id = doc.get('_id')
        if not doc_id:
            logger.warning(f"Document without '_id' found: {doc}")
            error_misc += 1
            continue

        save_url = f"{active_db}/{doc_id}"

        try:
            response = requests.put(save_url, json=doc, auth=HTTPBasicAuth(username, password))

            if response.status_code in [200, 201]:
                logger.info(f"Document '{doc_id}' saved successfully.")
            else:
                logger.error(f"Failed to save document '{doc_id}': {response.status_code} - {response.text}")
                error_count += 1
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error occurred while saving document '{doc_id}': {str(e)}")
            error_misc += 1

# Housekeeping function to delete databases
def house_keeping_please(db_name):
    global error_misc
    drop_db_url = f"{DB_BASE}{db_name}"

    try:
        response = requests.delete(drop_db_url, auth=HTTPBasicAuth(username, password))

        if response.status_code == 200:
            logger.info(f"Database {db_name} deleted successfully.")
        elif response.status_code == 404:
            logger.warning(f"Database {db_name} not found.")
        else:
            logger.error(f"Failed to delete database {db_name}: {response.status_code} - {response.text}")
            error_misc += 1

    except requests.exceptions.RequestException as e:
        logger.error(f"Error occurred while deleting the {db_name} database: {str(e)}")
        error_misc += 1

# migration
def exodus():
    global error_misc, error_fetch
    source_db = f"{DB_BASE}{database}_active"
    target_db = f"{DB_BASE}{database}"
    batch_size = 9000
    last_key = None

    while True:
        url = f"{source_db}/_all_docs?include_docs=true&limit={batch_size}"
        if last_key:
            url += f"&startkey={last_key}"

        response = requests.get(url, auth=HTTPBasicAuth(username, password))
        if response.status_code != 200:
            logger.error(f"Error fetching documents from '{database}_active': {response.status_code} - {response.text}")
            error_fetch += 1
            break

        data = response.json()
        rows = data.get('rows', [])
        if not rows:
            break

        for row in tqdm(rows, desc="Exodus process", unit="doc"):
            doc = row.get('doc')
            if not doc:
                continue

            if '_rev' in doc:
                del doc['_rev']

            doc_id = doc.get('_id')
            if not doc_id:
                logger.warning(f"Document without '_id' found: {doc}")
                error_count += 1
                continue

            save_url = f"{target_db}/{doc_id}"

            try:
                save_response = requests.put(save_url, json=doc, auth=HTTPBasicAuth(username, password))

                if save_response.status_code not in [200, 201]:
                    logger.error(f"Failed to save document '{doc_id}' to '{database}': {save_response.status_code} - {save_response.text}")
                    error_misc += 1
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Error occurred while saving document '{doc_id}' to '{database}': {str(e)}")
                error_misc += 1

        last_key = f'"{rows[-1]["id"]}"' if rows else None
        if len(rows) < batch_size:
            break
    
# satrt replication
def lazarous():
    import json
    import subprocess

    replications_file = "config/replications.config"
    ward_file = "config/department.config"
    log_file = "logs/replication_errors.log"

    with open(replications_file) as json_file:
        replication_settings = json.load(json_file)

    with open(ward_file) as json_file:
        wards_data = json.load(json_file)

    department_name = replication_settings["specific_department"]["department"]
    wards = []
    for department in wards_data["departments"]:
        if department["name"] == department_name:
            wards = department["wards"]
            break

    source_url = f"http://{replication_settings['source']['user']}:{replication_settings['source']['passwd']}@{replication_settings['source']['host']}:{replication_settings['source']['port']}/{replication_settings['source_base_db']['database']}"
    target_url = f"http://{replication_settings['target']['user']}:{replication_settings['target']['password']}@{replication_settings['target']['host']}:{replication_settings['target']['port']}/{replication_settings['target_base_db']['database']}"
    replicator_db_url = f"http://{replication_settings['source']['user']}:{replication_settings['source']['passwd']}@{replication_settings['source']['host']}:{replication_settings['source']['port']}/_replicator"

    create_replicator_db_cmd = ['curl', '-X', 'PUT', replicator_db_url]
    try:
        subprocess.run(create_replicator_db_cmd, check=True, capture_output=True, text=True)
        with open(log_file, 'a') as log:
            log.write(f"Created replicator databese:\n")
    except subprocess.CalledProcessError as e:
        with open(log_file, 'a') as log:
            log.write(f"Error creating _replicator database: {e.stderr}\n")

    design_id = (replication_settings["source"]["host"]).replace('.','')

    design_doc = {
        "filters": {
            f"ward_filter_{design_id}": f"function(doc, req) {{ var wards = {json.dumps(wards)}; return wards.includes(doc.ward); }}"
        }
    }

    create_design_doc_cmd = [
        'curl', '-d', json.dumps(design_doc), '-H', 'Content-Type: application/json',
        '-X', 'PUT', f"{target_url}/_design/ward_filter_{design_id}"
    ]
    try:
        result = subprocess.run(create_design_doc_cmd, check=True, capture_output=True, text=True)
        with open(log_file, 'a') as log:
            log.write(f"Design document created successfully on the target database\n")

    except subprocess.CalledProcessError as e:
        with open(log_file, 'a') as log:
            log.write(f"Error creating design document: {e.stderr}\n")

    def execute_replication(command, log_message):
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            with open(log_file, 'a') as log:
                log.write(f"Replication setup:\n")
        except subprocess.CalledProcessError as e:
            with open(log_file, 'a') as log:
                log.write(f"Error: {log_message}\n{e.stderr}\n")

    source_to_target_cmd = [
        'curl', '-d', json.dumps({
            "_id": "base-source-to-target",
            "source": source_url,
            "target": target_url,
            "create_target": True,
            "continuous": True
        }), '-H', 'Content-Type: application/json', '-X', 'POST', replicator_db_url
    ]

    target_to_source_cmd =[
        'curl', '-d', json.dumps({
            "_id": "target-to-source-filtered",
            "source": target_url,
            "target": source_url,
            "create_target": True,
            "continuous": True,
            "filter": f"ward_filter_{design_id}/ward_filter_{design_id}"
        }), '-H', 'Content-Type: application/json', '-X', 'POST', replicator_db_url
    ]

    execute_replication(source_to_target_cmd, "Setting up replication from source to target")
    execute_replication(target_to_source_cmd, "Setting up filtered replication from target to source")


    sub_directories = ["_lab_test_panels", "_lab_test_type", "_patients", "_users"]

    for suffix in sub_directories:
        source_suffix_url = f"{replication_settings['source_base_db']['database']}{suffix}"
        target_suffix_url = f"{replication_settings['target_base_db']['database']}{suffix}"
        
        source_url = f"http://{replication_settings['source']['user']}:{replication_settings['source']['passwd']}@{replication_settings['source']['host']}:{replication_settings['source']['port']}/{source_suffix_url}"
        target_url = f"http://{replication_settings['target']['user']}:{replication_settings['target']['password']}@{replication_settings['target']['host']}:{replication_settings['target']['port']}/{target_suffix_url}"

        source_to_target_cmd = [
            'curl', '-d', json.dumps({
                "_id": f"base-source-to-target_{suffix}",
                "source": source_url,
                "target": target_url,
                "create_target": True,
                "continuous": True
            }), '-H', 'Content-Type: application/json', '-X', 'POST', replicator_db_url
        ]
        
        target_to_source_cmd_ltp = [
            'curl', '-d', json.dumps({
                "_id": f"base-target-to-source_{suffix}",
                "source": target_url,
                "target": source_url,
                "create_target": True,
                "continuous": True,
            }), '-H', 'Content-Type: application/json', '-X', 'POST', replicator_db_url
        ]

        execute_replication(source_to_target_cmd, f"Replication setup from source to target for {suffix}")
        execute_replication(target_to_source_cmd_ltp, f"Replication setup from target to source for {suffix}")


# Log final results
if __name__ == "__main__":
    initialize_setup()
    active_docs, archive_docs = filter_entries()
    patient_update = update_patient_records(archive_docs)
    save_active_entries(active_docs)
    house_keeping_please(f"{database}")
    ensure_database_exists(f"{database}")
    exodus()
    house_keeping_please(f"{database}_active")
    house_keeping_please("_replicator")

    # Log final messages with document and error counts
    logger.info(f"Documents Updated patient: {patient_update}")
    logger.warning(f"Error: None" if patient_update else f"Error: No updates")
    logger.info(f"Active Documents count: {len(active_docs)}")
    logger.info(f"Old Documents count: {len(archive_docs)}")
    logger.error(f"Errors Fetching docs: {error_fetch}")
    logger.error(f"Errors Updating docs: {error_update}")
    logger.error(f"Errors - Misc: {error_misc}")
    logger.info(f"Database_created: {database}")

    # Print all buffered log messages at the end
    print(log_buffer.getvalue())
    time.sleep(10)
    print("\n\nSetting up replication now...")
    lazarous()

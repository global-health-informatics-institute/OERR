import requests
from requests.auth import HTTPBasicAuth
from config import url, username, password
from datetime import datetime, timedelta
import logging
from tqdm import tqdm  # Import tqdm for progress bars

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_BASE = f"{url}/"
DB = f"{url}/oerr"

# CodeA_Helper
def ensure_database_exists(database_name):
    if database_name != "oerr":
        database_name = f"oerr_{database_name}"

    address = f"{DB_BASE}{database_name}"

    try:
        response = requests.get(address, auth=HTTPBasicAuth(username, password))

        if response.status_code == 404:
            create_db_response = requests.put(address, auth=HTTPBasicAuth(username, password))

            if create_db_response.status_code == 201:
                logging.info(f"Database '{database_name}' created successfully.")
            else:
                logging.error(f"Failed to create database '{database_name}': {create_db_response.status_code} - {create_db_response.text}")
        elif response.status_code == 200:
            logging.info(f"Database '{database_name}' already exists.")
        else:
            logging.error(f"Error connecting to the database '{database_name}': {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while connecting to '{database_name}': {str(e)}")
        return False
    
    return True

# CodeA
def initialize_setup():
    db_list = ["oerr", "active"]
    for db in db_list:
        ensure_database_exists(db)

# CodeB
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
            logging.error(f"Error fetching documents: {response.status_code} - {response.text}")
            break

    return all_documents

# CodeC
def filter_entries():
    documents = fetch_entries()
    if not documents:
        logging.warning("Mostly - No documents found but ey maybe error fetching documents.")
        return

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

# codeD1
def update_patient():
    patient_url = f"{DB_BASE}oerr_patient"
    archive_documents = filter_entries()
    if not archive_documents:
        logging.info("No Archive documents available.")
        return
    
    for doc in tqdm(archive_documents, desc="Updating the status", unit="doc"):
        patient_id = doc.get('patient_id')

        try:
            response = requests.get(patient_url, auth=HTTPBasicAuth(username, password))

            if response.status_code == 200:
                patient_doc = response.json()
                patient_doc["archived"] = True 

                save_response = requests.put(patient_url, json=patient_doc, auth=HTTPBasicAuth(username,password))

                if (save_response.status_code in [200, 201]):
                    logging.info(f"Patient '{patient_id}' updated successfully.")
                else:
                    logging.error(f"Failed to update patient '{patient_id}': {save_response.status_code} - {save_response.text}")

            else:
                logging.error(f"Failed to fetch patient '{patient_id}': {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred while updating patient '{patient_id}': {str(e)}")

            
            

# CodeD
def save_active_entries():
    # Fetch cleaned documents
    active_documents = filter_entries()
    if not active_documents:
        logging.info("No active documents to save.")
        return

    active_db = f"{DB_BASE}oerr_active"
    
    if not ensure_database_exists("active"):
        logging.error("Failed to ensure 'oerr_active' database exists.")
        return
    
    for doc in tqdm(active_documents, desc="Saving active entries", unit="doc"):
        if '_rev' in doc:
            del doc['_rev']
        
        doc_id = doc.get('_id')
        if not doc_id:
            logging.warning(f"Document without '_id' found: {doc}")
            continue

        save_url = f"{active_db}/{doc_id}"

        try:
            response = requests.put(save_url, json=doc, auth=HTTPBasicAuth(username, password))

            if response.status_code in [200, 201]:
                logging.info(f"Document '{doc_id}' saved successfully.")
            else:
                logging.error(f"Failed to save document '{doc_id}': {response.status_code} - {response.text}")
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred while saving document '{doc_id}': {str(e)}")


# codeE
def house_keeping_please(db_name):
    drop_db_url = f"{DB_BASE}{db_name}"

    try:
        response = requests.delete(drop_db_url, auth=HTTPBasicAuth(username, password))

        if response.status_code == 200:
            logging.info(f"Database {db_name} deleted successfully.")
        elif response.status_code == 404:
            logging.warning(f"Database {db_name} not found.")
        else:
            logging.error(f"Failed to delete database {db_name}: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred while deleting the {db_name} database: {str(e)}")

# codeF
def exodus():
    # Set up the source and target databases
    source_db = f"{DB_BASE}oerr_active"
    target_db = f"{DB_BASE}oerr"
    batch_size = 9000
    last_key = None

    while True:
        # Fetch a batch of documents from oerr_active
        url = f"{source_db}/_all_docs?include_docs=true&limit={batch_size}"
        if last_key:
            url += f"&startkey={last_key}"

        response = requests.get(url, auth=HTTPBasicAuth(username, password))
        if response.status_code != 200:
            logging.error(f"Error fetching documents from 'oerr_active': {response.status_code} - {response.text}")
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
                logging.warning(f"Document without '_id' found: {doc}")
                continue

            save_url = f"{target_db}/{doc_id}"

            try:
                save_response = requests.put(save_url, json=doc, auth=HTTPBasicAuth(username, password))

                if save_response.status_code not in [200, 201]:
                    logging.error(f"Failed to save document '{doc_id}' to 'oerr': {save_response.status_code} - {save_response.text}")
            
            except requests.exceptions.RequestException as e:
                logging.error(f"Error occurred while saving document '{doc_id}' to 'oerr': {str(e)}")

        last_key = f'"{rows[-1]["id"]}"'

        # If less than a full batch was returned, We done!
        if len(rows) < batch_size:
            break

if __name__ == "__main__":
    initialize_setup()
    update_patient()
    save_active_entries()
    house_keeping_please("oerr")
    ensure_database_exists("oerr")
    exodus()
    house_keeping_please("oerr_active")

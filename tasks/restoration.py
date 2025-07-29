import json
import requests
from requests.auth import HTTPBasicAuth
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load config settings
basis_file = "config/basis.config"
with open(basis_file) as json_file:
    basis_settings = json.load(json_file)

# Setup CouchDB connection details
url = f"http://{basis_settings['couch']['host']}:{basis_settings['couch']['port']}"
username = f"{basis_settings['couch']['user']}"
password = f"{basis_settings['couch']['passwd']}"
database = f"{basis_settings['couch']['database']}"

DB_BASE = f"{url}/"
Test_DB = f"{url}/{database}"
Patient_DB = f"{url}/{database}_patients"
Archive_DB = f"{url}/{database}_archive"

# Function to fetch patient IDs where "archive" = "restored"
def fetch_patient_ids():
    restore_ids = []
    logging.info("Fetching patient IDs with 'archived' = 'restored' using Mango query")

    query = {
        "selector": {
            "archived": "restored"
        },
        "fields": ["_id"],
        "limit": 1000 
    }

    response = requests.post(f"{Patient_DB}/_find", json=query, auth=HTTPBasicAuth(username, password))
    if response.status_code == 200:
        data = response.json()
        for doc in data['docs']:
            restore_ids.append(doc['_id'])
        logging.info(f"Found {len(restore_ids)} restored patients.")
    else:
        logging.error(f"Failed to fetch patient IDs: {response.status_code} - {response.text}")
    
    return restore_ids

# Function to fetch test documents for given patient IDs
def fetch_test_docs():
    restore_tests = []
    patient_ids = fetch_patient_ids()
    
    if not patient_ids:
        logging.info("No patient IDs found.")
        return restore_tests
    
    logging.info(f"Fetching test documents for {len(patient_ids)} patients.")
    
    for patient_id in tqdm(patient_ids, desc="Fetching test documents"):
        # Use Mango query to find documents by patient_id
        query = {
            "selector": {
                "patient_id": patient_id
            },
            "limit": 1000  # Adjust limit as needed
        }

        response = requests.post(f"{Archive_DB}/_find", json=query, auth=HTTPBasicAuth(username, password))

        if response.status_code == 200:
            data = response.json()
            for doc in data['docs']:
                restore_tests.append(doc)
        else:
            logging.error(f"Failed to fetch test docs for patient {patient_id}: {response.status_code} - {response.text}")
            continue
    
    logging.info(f"Found {len(restore_tests)} test documents to restore.")
    return restore_tests


def restore_test_doc():
    restore_tests = fetch_test_docs()

    if not restore_tests:
        logging.info("No documents to restore.")
        return

    logging.info("Restoring documents to Test_DB.")
    
    for doc in tqdm(restore_tests, desc="Restoring test docs"):
        # Remove _rev field to ensure CouchDB treats it as a new document
        if '_rev' in doc:
            del doc['_rev']
        
        _id = doc['_id']
        response = requests.put(f"{Test_DB}/{_id}", json=doc, auth=HTTPBasicAuth(username, password))

        if response.status_code in [200, 201]:
            f"Successfully restored {_id}"
        else:
            f"Failed to restore {_id}: {response.status_code} - {response.text}"
            continue


# Function to delete original documents from Archive_DB
def delete_original_doc():
    restore_tests = fetch_test_docs()

    if not restore_tests:
        logging.info("\n\nNo documents to delete.")
        return
    
    logging.info("\n\nDeleting original documents from archive.")
    
    for doc in tqdm(restore_tests, desc="Deleting original docs"):
        _id = doc['_id']
        _rev = doc['_rev']
        response = requests.delete(f"{Archive_DB}/{_id}?rev={_rev}", auth=HTTPBasicAuth(username, password))
        
        if response.status_code == 200:
            f"Successfully deleted {_id}"
        else:
            f"Failed to delete {_id}: {response.status_code} - {response.text}"



def clean_up():
    clean_up_ids = fetch_patient_ids()
    
    if not clean_up_ids:
        logging.info("\n\nNo patients to clean up.")
        return
    
    logging.info(f"\n\nCleaning up 'archived' field for {len(clean_up_ids)} patients.")

    for patient_id in tqdm(clean_up_ids, desc="Cleaning up patient attribute"):
        response = requests.get(f"{Patient_DB}/{patient_id}", auth=HTTPBasicAuth(username, password))
        
        if response.status_code == 200:
            doc = response.json()
            doc['archived'] = False
            update_response = requests.put(f"{Patient_DB}/{patient_id}", json=doc, auth=HTTPBasicAuth(username, password))
            
            if update_response.status_code in [200, 201]:
                f"Successfully updated 'archived' field for patient {patient_id}."
            else:
                f"Failed to update 'archived' field for patient {patient_id}: {update_response.status_code} - {update_response.text}"
        else:
            f"Failed to fetch document for patient {patient_id}: {response.status_code} - {response.text}"


restore_test_doc()
delete_original_doc()
clean_up()
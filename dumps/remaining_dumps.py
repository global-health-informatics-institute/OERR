import json
import requests
import logging
from tqdm import tqdm
# choose json file and database
json_file_path = "dumps/patients.json"
db_url = "http://localhost:5984"
db_name = "source_db_patients"
username = "admin"
password = "root"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_database_if_not_exists(db_url, db_name, username=None, password=None):
    url = f"{db_url}/{db_name}"
    auth = (username, password) if username and password else None

    response = requests.get(url, auth=auth)
    
    if response.status_code == 404:
        # Database does not exist, so create it
        response = requests.put(url, auth=auth)
        if response.status_code == 201:
            logging.info(f"Database {db_name} created successfully.")
        else:
            logging.error(f"Failed to create database {db_name}: {response.status_code} \nBecause: {response.text}")
    elif response.status_code == 200:
        logging.info(f"Database {db_name} already exists.")
    else:
        logging.error(f"Failed to check database {db_name}: {response.status_code} \nBecause: {response.text}")

def upload_to_couchdb(json_file_path, db_url, db_name, username=None, password=None):
    # Check and create database if not exists
    create_database_if_not_exists(db_url, db_name, username, password)

    # Load JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Prepare the CouchDB URL
    url = f"{db_url}/{db_name}/_bulk_docs"
    
    # Prepare headers
    headers = {'Content-Type': 'application/json'}
    
    # Prepare authentication if provided
    auth = (username, password) if username and password else None
    
    # Prepare the payload for CouchDB
    payload = {
        "docs": data["docs"]
    }
    
    # Initialize tqdm progress bar
    with tqdm(total=len(payload['docs']), desc="Uploading records to CouchDB", unit="record") as pbar:
        for i in range(0, len(payload['docs']), 100):
            chunk = payload['docs'][i:i+100]
            response = requests.post(url, headers=headers, json={"docs": chunk}, auth=auth)
            
            if response.status_code == 201:
                pbar.update(len(chunk))
            else:
                logging.error(f"Failed to upload chunk to CouchDB: {response.status_code} \nBecause: {response.text}")
                break

if __name__ == "__main__":
    upload_to_couchdb(json_file_path, db_url, db_name, username, password)

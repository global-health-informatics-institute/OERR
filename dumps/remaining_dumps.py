import json
import requests
import logging
json_file_path = "users.json"
db_url = "http://localhost:5984"
db_name = "oerr_users"
username = "admin"
password = "root"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def upload_to_couchdb(json_file_path, db_url, db_name, username=None, password=None):

    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    url = f"{db_url}/{db_name}/_bulk_docs"
    
    headers = {'Content-Type': 'application/json'}
    
    auth = (username, password) if username and password else None
    
    payload = {
        "docs": data["docs"]
    }
    
    response = requests.post(url, headers=headers, json=payload, auth=auth)
    
    if response.status_code == 201:
        logging.info(f"Data successfully uploaded to {db_name} in CouchDB.")
    else:
        logging.error(f"Failed to upload data to CouchDB: {response.status_code} \nBecause: {response.text}")

if __name__ == "__main__":
    upload_to_couchdb(json_file_path, db_url, db_name, username, password)

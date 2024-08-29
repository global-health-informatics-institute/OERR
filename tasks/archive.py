import requests
from requests.auth import HTTPBasicAuth
from config import url, username, password
from datetime import datetime, timedelta

# Set up CouchDB connection details
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
                print(f"Database '{database_name}' created successfully.")
            else:
                print(f"Failed to create database '{database_name}': {create_db_response.status_code} - {create_db_response.text}")
        elif response.status_code == 200:
            print(f"Database '{database_name}' already exists.")
        else:
            print(f"Error connecting to the database '{database_name}': {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while connecting to '{database_name}': {str(e)}")
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
                break  # No more documents to fetch

            last_key = f'"{rows[-1]["id"]}"'  # Prepare the start key for the next batch

        else:
            print(f"Error fetching documents: {response.status_code} - {response.text}")
            break

    return all_documents

# CodeC
def filter_entries():
    documents = fetch_entries()
    if not documents:
        print("No documents found or error fetching documents.")
        return

    active_documents = []
    
    eight_days_ago = datetime.now() - timedelta(days=8)

    for doc in documents:
        date_ordered_timestamp = doc.get('date_ordered')
        if date_ordered_timestamp:
            # Convert the Unix timestamp to a datetime object
            date_ordered = datetime.fromtimestamp(date_ordered_timestamp)

            if date_ordered > eight_days_ago:
                active_documents.append(doc)

    return active_documents

# CodeD
def save_active_entries():
    # Fetch cleaned documents
    active_documents = filter_entries()
    if not active_documents:
        print("No active documents to save.")
        return

    # Database where the cleaned documents will be saved
    active_db = f"{DB_BASE}oerr_active"
    
    # Ensure the 'oerr_active' database exists
    if not ensure_database_exists("active"):
        print("Failed to ensure 'oerr_active' database exists.")
        return
    
    for doc in active_documents:
        # Remove '_rev' to clean up the document before saving
        if '_rev' in doc:
            del doc['_rev']
        
        # Document save URL (CouchDB uses the PUT method to save documents by ID)
        doc_id = doc.get('_id')
        if not doc_id:
            print(f"Document without '_id' found: {doc}")
            continue

        save_url = f"{active_db}/{doc_id}"

        try:
            # Save the document to the oerr_active database
            response = requests.put(save_url, json=doc, auth=HTTPBasicAuth(username, password))

            if response.status_code in [200, 201]:
                print(f"Document '{doc_id}' saved successfully.")
            else:
                print(f"Failed to save document '{doc_id}': {response.status_code} - {response.text}")
        
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while saving document '{doc_id}': {str(e)}")


# codeE
def house_keeping_please(db_name):
    drop_db_url = f"{DB_BASE}{db_name}"

    try:
        response = requests.delete(drop_db_url, auth=HTTPBasicAuth(username, password))

        if response.status_code == 200:
            print(f"Database {db_name} deleted successfully.")
        elif response.status_code == 404:
            print(f"Database {db_name} not found.")
        else:
            print(f"Failed to delete database {db_name}: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error occurred while deleting the {db_name} database: {str(e)}")
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
            print(f"Error fetching documents from 'oerr_active': {response.status_code} - {response.text}")
            break

        data = response.json()
        rows = data.get('rows', [])
        if not rows:
            break  # No more documents to process

        for row in rows:
            doc = row.get('doc')
            if not doc:
                continue

            # Remove the '_rev' field to clean the document
            if '_rev' in doc:
                del doc['_rev']

            # Save the cleaned document to the 'oerr' database
            doc_id = doc.get('_id')
            if not doc_id:
                print(f"Document without '_id' found: {doc}")
                continue

            save_url = f"{target_db}/{doc_id}"

            try:
                save_response = requests.put(save_url, json=doc, auth=HTTPBasicAuth(username, password))

                if save_response.status_code not in [200, 201]:
                    print(f"Failed to save document '{doc_id}' to 'oerr': {save_response.status_code} - {save_response.text}")
            
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while saving document '{doc_id}' to 'oerr': {str(e)}")

        # Update the last key for the next batch
        last_key = f'"{rows[-1]["id"]}"'

        # If less than a full batch was returned, we are done
        if len(rows) < batch_size:
            break

if __name__ == "__main__":
    initialize_setup()
    save_active_entries()
    house_keeping_please("oerr")
    ensure_database_exists("oerr")  # so it has nothing but a clean start
    exodus()
    house_keeping_please("oerr_active")

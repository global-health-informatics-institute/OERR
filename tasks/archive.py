import requests
from requests.auth import HTTPBasicAuth
from config import url, username, password
from datetime import datetime, timedelta
# Set up CouchDB connection details
DB_BASE = f"{url}/"
DB = f"{url}/oerr"

# CodeA_Helper
def ensure_database_exists(database_name):
    # Prefix all databases with 'oerr_' except for 'oerr' itself
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
    db_list = ["oerr", "replica", "archived", "pending"]
    for db in db_list:
        ensure_database_exists(db)


# CodeB
def fetch_entries():
    all_docs_url = f"{DB}/_all_docs?include_docs=true"
    response = requests.get(all_docs_url, auth=HTTPBasicAuth(username, password))
    if response.status_code == 200:
        data = response.json()
        documents = [row['doc'] for row in data['rows']]
        # print(documents)
        return documents
    else:
        print(f"Error fetching documents: {response.status_code} - {response.text}")
        return []


# codeC
def sort_entries():
    documents = fetch_entries()
    if not documents:
        print("No documents found or error fetching documents.")
        return

    archive_documents = []
    replica_documents = []
    
    eight_days_ago = datetime.now() - timedelta(days=8)

    for doc in documents:
        date_ordered_timestamp = doc.get('date_ordered')
        if date_ordered_timestamp:
            # Convert the Unix timestamp to a datetime object
            date_ordered = datetime.fromtimestamp(date_ordered_timestamp)

            if date_ordered < eight_days_ago:
                archive_documents.append(doc)
            else:
                replica_documents.append(doc)

    print("Documents to be archived:", archive_documents)
    print("Documents to be replicated:", replica_documents)

    return archive_documents, replica_documents


if __name__ == "__main__":
    initialize_setup()
    sort_entries()



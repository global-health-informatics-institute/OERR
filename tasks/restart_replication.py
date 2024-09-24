import json
import requests
import time
import logging

# Logging
restart_log = "logs/replication_restarts.log"
logging.basicConfig(filename=restart_log, level=logging.INFO,
                    format='%(asctime)s %(message)s')

application_file = "config/application.config"
with open(application_file) as json_file:
    application_settings = json.load(json_file)

url = f"http://{application_settings['couch']['host']}:{application_settings['couch']['port']}"
DB = f"{url}/{application_settings['couch']['database']}"
username = f"{application_settings['couch']['user']}"
password = f"{application_settings['couch']['passwd']}"
database = f"{application_settings['couch']['database']}"

COUCHDB_URL = url
REPLICATOR_DB = f"{COUCHDB_URL}/_replicator"


auth = (username, password)

def fetch_replicator_docs():
    """Fetch all documents from the _replicator database with authentication."""
    replicator_url = f"{REPLICATOR_DB}/_all_docs?include_docs=true"
    response = requests.get(replicator_url, auth=auth)
    
    if response.status_code == 200:
        replicator_docs = response.json()
        # Return the list of documents
        return {doc['id']: doc['doc'] for doc in replicator_docs.get('rows', [])}
    else:
        logging.error(f"Failed to fetch replicator docs. Response: {response.json()}")
        return {}

def fetch_active_tasks():
    """Fetch all active tasks from the _active_tasks endpoint with authentication."""
    tasks_url = f"{COUCHDB_URL}/_active_tasks"
    response = requests.get(tasks_url, auth=auth)
    
    if response.status_code == 200:
        tasks = response.json()
        # Filter out only replication tasks
        active_replications = [task for task in tasks if task.get('type') == 'replication']
        return active_replications
    else:
        logging.error(f"Failed to fetch active tasks. Response: {response.json()}")
        return []


def restart_replication(doc):
    """Restart the replication by deleting and recreating the document while keeping the same _id."""
    replication_id = doc['_id']
    

    delete_url = f"{REPLICATOR_DB}/{replication_id}?rev={doc['_rev']}"
    delete_response = requests.delete(delete_url, auth=auth)
    
    if delete_response.status_code == 200:
        logging.info(f"Deleted replication task {replication_id}. Now restarting...")


        doc.pop('_rev', None)
        

        create_url = f"{REPLICATOR_DB}/{replication_id}"
        create_response = requests.put(create_url, json=doc, auth=auth)
        
        if create_response.status_code == 201:
            logging.info(f"Replication {replication_id} restarted successfully.")
        else:
            logging.error(f"Failed to restart replication {replication_id}. Response: {create_response.json()}")
    else:
        logging.error(f"Failed to delete replication {replication_id}. Response: {delete_response.json()}")


def check_replication():
    """Check the status of all replication tasks and restart if inactive."""


    replicator_docs = fetch_replicator_docs()
    

    active_tasks = fetch_active_tasks()

    
    active_doc_ids = {task['doc_id'] for task in active_tasks}

    for doc_id, doc in replicator_docs.items():
        if doc_id not in active_doc_ids:
            logging.info(f"Replication task with doc_id {doc_id} is not active. Restarting...")
            restart_replication(doc)


check_replication()

import json
from couchdb import Server
import requests

# Load the configuration files
replications_file = "config/replications.config"
config_file = "config/application.config"

# Read the CouchDB settings from the config file
with open(config_file) as json_file:
    settings = json.load(json_file)

# Connect to the CouchDB server
couchConnection = Server("http://%s:%s@%s:%s/" %
                         (settings["couch"]["user"], settings["couch"]["passwd"],
                          settings["couch"]["host"], settings["couch"]["port"]))

# Define the replicator URL
replicator_url = "http://%s:%s@%s:%s/_replicator" % (
    settings["couch"]["user"], settings["couch"]["passwd"],
    settings["couch"]["host"], settings["couch"]["port"])

# Read the replication URLs from the file
with open(replications_file, "r") as replications:
    db_urls = [url.strip() for url in replications]

# List of subdirectories to be included in the replication
sub_directories = ["", "_lab_test_panels", "_lab_test_type", "_patients", "_users"]

# Function to check if a replication document already exists
def replication_exists(source_db, target_db):
    query = {
        "selector": {
            "source": source_db,
            "target": target_db
        }
    }
    response = requests.post(f"{replicator_url}/_find", json=query)
    result = response.json()
    return len(result['docs']) > 0

# Loop through each pair of databases and subdirectories and set up bidirectional replication
for i in range(len(db_urls)):
    for j in range(len(db_urls)):
        if i != j:
            for sub_dir in sub_directories:
                source_db = db_urls[i] + sub_dir
                target_db = db_urls[j] + sub_dir

                # Check if the first replication already exists: source -> target
                if not replication_exists(source_db, target_db):
                    replication_doc_1 = {
                        "source": source_db,
                        "target": target_db,
                        "create_target": True,
                        "continuous": True
                    }
                    response_1 = requests.post(
                        replicator_url,
                        json=replication_doc_1,
                        headers={"Content-Type": "application/json"}
                    )
                    print(f"Replication from {source_db} to {target_db}: {response_1.json()}")
                else:
                    print(f"Replication from {source_db} to {target_db} already exists.")

                # Check if the second replication already exists: target -> source
                if not replication_exists(target_db, source_db):
                    replication_doc_2 = {
                        "source": target_db,
                        "target": source_db,
                        "create_target": True,
                        "continuous": True
                    }
                    response_2 = requests.post(
                        replicator_url,
                        json=replication_doc_2,
                        headers={"Content-Type": "application/json"}
                    )
                    print(f"Replication from {target_db} to {source_db}: {response_2.json()}")
                else:
                    print(f"Replication from {target_db} to {source_db} already exists.")

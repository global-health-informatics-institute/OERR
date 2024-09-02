import json
from couchdb import Server
import os

# Load the replication configuration
replications_file = "config/replications.config"
config_file = "config/application.config"

with open(replications_file) as json_file:
    replication_settings = json.load(json_file)

# Load application settings
with open(config_file) as json_file:
    settings = json.load(json_file)

# Create source and target connection strings
source_url = "http://%s:%s@%s:%s/oerr" % (
    replication_settings["source"]["user"],
    replication_settings["source"]["passwd"],
    replication_settings["source"]["host"],
    replication_settings["source"]["port"]
)

target_url = "http://%s:%s@%s:%s/oerr" % (
    replication_settings["target"]["user"],
    replication_settings["target"]["password"],
    replication_settings["target"]["host"],
    replication_settings["target"]["port"]
)

replicator_db_url = "http://%s:%s@%s:%s/_replicator" % (
    replication_settings["source"]["user"],
    replication_settings["source"]["passwd"],
    replication_settings["source"]["host"],
    replication_settings["source"]["port"]
)

sub_directories = ["", "_lab_test_panels", "_lab_test_type", "_patients", "_users"]

# Ensure the _replicator database exists (no need to delete/recreate each time)
os.system('curl -X PUT %s' % replicator_db_url)

for sub_dir in sub_directories:
    # Replicate from source to target (master)
    source_to_target = 'curl -d \'{"source":"%s", "target":"%s", "create_target":true, "continuous":true}\' -H "Content-Type: application/json" -X POST %s' % (
        source_url.strip() + sub_dir,
        target_url.strip() + sub_dir,
        replicator_db_url
    )
    
    # Replicate from target (master) to source
    target_to_source = 'curl -d \'{"source":"%s", "target":"%s", "create_target":true, "continuous":true}\' -H "Content-Type: application/json" -X POST %s' % (
        target_url.strip() + sub_dir,
        source_url.strip() + sub_dir,
        replicator_db_url
    )

    # Execute the replication commands
    os.system(source_to_target)
    os.system(target_to_source)

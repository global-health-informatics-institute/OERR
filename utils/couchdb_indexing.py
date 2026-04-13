from typing import Any

from models.database import DataAccess
from utils.misc import initialize_replication_settings

# this resolves conflicts but ensuring each node has a unique ddoc name for the same index.
# preventing multiple candidates is also handled by "filtered replication"
# which only replicates documents relevant to the node, thus reducing the chances of conflicts
NODE_ID = "".join(char for char in (initialize_replication_settings()["source"]["host"]) if char.isalnum())

index_names = [
    'idx_by_status',
    'idx_by_patient_id',
    'idx_by_ward_and_status',
    'idx_by_ordered_by_and_status'
]

index_definitions = {
    'idx_by_status': {
        "ddoc": f"_design/idx_{NODE_ID}_status",
        "index": {
            "fields": ["status"]
        },
        "name": "idx_by_status",
        "type": "json"
    },
    'idx_by_patient_id': {
        "ddoc": f"_design/idx_{NODE_ID}_patient_id",
        "index": {
            "fields": ["patient_id"]
        },
        "name": "idx_by_patient_id",
        "type": "json"
    },
    'idx_by_ward_and_status': {
        "ddoc": f"_design/idx_{NODE_ID}_ward_and_status",
        "index": {
            "fields": ["ward", "status"]
        },
        "name": "idx_by_ward_and_status",
        "type": "json"
    },
    'idx_by_ordered_by_and_status': {
        "ddoc": f"_design/idx_{NODE_ID}_ordered_by_and_status",
        "index": {
            "fields": ["ordered_by", "status"]
        },
        "name": "idx_by_ordered_by_and_status",
        "type": "json"
    }
}


class Couchdb_Indexing:
    """
    Fire and forget class to manage CouchDB indexing for the application.
    On initialization, it checks for the existence of required indexes and creates them if they don't exist.
    run by just instantiating Couchdb_Indexing(). i.e It will be ran on /login route before any operations begin
    """
    def __init__(self, database_name=None):
        if(database_name):
            self.database = DataAccess(database_name).db
        else:
            self.database = DataAccess().db
        
        self._run_indexing()


    def check_if_index_exists(self, index_name):
        if index_name in index_definitions:
            definition = index_definitions[index_name]
            try:
                indexes = self.database.index()
                for idx in indexes:
                    if idx['name'] == definition['name']:
                        return True
                return False
            except Exception as e:
                print(f"Error checking index existence: {e}")
                return False


    def create_index(self, index_name):
        if index_name in index_definitions:
            definition = index_definitions[index_name]
            
            # The "Trick": Use the library's internal resource handler
            # It already has the base URL and Auth context
            resource = self.database.resource
            
            # We target the '_index' endpoint relative to the database root
            try:
                status, headers, buffer = resource.post('_index', body={
                    "ddoc": definition["ddoc"],
                    "index": definition["index"],
                    "name": definition["name"],
                    "type": "json"
                })
                
                if status == 200 or status == 201:
                    print(f"Successfully created: {index_name}")
                else:
                    print(f"Failed: {status}")
            except Exception as e:
                print(f"Error during index creation: {e}")


    def _run_indexing(self):
        for index_name in index_names:
            if not self.check_if_index_exists(index_name):
                print(f"Creating index: {index_name}")
                self.create_index(index_name)
            else:
                print(f"Index already exists: {index_name}")
    

    


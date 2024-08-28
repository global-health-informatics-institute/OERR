import couchdb
from  utils import misc  # Assuming this contains the method to initialize settings

class DataAccess:
    def __init__(self, database=None):
        # Initialize application settings
        self.settings = misc.initialize_settings()

        # Connect to CouchDB
        self.couch_connection = couchdb.Server(f"http://{self.settings['couch']['user']}:{self.settings['couch']['passwd']}@{self.settings['couch']['host']}:{self.settings['couch']['port']}")

        # Determine the database name (main database or a specific one)
        self.db_name = self.settings["couch"]["database"] if database is None else f"{self.settings['couch']['database']}_{database}"

        # Attempt to connect to the specified database
        if self.db_name in self.couch_connection:
            self.db = self.couch_connection[self.db_name]
        else:
            self.db = self.couch_connection.create(self.db_name)
            print(f"Database '{self.db_name}' created.")

def initialize_databases():
    # Initialize the main database and other required databases

    archived_db = DataAccess("archived")    # Archived database
    pending_db = DataAccess("pending")      # Pending database
    replica_db = DataAccess("replica")      # Replica database

    # Output the status of the initialized databases
    print("Databases initialized and ready for use:")
    print(f"Archived database: {archived_db.db_name}")
    print(f"Pending database: {pending_db.db_name}")
    print(f"Replica database: {replica_db.db_name}")

    return archived_db, pending_db, replica_db

if __name__ == '__main__':
    initialize_databases()

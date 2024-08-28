import couchdb
from datetime import datetime, timedelta

# Helper Function: Connect to CouchDB
def connect_to_couchdb(username: str, password: str, url: str) -> couchdb.Server:
    server = couchdb.Server(f'http://{username}:{password}@{url}')
    print(server)
    return server

# Helper Function: Ensure Database Existence
def ensure_database(server: couchdb.Server, db_name: str) -> couchdb.Database:
    if db_name not in server:
        return server.create(db_name)
    return server[db_name]

# 1. CodeA: Database Initialization and Connection Setup
def initialize_databases():
    server = connect_to_couchdb('admin', 'root', 'localhost:5984')
    db_oerr = ensure_database(server, 'oerr')
    db_oerr_archived = ensure_database(server, 'oerr_archived')
    db_oerr_pending = ensure_database(server, 'oerr_pending')
    db_oerr_replica = ensure_database(server, 'oerr_replica')
    
    return db_oerr, db_oerr_archived, db_oerr_pending, db_oerr_replica

# 2. CodeB: Data Retrieval and Identification
def retrieve_and_categorize_records(db_oerr):
    current_time = datetime.now()
    old_records = []
    new_records = []
    
    for doc_id in db_oerr:
        doc = db_oerr[doc_id]
        
        # Ensure the document is of type 'test' to filter relevant records
        if doc.get('type') == 'test':
            date_ordered = datetime.fromtimestamp(doc['date_ordered'])

            
            if (current_time - date_ordered).days > 8:
                old_records.append(doc)
            else:
                new_records.append(doc)
    
    return old_records, new_records

# 3. CodeC: Archiving Old Data
def archive_old_records(db_oerr_archived, db_oerr_pending, old_records):
    for record in old_records:
        try:
            # Archive record if not already present
            if record['_id'] not in db_oerr_archived:
                db_oerr_archived.save(record)
        except couchdb.http.ResourceConflict:
            # Save conflicting record in pending with target 'archive'
            db_oerr_pending.save({**record, 'target': 'archive'})
        except Exception as e:
            print(f"Error archiving record {record['_id']}: {e}")
            db_oerr_pending.save({**record, 'target': 'archive_error'})

# 4. CodeD: Migrate New Records
def migrate_new_records(db_oerr_replica, db_oerr_pending, new_records):
    for record in new_records:
        try:
            # Migrate record if not already present in the replica database
            if record['_id'] not in db_oerr_replica:
                db_oerr_replica.save(record)
        except couchdb.http.ResourceConflict:
            # Save conflicting record in pending with target 'active'
            db_oerr_pending.save({**record, 'target': 'active'})
        except Exception as e:
            print(f"Error migrating record {record['_id']}: {e}")
            db_oerr_pending.save({**record, 'target': 'migration_error'})

# 5. CodeE: Database Cleanup, Replication, and Conflict Resolution
def cleanup_and_replicate(db_oerr, db_oerr_replica, db_oerr_pending, db_oerr_archived):
    server = db_oerr.server
    
    # Drop old oerr database
    try:
        del server['oerr']
    except KeyError:
        print("Database 'oerr' does not exist, skipping deletion.")
    
    # Create new oerr database
    db_oerr_new = server.create('oerr')
    
    # Replicate data from oerr_replica to the new oerr
    for doc_id in db_oerr_replica:
        try:
            db_oerr_new.save(db_oerr_replica[doc_id])
        except couchdb.http.ResourceConflict:
            print(f"Conflict detected for document {doc_id}.")
            # Handle conflict if needed (e.g., keep the most recent, merge, etc.)
    
    # Process the pending records
    for doc_id in db_oerr_pending:
        doc = db_oerr_pending[doc_id]
        try:
            if doc['target'] == 'archive':
                db_oerr_archived.save(doc)
            elif doc['target'] == 'active':
                db_oerr_new.save(doc)
        except Exception as e:
            print(f"Error processing pending record {doc_id}: {e}")

# 6. CodeF: PURGE
def purge_databases(server: couchdb.Server):
    try:
        del server['oerr_replica']
    except KeyError:
        print("Database 'oerr_replica' does not exist, skipping deletion.")
    
    try:
        del server['oerr_pending']
    except KeyError:
        print("Database 'oerr_pending' does not exist, skipping deletion.")

# Main Execution Logic
if __name__ == '__main__':
    # db_oerr, db_oerr_archived, db_oerr_pending, db_oerr_replica = initialize_databases()
    
    # old_records, new_records = retrieve_and_categorize_records(db_oerr)
    
    # print(f"Number of records to archive: {len(old_records)}")
    # print(f"Number of records to keep active: {len(new_records)}")
    
    # archive_old_records(db_oerr_archived, db_oerr_pending, old_records)
    
    # migrate_new_records(db_oerr_replica, db_oerr_pending, new_records)
    
    # cleanup_and_replicate(db_oerr, db_oerr_replica, db_oerr_pending, db_oerr_archived)
    
    # purge_databases(db_oerr.server)

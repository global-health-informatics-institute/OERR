import couchdb
import time

# Connect to CouchDB
def connect_to_couchdb():
    couch = couchdb.Server("http://admin:root@localhost:5984/")
    return couch

# Fetch records from the 'oerr' database
def fetch_records(couch):
    db = couch['oerr']
    # Retrieve all documents with a limit of 9000
    patient_records = []
    for doc_id in db:
        doc = db[doc_id]
        if doc.get("type") == "test":
            patient_records.append(doc)
            if len(patient_records) >= 90000:
                break
    return patient_records

# Identify old and new records
def categorize_records(records, days_threshold= 100000000):
    old_records = []
    new_records = []
    current_time = time.time()

    for record in records:
        if "date_ordered" in record:
            age_in_days = (current_time - record["date_ordered"]) / (24 * 3600)
            if age_in_days > days_threshold:
                old_records.append(record)
            else:
                new_records.append(record)

    return old_records, new_records

if __name__ == '__main__':
    # Step 1: Connect to CouchDB
    couch = connect_to_couchdb()

    # Step 2: Fetch records from 'oerr' database
    print("Fetching records from 'oerr' database...")
    records = fetch_records(couch)

    # Step 3: Categorize records into old and new
    print(f"Processing {len(records)} records...")
    old_records, new_records = categorize_records(records)

    # Output the results
    print(f"Number of records to archive: {len(old_records)}")
    print(f"Number of records to keep active: {len(new_records)}")

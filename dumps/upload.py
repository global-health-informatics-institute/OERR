import couchdb
import json
from tqdm import tqdm

# Connect to CouchDB server
couch = couchdb.Server('http://admin:root@localhost:5984/')
db_name = 'oerr'
file_name = 'tests_dump.json' 


if db_name in couch:
    db = couch[db_name]
else:
    db = couch.create(db_name)

with open(file_name, 'r') as file:
    lines = file.readlines()

# Process each line with a progress bar
for line in tqdm(lines, desc="Uploading documents", unit="doc"):
    doc = json.loads(line)
    doc_id = doc['_id']
    
    # Remove the _rev field if it exists
    if '_rev' in doc:
        del doc['_rev']
    
    try:
        # Check if the document already exists
        if doc_id in db:
            existing_doc = db[doc_id]
            doc['_rev'] = existing_doc.rev  # Set the revision to the current one
        # Save the document (will create if new or update if existing)
        db.save(doc)
    except couchdb.http.ResourceConflict:
        print(f"Conflict detected for document {doc_id}. Skipping.")

print("upload complete.")

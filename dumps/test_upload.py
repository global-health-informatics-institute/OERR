import couchdb
import json
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

couch = couchdb.Server('http://admin:root@localhost:5984/')
db_name = 'oerr'
file_name = 'tests_dump.json' 

if db_name in couch:
    db = couch[db_name]
    logger.info(f"Connected to existing database: {db_name}")
else:
    db = couch.create(db_name)
    logger.info(f"Created new database: {db_name}")

with open(file_name, 'r') as file:
    lines = file.readlines()

for line in tqdm(lines, desc="Uploading documents", unit="doc"):
    doc = json.loads(line)
    doc_id = doc['_id']
    
    if '_rev' in doc:
        del doc['_rev']
    
    try:
        if doc_id in db:
            existing_doc = db[doc_id]
            doc['_rev'] = existing_doc.rev  # Set the revision to the current one
            logger.info(f"Updating existing document with ID: {doc_id}")
        else:
            logger.info(f"Creating new document with ID: {doc_id}")

        db.save(doc)
    except couchdb.http.ResourceConflict:
        logger.warning(f"Conflict detected for document {doc_id}. Skipping.")

logger.info("Upload complete.")

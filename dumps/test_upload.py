import couchdb
import json
import logging
from tqdm import tqdm
import io

# Log buffer
log_buffer = io.StringIO()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(log_buffer)])
logger = logging.getLogger(__name__)

# CouchDB connection
couch = couchdb.Server('http://admin:root@localhost:5984/')
db_name = 'oerr'
file_name = 'tests_dump.json' 
updates = 0
new_docs = 0
conflicts = 0

if db_name in couch:
    db = couch[db_name]
    logger.info(f"Connected to existing database: {db_name}")
else:
    db = couch.create(db_name)
    logger.info(f"Created new database: {db_name}")

with open(file_name, 'r') as file:
    lines = file.readlines()

for line in tqdm(lines, desc="Uploading documents", unit="doc", ncols=80, leave=True):
    doc = json.loads(line)
    doc_id = doc['_id']
    
    if '_rev' in doc:
        del doc['_rev']
    
    try:
        if doc_id in db:
            existing_doc = db[doc_id]
            doc['_rev'] = existing_doc.rev
            updates += 1
        else:
            new_docs += 1

        db.save(doc)
    except couchdb.http.ResourceConflict:
        conflicts += 1

logger.info(f"Documents added: {new_docs}")
logger.info(f"Documents updated: {updates}")
logger.warning(f"Documents skipped: {conflicts}")
logger.info("Upload complete.")


print(log_buffer.getvalue())

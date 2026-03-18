import json
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import logging
from tqdm import tqdm

# CONFIG
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

application_file = "config/application.config"

archive_file = "config/archive.config"

with open(application_file) as json_file:
    application_settings = json.load(json_file)


with open(archive_file) as json_file:
    archive_settings = json.load(json_file)


# URL, TARGETS, PARAMS
USERNAME = f"{application_settings['couch']['user']}"
PASSWORD = f"{application_settings['couch']['passwd']}"
DATABASE = f"{application_settings['couch']['database']}"
HOST = f"{application_settings['couch']['host']}"
PORT = f"{application_settings['couch']['port']}"
URL = f"http://{HOST}:{PORT}"
DB_BASE_URL = f"{URL}/{DATABASE}"


JOB_DB = ["", "_active", "_archive"]

PATIENT_URL = f"{DB_BASE_URL}_patients"


CUT_OFF_DAYS = int(archive_settings.get("cut_off_days", 8)) 
cut_off_date = datetime.now() - timedelta(days=CUT_OFF_DAYS)
CUT_OFF_DATE = int(cut_off_date.timestamp())

DELETE_ARCHIVE = archive_settings.get("delete_archive", False)

# CREATE DB IF NOT EXIST
def _helper_create_db(database_name):
    create_request = requests.put(f"{DB_BASE_URL}{database_name}", auth=HTTPBasicAuth(USERNAME, PASSWORD))
    return create_request.status_code

def _helper_check_db_if_exist(database_name):
    check_request = requests.head(f"{DB_BASE_URL}{database_name}", auth=HTTPBasicAuth(USERNAME, PASSWORD))
    return check_request.status_code

def create_db_if_not_exist():
    try:
        for db in JOB_DB:
            if _helper_check_db_if_exist(db) == 404:
                logging.info(f"Database does not exist: {db}")
                if _helper_create_db(db) == 201:
                    logging.info(f"Database created: {db}")
                else:
                    logging.error(f"Error creating db: {db}")
            else:
                logging.info(f"Database already exists: {db}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error: (check db if exist) - {e}")

# LOAD ENTRIES
def _helper_request_docs(batch_url):
    get_docs_request = requests.get(batch_url, auth=HTTPBasicAuth(username=USERNAME, password=PASSWORD))
    return get_docs_request.status_code, get_docs_request.json() if get_docs_request.status_code == 200 else None

def _helper_unpack_docs(data, batch_size):
    rows = data.get('rows', [])
    documents = [row['doc'] for row in rows]

    if len(rows) < batch_size:
        return documents, None

    return documents, f'"{rows[-1]["id"]}"'  # second value is last key


def load_entries(batch_size=9000):
    batch_url = f"{DB_BASE_URL}/_all_docs?include_docs=true&limit={batch_size}"
    last_key = None
    all_docs = []

    try:
        while True:
            url = batch_url
            if last_key:
                url += f"&startkey={last_key}&skip=1"

            status_code, data = _helper_request_docs(batch_url=url)

            if status_code != 200 or not data:
                break

            docs, last_key = _helper_unpack_docs(data, batch_size)
            all_docs.extend(docs)

            if not last_key:
                break

    except Exception as e:
        logging.error(f"Error: (loading entries) - {e}")
        return []

    return all_docs

# FILTER ENTRIES
"""
returns an array of active docs, archive docs and archived docs patient owner
active_docs, archive_docs, patient_id
"""

def _helper_get_patient_id(document):
    patient_id = document.get('patient_id')
    return patient_id or None


def filter_entries(all_entries):
    if not all_entries:
        logging.warning("Warning: No documents found")
        return [], [], []

    active_entries = []
    archive_entries = []
    patient_ids = []

    for entry in tqdm(all_entries, desc="filtering + sorting"):
        date_ordered = entry.get('date_ordered')
        if date_ordered:
            if date_ordered > CUT_OFF_DATE:
                active_entries.append(entry)
            else:
                archive_entries.append(entry)
                patient_id = _helper_get_patient_id(entry)
                if patient_id:
                    patient_ids.append(patient_id)
    if patient_ids:
        patient_ids = list(set(patient_ids))

    return active_entries, archive_entries, patient_ids


# MARK PATIENTS
def _get_patient_doc(patient_id):
    response = requests.get(
        url=f"{PATIENT_URL}/{patient_id}",
        auth=HTTPBasicAuth(username=USERNAME, password=PASSWORD),
    )
    if response.status_code == 200:
        raw_doc = response.json()
        raw_doc["archived"] = True
        return raw_doc
    return None


def _patch_request(patient_id):
    patient_doc = _get_patient_doc(patient_id=patient_id)
    if patient_doc:
        patch_patient_request = requests.put(
            url=f"{PATIENT_URL}/{patient_id}",
            auth=HTTPBasicAuth(username=USERNAME, password=PASSWORD),
            json=patient_doc
        )
        # ADD THIS LOGGING TO SEE THE ERROR
        if patch_patient_request.status_code not in [200, 201, 204]:
            logging.error(f"Failed to update {patient_id}: {patch_patient_request.status_code} - {patch_patient_request.text}")
            
        return patch_patient_request.status_code
    return 424


def mark_patients_as_archived(patient_ids):
    succes_count = 0
    fail_patches = []
    for patient_id in tqdm(patient_ids, desc="marking patients"):
        if patient_id:
            # ADD 201 HERE - CouchDB returns 201 for successful PUT updates
            if _patch_request(patient_id) in [200, 201, 204]:
                succes_count += 1
            else:
                fail_patches.append(patient_id)
    
    logging.info(f"successful patched patient docs - {succes_count}")
    if fail_patches:
        logging.warning(f"failed patched patient docs - {len(fail_patches)}")
        logging.warning(f"patient ids: {fail_patches}")



# TEMPORARY MIGRATIONS
def _helper_pop_revision(doc):
    doc.pop("_rev", None) 
    return doc

def _helper_convert_array_to_object(batch):
    return { "docs": batch }

def _helper_bulk_post(batch, database):
    put_batch_request = requests.post(
        url=f"{DB_BASE_URL}{database}/_bulk_docs",
        auth=HTTPBasicAuth(username=USERNAME, password=PASSWORD),
        json=_helper_convert_array_to_object(batch=batch)
    )
    return put_batch_request.status_code

def run_migration(data, database):
    tmp_array = []
    for doc in data:
        tmp_array.append(_helper_pop_revision(doc))
    if _helper_bulk_post(batch=tmp_array, database=database) in [200, 201]:
        logging.info(f"migrated data - {database} - {len(data)}")
    else:
        logging.info(f"migration fail - {database} - {len(data)}")

# DELETE DB
def delete_db(database):
    if database == "_replicator":
        url = f"{URL}/{database}"
    else:
        url=f"{DB_BASE_URL}{database}"
    delete_db_request = requests.delete(
        url=url,
        auth=HTTPBasicAuth(username=USERNAME, password=PASSWORD)
    )
    status_code = delete_db_request.status_code
    if status_code in [200, 202]:
        logging.info(f"database deleted sucessfully - {(database or 'primary')} - {status_code}")
    else:
        logging.info(f"database delete fail - {(database or 'primary')} - {status_code}")
    return status_code



delete_db(database="_replicator")

create_db_if_not_exist()

all_entries = load_entries()

active_entries, archive_entries, patient_ids = filter_entries(all_entries)

if active_entries:
    run_migration(data=active_entries, database='_active')

if archive_entries:
    mark_patients_as_archived(patient_ids=patient_ids)
    run_migration(data=archive_entries, database='_archive')

delete_db(database="")

create_db_if_not_exist()

run_migration(data=active_entries, database="")

delete_db(database="_active")

if DELETE_ARCHIVE:
    delete_db(database="_archive")
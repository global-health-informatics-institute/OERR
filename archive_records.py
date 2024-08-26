import json
import subprocess
import datetime
import requests

from utils import misc
from couchdb import Server
from models.patient import Patient
from models.database import DataAccess
settings = misc.initialize_settings()
def initialize_connection():
    global main_db
    global db
    global replica_db

    couch_connection = Server("http://%s:%s@%s:%s/" %
                              (settings["couch"]["user"], settings["couch"]["passwd"],
                               settings["couch"]["host"], settings["couch"]["port"]))

# delete_command = [
#     "curl",
#     "-X", "DELETE",
#     f"http://{settings['couch']['host']}:{settings['couch']['port']}/{settings['couch']['database']}",
#     "-u", f"{settings['couch']['user']}:{settings['couch']['passwd']}"
# ]http://localhost:5984/_replicate
#http://localhost:5984/_replicate
# # Execute the curl command
# subprocess.run(delete_command)

url = ('http://localhost:5984/_utils/#database/_replicator')
data = '{"source": "http://localhost:5984/mss_results_new_records","target":"http://localhost:5984/mss_results_new"}'
headers = {'content-type':'application/json'}
auth = (settings['couch']['user'], settings['couch']['passwd'])
response = requests.post(url, data=data, headers=headers, auth=auth)


#
#
# def initiate_archiving():
#     print("Beginning archiving records")
#     patient_ids = DataAccess("patients").db.find({"selector": {"_id": {"$gt": None}}, "fields": ["_id"], "limit": 10000})
#
#     for row in patient_ids:
#         archive_record, archive_new_record = check_recent_test(row["_id"])
#         if archive_record:
#             archive_patient(row["_id"])
#             archive_records(archive_record, "older")
#         if archive_new_record:
#             archive_records(archive_new_record, "newer")
#
#             # # get all patient ids
#             # for row in patient_ids:
#             #     docs = check_recent_test(row["_id"])
#             #     if not docs == []:
#             #         archive_patient(row["_id"])
#             #         archive_records(docs)
#
#
# def archive_patient(patient_id):
#     patient = DataAccess("patients").db.get(patient_id)
#     pt_record = Patient(patient["_id"], patient["name"], patient["dob"], patient["gender"], True, patient["_rev"])
#     pt_record.save()
#
#
# def archive_records(records, new_record_type):
#     backup_name = f"{new_record_type}_records_archive.json"
#     with open(backup_name, "a") as file1:
#         for record in records:
#             file1.write(json.dumps(record) + '\n')
#
#     DataAccess().db.purge(records)
#
#
# def check_recent_test(patient_id):
#     test_records = DataAccess().db.find({"selector": {"patient_id": patient_id}, "limit": 2000})
#     current_time = (datetime.datetime.now() - datetime.timedelta(days=8)).strftime('%s')
#     print(current_time)
#
#     archive_record = []
#     archive_new_record = []
#     for record in test_records:
#         if float(record["date_ordered"]) >= float(current_time):
#             archive_record.append(record)
#         else:
#             archive_new_record.append(record)
#
#     return archive_record, archive_new_record
#
#
# if __name__ == '__main__':
#     initiate_archiving()

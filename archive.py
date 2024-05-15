import subprocess
import datetime
from utils import misc
from couchdb import Server
from models.patient import Patient
from models.database import DataAccess

settings = misc.initialize_settings()


# Initialize global variables
main_db = None
db = None
replica_db = None
def initialize_connection():
    global main_db
    global db
    global replica_db

    couch_connection = Server("http://%s:%s@%s:%s/" %
                              (settings["couch"]["user"], settings["couch"]["passwd"],
                               settings["couch"]["host"], settings["couch"]["port"]))

    db_name = settings["couch"]["database"]
    dbmsave_name = db_name + "_archived_records"
    replica_name = db_name + "_records"

    if dbmsave_name in couch_connection:
        db = couch_connection[dbmsave_name]
    else:
        db = couch_connection.create(dbmsave_name)

    if replica_name in couch_connection:
        replica_db = couch_connection[replica_name]
    else:
        replica_db = couch_connection.create(replica_name)


def initiate_archiving():
    initialize_connection()

    print("Beginning archiving records")
    patient_ids = DataAccess("patients").db.find({"selector": {"_id": {"$gt": None}}, "fields": ["_id"], "limit": 9000})

    # get all patient ids
    for row in patient_ids:
        test_records = list(DataAccess().db.find({"selector": {"patient_id": row["_id"]}, "limit": 9000}))
        if len(test_records) > 0:
            archive_record = check_recent_test(test_records)

            if archive_record:
                archive_records(test_records),
            else:
                recent_records(test_records)
                # main_db.delete("doc")

    delete_command = [
        "curl",
        "-X", "DELETE",
        f"http://{settings['couch']['host']}:{settings['couch']['port']}/{settings['couch']['database']}",
        "-u", f"{settings['couch']['user']}:{settings['couch']['passwd']}"
    ]

    subprocess.run(delete_command)


def archive_records(records):
    for record in records:
        archived_tests = {}

        for i in record.keys():
            if i != "_id":
                archived_tests[i] = record[i]
                db.save(archived_tests)

                # main_db.delete()

def recent_records(records):
    for record in records:
        newer_records = {}
        for i in record.keys():
            if i == "_id":
                newer_records[i] = record[i]
                replica_db.save(newer_records)


def check_recent_test(records):
    current_time = (datetime.datetime.now() - datetime.timedelta(days=8)).strftime('%s')
    for i in records:
        if float(i["date_ordered"]) >= float(current_time):
            return False
    return True


if __name__ == '__main__':
    initiate_archiving()

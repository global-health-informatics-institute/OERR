import datetime
from utils import misc
from couchdb import Server
from models.patient import Patient
from models.database import DataAccess

global db
global main_db

settings = misc.initialize_settings()


def initiate_archiving():
    initialize_connection()
    print("Beginning archiving records")
    patient_ids = DataAccess("patients").db.find({"selector": {"_id": {"$gt": None}}, "fields": ["_id"], "limit": 9000})

    # get all patient ids
    for row in patient_ids:
        test_records = list(DataAccess().db.find({"selector": {"patient_id": row["_id"]}, "limit": 9000}))
        if len(test_records) > 0:
            # Check patient record for last test
            archive_record = check_recent_test(test_records)

            if archive_record:
                archive_records(test_records)


def archive_records(records):
    for record in records:
        archived_record = {}
        for i in record.keys():
            if i != "_id":
                archived_record[i] = record[i]
        db.save(archived_record)
        main_db.delete(record)
        #DataAccess().db.delete(record.get("_id"))


def initialize_connection():
    # Connect to a couchdb instance
    couch_connection = Server("http://%s:%s@%s:%s/" %
                              (settings["couch"]["user"], settings["couch"]["passwd"],
                               settings["couch"]["host"], settings["couch"]["port"]))

    global main_db
    global db
    # Connect to a database or Create a Database
    try:
        db = couch_connection[settings["couch"]["database"] + "_archived_test"]
        main_db = couch_connection[settings["couch"]["database"]]

    except:
        db = couch_connection.create(settings["couch"]["database"] + "_archived_test")
        main_db = couch_connection[settings["couch"]["database"]]


def check_recent_test(records):
    current_time = (datetime.datetime.now() - datetime.timedelta(days=90)).strftime('%s')

    for i in records:
        if float(i["date_ordered"]) >= float(current_time):
            return False
    return True


if __name__ == '__main__':
    initiate_archiving()

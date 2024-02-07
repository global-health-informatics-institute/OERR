import json
import datetime
from models.patient import Patient
from models.database import DataAccess


def initiate_archiving():
    print("Beginning archiving records")
    patient_ids = DataAccess("patients").db.find({"selector": {"_id": {"$gt": None}}, "fields": ["_id"], "limit": 10000})

    # get all patient ids
    for row in patient_ids:
        docs = check_recent_test(row["_id"])
        if not docs == []:
            archive_patient(row["_id"])
            archive_records(docs)


def archive_patient(patient_id):
    patient = DataAccess("patients").db.get(patient_id)
    pt_record = Patient(patient["_id"], patient["name"], patient["dob"], patient["gender"], True, patient["_rev"])
    pt_record.save()


def archive_records(records):
    backup_name = "records_archive.json"
    file1 = open(backup_name, "a")

    for record in records:
        file1.write(json.dumps(record))

    file1.close()
    DataAccess().db.purge(records)


def check_recent_test(patient_id):
    test_records = DataAccess().db.find({"selector": {"patient_id": "%s" % patient_id}, "limit": 2000})
    current_time = (datetime.datetime.now() - datetime.timedelta(days=1460)).strftime('%s')

    archive_record = []
    for record in test_records:

        if float(record["date_ordered"]) >= float(current_time):
            return []
        else:
            archive_record.append(record)

    return archive_record


if __name__ == '__main__':
    initiate_archiving()

import json

"""
BASE_URL, auth_payload, VALID_USER and VALID_PASSWORD have been set to empty strings for security reasons.
Please replace the empty strings with the correct values before running the script.
"""
BASE_URL = ""
LOGIN_ENDPOINT = ""
auth_payload = {
    "username": "administrator",
    "password": "kchlims"
}
REFRESH_ENDPOINT = "/api/v1/auth/refresh_token"
TEST_TYPE_ENDPOINT = "/api/v1/test_types/"
TEST_PANEL_ENDPOINT = "/api/v1/test_panels/"
WARD_ENDPOINT = "/api/v1/facility_sections"
DEPARTMENT_ENDPOINT = "/api/v1/departments"
SPECIMEN_ENDPOINT = "/api/v1/specimen"
SYNC_RESPONSE_ENDPOINT = "/api/v1/sync"

VALID_USER = ""
VALID_PASSWORD = ""


# Load Configurations
config_file = "config/application.config"

settings = {}
with open(config_file) as json_file:
    settings = json.load(json_file)
couch_config = settings.get("couch", {})

FACILITY_SECTIONS =  {
    "UNDER 5": "27",
    "CWA": "7",
    "CWB": "3",
    "CWC": "1",
    "CW HDU": "2",

    "OPD2": "4",
    "MSS": "44",
    "4A": "19",
    "4B": "20",
    "MHDU": "56",
    "DIALYSIS UNIT": "10",


    "CASUALTY": "34",
    "1A": "12",
    "1B": "13",
    "3A": "17",
    "3B": "18",
    "SHDU": "57",
    "THEATRE": "9",


    "LABOUR": "36",
    "POSTNATAL WARD":"42",
    "ANTENATAL WARD": "64",
    "EM OPD": "35",
    "EMHDU" : "37",
    "EM NURSERY": "39",
    "GYNAE": "40",

    "ICU": "11",
    "OPD1": "60",
    "EYE WARD": "59",
    "DENTAL" : "25",
    "ENT": "61" 
}

SPECIMEN_STATUSES = {
  "specimen-not-collected" :"Specimen Received",
  "specimen-accepted" : "Specimen Received",
  "specimen-rejected" : "Rejected"
}

TEST_STATUSES = {
  "pending": "Specimen Received",
  "started": "Being Analyzed",
  "completed": "Pending Verification",
  "verified": "Analysis Complete",
  "voided": "Not Done",
  "not-done": "Not Done",
  "rejected": "Rejected"
}

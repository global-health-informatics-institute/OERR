# this is a a location for all the miscellaneous functions
from datetime import date
import json


# calculate age for display

def calculate_age(birth_date):
    age_in_days = int((date.today() - birth_date).days)

    if age_in_days < 31:
        return str(age_in_days) + " days"
    elif age_in_days < 548:
        years = int(date.today().year - birth_date.year)
        months = int(date.today().month - birth_date.month)
        return str((years * 12) + months) + " months"
    else:
        return str(int(age_in_days / 365.2425)) + " years"


def collapse_test_orders(orders):
    collapsed_orders = []
    tests_by_depts = {}
    for order in orders:
        if order.get("type") == "test panel":
            collapsed_orders.append(order)
        else:
            if tests_by_depts.get(order.get("department")) is None:
                tests_by_depts[order.get("department")] = {order.get("specimen_type"): []}
            try:
                tests_by_depts[order.get("department")][order.get("specimen_type")].append(order)
            finally:
                pass

    for dept in tests_by_depts.keys():
        for specimen_type in tests_by_depts[dept].keys():
            if len(tests_by_depts[dept][specimen_type]) == 1:
                collapsed_orders.append(tests_by_depts[dept][specimen_type][0])
            else:
                collapsed_orders += ([tests_by_depts[dept][specimen_type][i * 3:(i + 1) * 3] for i in
                                      range((len(tests_by_depts[dept][specimen_type]) + 3 - 1) // 3)])

    return collapsed_orders


def initialize_settings():
    settings = {}
    try:
        with open("config/application.config") as json_file:
            settings = json.load(json_file)
    finally:
        pass
    return settings


def current_facility():
    try:
        with open("config/application.config") as json_file:
            settings = json.load(json_file)
            return settings["facility"]
    except:
        return "Undefined"


def container_options():
    return {'Sterile container': "blue_top_urine.png", "Swab": "swab.jpg",
            'Red top': "red_top.jpg", 'Baktech': "bactec.png",
            'Conical container': "conical_contatiner.jpeg",
            'EDTA': 'purple_top.jpg', 'yellow top': "yellow_top.jpg"}


def update_patient(patient_id):
    import json
    import requests
    from requests.auth import HTTPBasicAuth
    with open('config/application.config') as json_file:
        patient_db_settings = json.load(json_file)

    
    db_address = f"http://{patient_db_settings['couch']['host']}:{patient_db_settings['couch']['port']}"
    username = patient_db_settings['couch']['user']
    password = patient_db_settings['couch']['passwd']
    database_name = f"{patient_db_settings['couch']['database']}_patients"


    db_url = f"{db_address}/{database_name}/_find"

    query = {
        "selector": {
            "_id": patient_id
        },
        "limit": 1
    }

    response = requests.post(db_url, json=query, auth=HTTPBasicAuth(username, password))

    if response.status_code == 200:
        docs = response.json()['docs']
        
        for doc in docs:
            if 'archived' in doc and ((doc['archived'] is True) or (doc['archived'] is False)):
                doc['archived'] = 'restored'  

                doc_id = doc['_id']
                doc_rev = doc['_rev']
                update_url = f"{db_address}/{database_name}/{doc_id}"
                
                updated_doc = {
                    **doc,
                    '_rev': doc_rev
                }
                
                update_response = requests.put(update_url, json=updated_doc, auth=HTTPBasicAuth(username, password))

                if update_response.status_code == 201:
                    f"Document {doc_id} updated successfully."
                else:
                    f"Failed to update document {doc_id}: {update_response.status_code} - {update_response.text}"
    else:
        f"Failed to retrieve documents: {response.status_code} - {response.text}"
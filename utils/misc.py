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

def initialize_user_roles():
    user_roles = {}
    try:
        with open("config/user_roles.config") as json_file:
            user_roles = json.load(json_file)
    finally:
        pass
    return user_roles


def initialize_departments():
    departments = {}
    try:
        with open("config/department.config") as json_file:
            departments = json.load(json_file)
    finally:
        pass
    return departments


# Load common histories from config file
def load_common_histories(by_department=False):
    common_histories = []
    grouped_histories = {}

    def normalize_history_entry(entry):
        if isinstance(entry, str):
            value = entry.strip()
            if value:
                return {"id": None, "name": value}
            return None

        if isinstance(entry, dict):
            name = entry.get("name")
            if not isinstance(name, str):
                return None
            name = name.strip()
            if not name:
                return None

            entry_id = entry.get("id")
            if not isinstance(entry_id, (str, int)):
                entry_id = None
            return {"id": entry_id, "name": name}

        return None

    def dedupe_histories(histories):
        deduped = []
        seen_ids = set()
        seen_names = set()

        for history in histories:
            if not isinstance(history, dict):
                continue

            history_name = history.get("name")
            history_id = history.get("id")
            if not history_name:
                continue

            if history_id is not None:
                key = str(history_id)
                if key in seen_ids:
                    continue
                seen_ids.add(key)
            else:
                key = history_name.lower()
                if key in seen_names:
                    continue
                seen_names.add(key)
            deduped.append(history)
        return deduped

    try:
        with open("config/clinical_histories.config") as json_file:
            configured_histories = json.load(json_file)
            if isinstance(configured_histories, list):
                common_histories = [
                    normalized for normalized in (normalize_history_entry(item) for item in configured_histories)
                    if normalized is not None
                ]
                grouped_histories = {}
            elif isinstance(configured_histories, dict):
                for department, histories in configured_histories.items():
                    if isinstance(histories, list):
                        department_histories = [
                            normalized for normalized in (normalize_history_entry(item) for item in histories)
                            if normalized is not None
                        ]
                        grouped_histories[department] = department_histories
                        common_histories.extend(department_histories)
            else:
                common_histories = []
                grouped_histories = {}
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        common_histories = []
        grouped_histories = {}
    finally:
        pass
    if by_department:
        return {
            department: dedupe_histories(histories)
            for department, histories in grouped_histories.items()
        }
    return dedupe_histories(common_histories)


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

def get_teams_units_department_ward(all_departments, ward_selected):
        for department in all_departments["departments"]:
            if ward_selected in department["wards"]:
                if not department.get("teams"):
                    department["teams"] = []
                if not department.get("units"):
                    department["units"] = []
                if not department.get("wards"):
                    department["wards"] = []
                return department["teams"], department["units"], department["name"], department["wards"], ward_selected
        return None, None, None, None, None

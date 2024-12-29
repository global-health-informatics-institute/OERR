import base64
import json
from flask import Blueprint, jsonify, request
from couchdb import Server
from extensions.extension import logger
from apis.extensions_api import (
    FACILITY_SECTIONS, VALID_PASSWORD, VALID_USER,  
    config_file, SPECIMEN_STATUSES, TEST_STATUSES
)

oerr_bp = Blueprint('oerr', __name__)



settings = {}
with open(config_file) as json_file:
    settings = json.load(json_file)



def connect_to_oerr_test():
    try:
        couch_config = settings.get("couch", {})
        user = couch_config.get("user")
        passwd = couch_config.get("passwd")
        host = couch_config.get("host")
        port = couch_config.get("port")
        database = f'{couch_config.get("database")}'

        couch_connection = Server(f"http://{user}:{passwd}@{host}:{port}/")
        global db_oerr_tests
        db_oerr_tests = (
            couch_connection[database] if database in couch_connection 
            else couch_connection.create(database)
        )
        logger.info("Successfully connected to OERR test database.")
    except Exception as e:
        logger.error(f"Error connecting to OERR tests: {str(e)}")
        raise



def authenticate_iblis(auth_header):
    if not auth_header:
        logger.warning("Missing Authorization header.")
        return False
    try:
        encoded_credentials = auth_header.split(" ")[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
        username, password = decoded_credentials.split(":")
        return username == VALID_USER and password == VALID_PASSWORD
    except (IndexError, ValueError, base64.binascii.Error) as e:
        logger.error(f"Error decoding credentials: {e}")
        return False



def find_match(oerr_identifier):
    try:
        doc_id = oerr_identifier.get("_id")
        if doc_id and doc_id in db_oerr_tests:
            return doc_id
        
        if(oerr_identifier.get("is_panel") is True):
            mango_query = {
                "selector": {
                    "patient_id": oerr_identifier.get("patient_id"),
                    "ward": oerr_identifier.get("ward"),
                    "ordered_by": oerr_identifier.get("ordered_by"),
                    "collected_at": oerr_identifier.get("collected_at"),
                },
                "fields": ["_id"],
                "limit": 1
            }
            results = db_oerr_tests.find(mango_query)
            for doc in results:
                return doc["_id"]
            return None


        # Use Mango query
        mango_query = {
            "selector": {
                "patient_id": oerr_identifier.get("patient_id"),
                "ward": oerr_identifier.get("ward"),
                "ordered_by": oerr_identifier.get("ordered_by"),
                "collected_at": oerr_identifier.get("collected_at"),
                "test_type": str(oerr_identifier.get("test_type"))
            },
            "fields": ["_id"],
            "limit": 1
        }
        results = db_oerr_tests.find(mango_query)
        for doc in results:
            return doc["_id"]
        return None
    except Exception as e:
        logger.error(f"Error in finding match: {str(e)}")
        return None



def process_payload(payload):
    def actual_status(specimen_status, test_status):
        return TEST_STATUSES.get(test_status, SPECIMEN_STATUSES.get(specimen_status, "Unknown"))

    def get_order_info():
        return {
            "is_panel": bool(payload.get("test_panel_name")),
            "is_culture": payload.get("test_panel_id") == 4,
            "test_type": payload.get("test_type_id"),
            "test_status": payload.get("status"),
            "specimen_status": payload.get("order_status"),
            "actual_status": actual_status(payload.get("order_status"), payload.get("status"))
        }

    def get_test_results():
        results = []
        for indicator in payload.get("indicators", []):
            result = indicator.get("result", {})
            if "value" not in result:
                continue
            if indicator.get("name") == "Lab Tech. Name:": 
              continue  
            results.append({
                "name": indicator.get("name"),
                "value": result.get("value"),
            })
        return results

    def get_status_info():
        return {"actual_status": actual_status(payload.get("order_status"), payload.get("status"))}

    def get_oerr_identifiers():
        oerr = payload.get("oerr_identifiers", {})

        def map_ward_key(key_value):
            return {v: k for k, v in FACILITY_SECTIONS.items()}.get(str(key_value), "Unknown Ward")
        return {
            "patient_id": oerr.get("npid"),
            "ward": map_ward_key(oerr.get("facility_section_id")),
            "ordered_by": oerr.get("requested_by"),
            "collected_at": oerr.get("sample_collected_at"),
            "_id": oerr.get("doc_id"),
            "test_type": str(oerr.get("test_type_id")),
            "is_panel": oerr.get("is_panel")
        }

    def get_rejection_reason():
        return {"rejection_reason": payload.get("rejection_reason")}


    logger.info(json.dumps(get_test_results(), indent=4))
    logger.info(type(get_test_results()))
    print("\n\n")
    return {
        "order_information": get_order_info(),
        "test_results": get_test_results(),
        "actual_status": get_status_info(),
        "oerr_identifiers": get_oerr_identifiers(),
        "not_done_reason": get_rejection_reason()
    }

# Update document
def update_doc(order_information, test_results, actual_status, oerr_identifiers, not_done_reason):
    def update_parent_status(current_status, new_status):
        status_hierarchy = [
            "Specimen Received", "Being Analyzed", "Pending Verification", 
            "Analysis Complete", "Not Done", "Rejected"
        ]
        try:
            current_index = status_hierarchy.index(current_status) if current_status in status_hierarchy else -1
            new_index = status_hierarchy.index(new_status) if new_status in status_hierarchy else -1
            return new_status if new_index > current_index else current_status
        except ValueError:
            logger.warning("Status provided is not recognized in hierarchy.")
            return current_status

    try:
        _id = oerr_identifiers.get("_id") or find_match(oerr_identifiers)
        if not _id:
            logger.error("No matching document found.")
            return False

        doc = db_oerr_tests.get(_id)
        if not doc:
            logger.error(f"Document with ID {_id} not found in database.")
            return False

        is_panel = order_information.get("is_panel", False)
        is_culture = order_information.get("is_culture", False)

        if is_panel:
            test_type_key = str(oerr_identifiers.get("test_type"))  
            doc["status"] = update_parent_status(doc.get("status", "Ordered"), actual_status.get("actual_status"))
            


            # Ensure the test entry exists in the panel
            test_entry = doc.setdefault("tests", {}).setdefault(test_type_key, {})
            
            # Update status for the specific test
            test_entry["status"] = actual_status.get("actual_status")
            
            # Update measures for the test
            test_entry.setdefault("measures", {}).update(
                {result["name"]: result["value"] for result in test_results if "name" in result and "value" in result}
            )
            logger.debug(f"Updated measures for test type {test_type_key}: {test_entry['measures']}")
            (f"Test Results: {test_results}")



        else:
            doc["status"] = actual_status.get("actual_status")
            if is_culture:
                doc.setdefault("measures", {}).update(
                    {result["name"]: result["value"] for result in test_results}
                )
            else:
                doc.setdefault("measures", {}).update(
                    {result["name"]: result["value"] for result in test_results}
                )

        if actual_status.get("actual_status") in ["Rejected", "Not Done"]:
            doc["rejection_reason"] = not_done_reason.get("rejection_reason")

        db_oerr_tests.save(doc)
        logger.info(f"Document with ID {_id} updated successfully.")
        return True

    except Exception as e:
        logger.error(f"Error updating document: {str(e)}")
        return False

# API Endpoint
@oerr_bp.route('/oerr_update/', methods=["POST"])
def receive_payload():
    auth_header = request.headers.get('Authorization')
    if not authenticate_iblis(auth_header):
        return jsonify({"error": "Unauthorized"}), 401
    # LEAVE THIS HERE INCASE I WOULD LIKE TO USE THE ONLINE JSON
    iblis_payload = request.json
    if not iblis_payload:
        logger.error("Invalid JSON payload received.")
        return jsonify({"error": "Invalid JSON payload"}), 400
    processed_payload = process_payload(iblis_payload)
    logger.info(json.dumps(iblis_payload, indent=4))



    # payload = CULTURE_TEST_PAYLOAD
    # processed_payload = process_payload(payload)
    # print(type(processed_payload))
    # logger.info(json.dumps(processed_payload, indent=4))


    match_value = find_match(processed_payload.get("oerr_identifiers"))
    if match_value:
        if update_doc(**processed_payload):
            return jsonify({"message": "Update successful", "doc_id": match_value}), 200
        else:
            return jsonify({"warning": "Update failed", "doc_id": match_value}), 400
    else:
        return jsonify({"warning": "No match found"}), 404

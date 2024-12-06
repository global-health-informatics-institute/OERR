import datetime
import base64
import json
from flask import Blueprint, jsonify, request
from couchdb import Server
from extensions.extension import logger
from apis.extensions_api import (
    FACILITY_SECTIONS, VALID_PASSWORD, VALID_USER, TEST_PAYLOAD, 
    config_file, SPECIMEN_STATUSES, TEST_STATUSES
)

# Blueprint
oerr_bp = Blueprint('oerr', __name__)

# Configuration settings
settings = {}
with open(config_file) as json_file:
    settings = json.load(json_file)

# CouchDB connection
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

# Authentication
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

# Find matching document
def find_match(oerr_identifier):
    try:
        doc_id = oerr_identifier.get("_id")
        if doc_id and doc_id in db_oerr_tests:
            return doc_id

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

# Process payload
def process_payload(payload):
    def actual_status(specimen_status, test_status):
        return TEST_STATUSES.get(test_status, SPECIMEN_STATUSES.get(specimen_status, "Unknown"))

    def get_order_info():
        return {
            "is_panel": bool(payload.get("test_panel_id")),
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
            "test_type": str(oerr.get("test_type_id"))
        }

    def get_suscept_test_result():
        results = []
        for test in payload.get("suscept_test_result", []):
            for drug in test.get("drugs", []):
                results.append({
                    "organism_name": test.get("name"),
                    "drug_name": drug.get("name"),
                    "zone": drug.get("zone"),
                    "interpretation": drug.get("interpretation"),
                })
        return results

    def get_not_done_reason():
        for status in payload.get("status_trail", []):
            if status.get("status") == "rejected" and status.get("status_reason"):
                return status.get("status_reason")
        return None
    logger.info(json.dumps(get_oerr_identifiers(), indent=4))
    return {
        "order_information": get_order_info(),
        "test_results": get_test_results(),
        "actual_status": get_status_info(),
        "oerr_identifiers": get_oerr_identifiers(),
        "suscept_test_result": get_suscept_test_result(),
        "not_done_reason": get_not_done_reason()
    }

# Update document
def update_doc(order_information, test_results, suscept_test_result, actual_status, oerr_identifiers, not_done_reason):
    try:
        _id = oerr_identifiers.get("_id") or find_match(oerr_identifiers)
        if not _id:
            logger.error("No matching document found.")
            return False
        doc = db_oerr_tests.get(_id)
        doc["status"] = actual_status.get("actual_status")
        if actual_status.get("actual_status") in ["Rejected", "Not Done"]:
            doc["rejection_reason"] = not_done_reason
        if order_information.get("is_panel") and order_information.get("is_culture"):
            doc.setdefault("tests", {})[str(oerr_identifiers.get("test_type"))] = suscept_test_result
        elif order_information.get("is_panel"):
            doc.setdefault("tests", {})[str(oerr_identifiers.get("test_type"))] = {
                result["name"]: result["value"] for result in test_results
            }
        else:
            doc.setdefault("measures", {}).update(
                {result["name"]: result["value"] for result in test_results}
            )
        db_oerr_tests.save(doc)
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

 

    # payload = TEST_PAYLOAD
    # processed_payload = process_payload(payload)

    match_value = find_match(processed_payload.get("oerr_identifiers"))
    if match_value:
        if update_doc(**processed_payload):
            return jsonify({"message": "Update successful", "doc_id": match_value}), 200
        else:
            return jsonify({"warning": "Update failed", "doc_id": match_value}), 400
    else:
        return jsonify({"warning": "No match found"}), 404

import os
from apis.auth_api import load_token_from_db
from extensions.extension import logger
import json
import requests
from flask import Blueprint,jsonify
from couchdb import Server
from apis.extensions_api import BASE_URL, TEST_TYPE_ENDPOINT, config_file, couch_config

test_type_bp = Blueprint('test_types', __name__)

settings = {}
with open(config_file) as json_file:
    settings = json.load(json_file)

def connect_to_test_types():
    try:

        user = couch_config.get("user")
        passwd = couch_config.get("passwd")
        host = couch_config.get("host")
        port = couch_config.get("port")
        database = f'{couch_config.get("database")}_lab_test_type'

        couchConnection = Server(f"http://{user}:{passwd}@{host}:{port}/")
        global db_test_type
        db_test_type = couchConnection[database] if database in couchConnection else couchConnection.create(database)
        logger.info("Successfully connected to CouchDB.")        
    except Exception as e:
        logger.error(f"Error connecting to CouchDB: {str(e)}")
        raise

def load_test_type():
    if(requests.get(f'http://{couch_config.get("host")}:{couch_config.get("port")}/auth_client').status_code == 200):
        print("status 200")
    TOKEN = load_token_from_db()
    if not TOKEN:
        logger.error("No token available. Authentication required.")
        return jsonify({"error": "No token available. Please authenticate."}), 403

    url = f"{BASE_URL}{TEST_TYPE_ENDPOINT}"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_data = response.json()

            # Check if the response is a list
            if isinstance(response_data, list):
                test_types = response_data  # Directly assign it if it's a list
            elif isinstance(response_data, dict):
                test_types = response_data.get("test_types", [])  # Get "test_types" if it's a dict
            else:
                logger.error("Unexpected response format from API.")
                return jsonify({"error": "Unexpected response format."}), 500

            # Filter the fields to keep only id, name, department_id, and expected_turn_around_time
            filtered_test_types = []
            for test in test_types:
                filtered_test = {
                    "_id": test.get("name", ""),
                    "name": test.get("name", ""),
                    "department_id": test.get("department_id", ""),
                    "test_type_id": str(test.get("expected_turn_around_time", {}).get("test_type_id", "")),
                }
                filtered_test_types.append(filtered_test)

            # Save to a JSON file
            output_path = "dumps/iblis_test_types.json"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as outfile:
                json.dump(filtered_test_types, outfile, indent=4)

            logger.info(f"Filtered test types saved to {output_path}.")
            return jsonify({"message": "Test types loaded and saved successfully."}), 200
        else:
            logger.error(f"Failed to fetch test types: {response.status_code}")
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        logger.error(f"Error loading test types: {str(e)}")
        return jsonify({"error": str(e)}), 500




def update_test_type():
    json_dump = "dumps/iblis_test_types.json"
    try:
        # Load the JSON data from the file
        with open(json_dump, "r") as json_file:
            test_types = json.load(json_file)

        updated_count = 0
        missing_count = 0
        missing_doc_list = []


        for test in test_types:
            _id = test.get("_id")  # Identify document by `_id`
            if not _id:
                logger.warning("Skipping test type without '_id'.")
                continue

            # Check if the document exists in CouchDB
            global db_test_type
            if _id in db_test_type:
                doc = db_test_type[_id]

                for key, value in test.items():
                    if key not in doc or doc[key] != value:
                        doc[key] = value


                db_test_type.save(doc)
                updated_count += 1
            else:
                missing_doc_list.append(test)
                missing_count += 1

        logger.info(
            f"Update complete:\
                updated docs {updated_count}\
                Missing docs {missing_count}\
            "
        )
        return jsonify({"message": "Test types updated successfully.", "updated": updated_count, "Missing": missing_count, "missing list": missing_doc_list}), 200

    except FileNotFoundError:
        logger.error("JSON file not found. Make sure the file exists and is accessible.")
        return jsonify({"error": "JSON file not found."}), 404
    except Exception as e:
        logger.error(f"Error updating test types: {str(e)}")
        return jsonify({"error": str(e)}), 500


@test_type_bp.route("/download_test_types/", methods=["GET"])
def load_tests():
    return load_test_type()

@test_type_bp.route("/update_test_types/", methods=["GET"])
def update_tests():
    return update_test_type()
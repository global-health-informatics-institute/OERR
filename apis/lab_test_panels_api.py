import os
from apis.auth_api import load_token_from_db
from extensions.extension import logger
import json
import requests
from flask import Blueprint,jsonify
from couchdb import Server
from apis.extensions_api import BASE_URL, TEST_PANEL_ENDPOINT, config_file

test_panels_bp = Blueprint('test_panels', __name__)

settings = {}
with open(config_file) as json_file:
    settings = json.load(json_file)

def connect_to_test_panels():
    try:
        couch_config = settings.get("couch", {})
        user = couch_config.get("user")
        passwd = couch_config.get("passwd")
        host = couch_config.get("host")
        port = couch_config.get("port")
        database = f'{couch_config.get("database")}_lab_test_panels'

        couchConnection = Server(f"http://{user}:{passwd}@{host}:{port}/")
        global db_test_panels
        db_test_panels = couchConnection[database] if database in couchConnection else couchConnection.create(database)
        logger.info("Successfully connected to CouchDB.")        
    except Exception as e:
        logger.error(f"Error connecting to CouchDB: {str(e)}")
        raise


def load_test_panels():
    TOKEN = load_token_from_db()
    if not TOKEN:
        logger.error("No token available. Authentication required.")
        return jsonify({"error": "No token available. Please authenticate."}), 403

    url = f"{BASE_URL}{TEST_PANEL_ENDPOINT}"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_data = response.json()

            # Check if the response is a list
            if isinstance(response_data, list):
                test_panels = response_data  # Directly assign if it's a list
            elif isinstance(response_data, dict):
                test_panels = response_data.get("test_panels", [])  # Get "test_panels" if it's a dict
            else:
                logger.error("Unexpected response format from API.")
                return jsonify({"error": "Unexpected response format."}), 500

            # Filter the fields to keep only id, name, short_name, and panel_id
            filtered_test_panels = []
            for panel in test_panels:
                filtered_panel = {
                    "_id": panel.get("name", ""),
                    "name": panel.get("name", ""),
                    "short_name": panel.get("short_name", ""),
                    "panel_id": str(panel.get("id", "")),
                }
                filtered_test_panels.append(filtered_panel)

            # Save to a JSON file
            output_path = "dumps/iblis_test_panels.json"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as outfile:
                json.dump(filtered_test_panels, outfile, indent=4)

            logger.info(f"Filtered test panels saved to {output_path}.")
            return jsonify({"message": "Test panels loaded and saved successfully."}), 200
        else:
            logger.error(f"Failed to fetch test panels: {response.status_code}")
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        logger.error(f"Error loading test panels: {str(e)}")
        return jsonify({"error": str(e)}), 500


def update_test_panels():
    json_dump = "dumps/iblis_test_panels.json"
    try:
        # Load the JSON data from the file
        with open(json_dump, "r") as json_file:
            test_panels = json.load(json_file)

        updated_count = 0
        missing_count = 0
        missing_doc_list = []


        for panel in test_panels:
            _id = panel.get("_id")  # Identify document by `_id`
            if not _id:
                logger.warning("Skipping test panels without '_id'.")
                continue

            # Check if the document exists in CouchDB
            global db_test_panels
            if _id in db_test_panels:
                doc = db_test_panels[_id]

                for key, value in panel.items():
                    if key not in doc or doc[key] != value:
                        doc[key] = value


                db_test_panels.save(doc)
                updated_count += 1
            else:
                missing_doc_list.append(panel)
                missing_count += 1

        logger.info(
            f"Update complete:\
                updated docs {updated_count}\
                Missing docs {missing_count}\
            "
        )
        return jsonify({"message": "Test panels updated successfully.", "updated": updated_count, "Missing": missing_count, "missing list": missing_doc_list}), 200

    except FileNotFoundError:
        logger.error("JSON file not found. Make sure the file exists and is accessible.")
        return jsonify({"error": "JSON file not found."}), 404
    except Exception as e:
        logger.error(f"Error updating test types: {str(e)}")
        return jsonify({"error": str(e)}), 500


@test_panels_bp.route("/download_test_panels/", methods=["GET"])
def load_tests_panels():
    return load_test_panels()

@test_panels_bp.route("/update_test_panels/", methods=["GET"])
def update_tests_panels():
    return update_test_panels()
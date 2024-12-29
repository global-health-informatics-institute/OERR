import os
from apis.auth_api import load_token_from_db
from extensions.extension import logger
import json
import requests
from flask import Blueprint,jsonify
from couchdb import Server
from apis.extensions_api import BASE_URL, SPECIMEN_ENDPOINT, couch_config

specimen_bp = Blueprint('specimens', __name__)

settings = {}

def load_specimens_function():
    if(requests.get(f'http://{couch_config.get("host")}:{couch_config.get("port")}/auth_client').status_code == 200):
        print("status 200")
    TOKEN = load_token_from_db()
    if not TOKEN:
        logger.error("No token available. Authentication required.")
        return jsonify({"error": "No token available. Please authenticate."}), 403

    url = f"{BASE_URL}{SPECIMEN_ENDPOINT}"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_data = response.json()

            # Check if the response is a list
            if isinstance(response_data, list):
                specimens = response_data
            elif isinstance(response_data, dict):
                specimens = response_data.get("", [])
            else:
                logger.error("Unexpected response format from API.")
                return jsonify({"error": "Unexpected response format."}), 500


            filtered_specimens = []
            for specimen in specimens:
                filtered_specimen = {
                    "_id": specimen.get("name", ""),
                    "name": specimen.get("name", ""),
                    "id": str(specimen.get("id", "")),
                }
                filtered_specimens.append(filtered_specimen)

            # Save to a JSON file
            output_path = "dumps/iblis_specimens.json"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as outfile:
                json.dump(filtered_specimens, outfile, indent=4)

            logger.info(f"Filtered specimen saved to {output_path}.")
            return jsonify({"message": "specimens loaded and saved successfully."}), 200
        else:
            logger.error(f"Failed to fetch test specimens: {response.status_code}")
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        logger.error(f"Error loading specimen: {str(e)}")
        return jsonify({"error": str(e)}), 500




@specimen_bp.route("/download_specimens/", methods=["GET"])
def load_specimens():
    return load_specimens_function()

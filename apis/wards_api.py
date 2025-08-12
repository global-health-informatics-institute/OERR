import os
from apis.auth_api import load_token_from_db
from extensions.extension import logger
import json
import requests
from flask import Blueprint,jsonify
from couchdb import Server
from apis.extensions_api import BASE_URL, WARD_ENDPOINT, couch_config

ward_bp = Blueprint('wards', __name__)

settings = {}

def load_wards_function():
    if(requests.get(f'http://{couch_config.get("host")}:{couch_config.get("port")}/auth_client').status_code == 200):
        print("status 200")
    TOKEN = load_token_from_db()
    if not TOKEN:
        logger.error("No token available. Authentication required.")
        return jsonify({"error": "No token available. Please authenticate."}), 403

    url = f"{BASE_URL}{WARD_ENDPOINT}"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_data = response.json()

            # Check if the response is a list
            if isinstance(response_data, list):
                wards = response_data
            elif isinstance(response_data, dict):
                wards = response_data.get("data", [])
            else:
                logger.error("Unexpected response format from API.")
                return jsonify({"error": "Unexpected response format."}), 500


            filtered_wards = []
            for ward in wards:
                filtered_ward = {
                    "_id": ward.get("name", ""),
                    "name": ward.get("name", ""),
                    "id": str(ward.get("id", "")),
                }
                print(ward)
                filtered_wards.append(filtered_ward)

            # Save to a JSON file
            output_path = "dumps/iblis_wards.json"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as outfile:
                json.dump(filtered_wards, outfile, indent=4)

            logger.info(f"Filtered wards saved to {output_path}.")
            return jsonify({"message": "Wards loaded and saved successfully."}), 200
        else:
            logger.error(f"Failed to fetch test wards: {response.status_code}")
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        logger.error(f"Error loading wards: {str(e)}")
        return jsonify({"error": str(e)}), 500




@ward_bp.route("/download_wards/", methods=["GET"])
def load_wards():
    return load_wards_function()

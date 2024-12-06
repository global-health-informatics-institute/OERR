import os
from apis.auth_api import load_token_from_db
from extensions.extension import logger
import json
import requests
from flask import Blueprint,jsonify
from couchdb import Server
from apis.extensions_api import BASE_URL, DEPARTMENT_ENDPOINT, couch_config

department_bp = Blueprint('departments', __name__)

settings = {}

def load_departments_function():
    if(requests.get(f'http://{couch_config.get("host")}:{couch_config.get("port")}/auth_client').status_code == 200):
        print("status 200")
    TOKEN = load_token_from_db()
    if not TOKEN:
        logger.error("No token available. Authentication required.")
        return jsonify({"error": "No token available. Please authenticate."}), 403

    url = f"{BASE_URL}{DEPARTMENT_ENDPOINT}"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_data = response.json()

            # Check if the response is a list
            if isinstance(response_data, list):
                departments = response_data
            elif isinstance(response_data, dict):
                departments = response_data.get("", [])
            else:
                logger.error("Unexpected response format from API.")
                return jsonify({"error": "Unexpected response format."}), 500


            filtered_departments = []
            for department in departments:
                filtered_department = {
                    "_id": department.get("name", ""),
                    "name": department.get("name", ""),
                    "id": str(department.get("id", "")),
                }
                filtered_departments.append(filtered_department)

            # Save to a JSON file
            output_path = "dumps/iblis_departments.json"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as outfile:
                json.dump(filtered_departments, outfile, indent=4)

            logger.info(f"Filtered department saved to {output_path}.")
            return jsonify({"message": "departments loaded and saved successfully."}), 200
        else:
            logger.error(f"Failed to fetch test departments: {response.status_code}")
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        logger.error(f"Error loading department: {str(e)}")
        return jsonify({"error": str(e)}), 500




@department_bp.route("/download_departments/", methods=["GET"])
def load_departments():
    return load_departments_function()

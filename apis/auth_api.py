from extensions.extension import logger
import json
import requests
from flask import Blueprint, Flask, jsonify
from couchdb import Server
from datetime import datetime, timezone
from apis.extensions_api import BASE_URL, LOGIN_ENDPOINT, REFRESH_ENDPOINT, auth_payload, config_file

auth_bp = Blueprint('auth', __name__)


# Globals
TOKEN = None
global db
global db_test_type

# Load Configurations
settings = {}
with open(config_file) as json_file:
    settings = json.load(json_file)


# Database Connection
def connect_to_tokken():
    try:
        couch_config = settings.get("couch", {})
        user = couch_config.get("user")
        passwd = couch_config.get("passwd")
        host = couch_config.get("host")
        port = couch_config.get("port")
        database = f'{couch_config.get("database")}_token'

        couchConnection = Server(f"http://{user}:{passwd}@{host}:{port}/")
        global db
        db = couchConnection[database] if database in couchConnection else couchConnection.create(database)
        logger.info("Successfully connected to CouchDB.")        
    except Exception as e:
        logger.error(f"Error connecting to CouchDB: {str(e)}")
        raise

def save_token(token, date):
    try:
        global TOKEN
        TOKEN = token  # Save token globally

        doc_id = "application_token"
        if doc_id in db:
            doc = db[doc_id]
            doc["token"] = token
            doc["expiry_date"] = date
            db.save(doc)
        else:
            db[doc_id] = {
                "type": "tokens",
                "token": token,
                "expiry_date": date
            }
        logger.info("Token successfully saved/updated in CouchDB.")
    except Exception as e:
        logger.error(f"Failed to save token to CouchDB: {str(e)}")


def load_token_from_db():
    global TOKEN
    try:
        doc_id = "application_token"
        if doc_id in db:
            token_doc = db[doc_id]
            TOKEN = token_doc.get("token")
            expiry_date = token_doc.get("expiry_date")
            logger.info(f"Loaded token from CouchDB: {TOKEN}, Expires: {expiry_date} \n\n")
            return TOKEN
        else:
            logger.warning("No token found in CouchDB.")
            return None
    except Exception as e:
        logger.error(f"Error loading token from CouchDB: {str(e)}")
        return None


def login_auth():
    url = f"{BASE_URL}{LOGIN_ENDPOINT}"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, json=auth_payload)
        if response.status_code == 200:
            data = response.json()
            token = data.get("authorization", {}).get("token")
            expiry_date = data.get("authorization", {}).get("expiry_time")
            if token and expiry_date:
                save_token(token=token, date=expiry_date)
            return jsonify(data), 200
        else:
            logger.warning(f"Login Auth Failed: {response.status_code}")
            return jsonify({"error": response.text}), 401
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP Request failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

def refresh_auth():
        try:
            # Retrieve the token document
            doc_id = "application_token"
            if doc_id in db:
                token_doc = db[doc_id]
                expiry_date_str = token_doc.get("expiry_date")

                # Parse expiry_date and compare with the current time
                expiry_date = datetime.fromisoformat(expiry_date_str.replace("Z", "+00:00"))
                current_time = datetime.now(timezone.utc)

                if current_time >= expiry_date:
                    logger.info("Token expired. Re-authentication needed.")
                    return True  # Token is expired
                else:
                    logger.info(f"Token is still valid. Expires at {expiry_date}.")
                    return False  # Token is still valid
            else:
                logger.warning("Token document not found. Re-authentication needed.")
                return True  # No token document found, force re-authentication
        except Exception as e:
            logger.error(f"Error checking token validity: {str(e)}")
            return True  # On error, assume token is invalid

def refresh_helper(token):
    url = f"{BASE_URL}{REFRESH_ENDPOINT}"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            refreshed_token = data.get("authorization", {}).get("token")
            expiry_date = data.get("authorization", {}).get("expiry_time")
            if refreshed_token and expiry_date:
                save_token(token=refreshed_token, date=expiry_date)
            return refreshed_token
        else:
            logger.warning(f"Refresh Failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP Request failed: {str(e)}")
        return None


@auth_bp.route("/auth_client/", methods=["POST", "GET"])
def retrieve_token():
    if refresh_auth():
        return login_auth()
    else:
        return jsonify(
            {
                "message": "Token is still valid.",
                "token": TOKEN
            }
        ), 200

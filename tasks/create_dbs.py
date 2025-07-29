import json
import requests
from requests.auth import HTTPBasicAuth
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

basis_file = "config/basis.config"


with open(basis_file) as json_file:
    basis_settings = json.load(json_file)
url = f"http://{basis_settings['couch']['host']}:{basis_settings['couch']['port']}"
DB = f"{url}/{basis_settings['couch']['database']}"
username = f"{basis_settings['couch']['user']}"
password = f"{basis_settings['couch']['passwd']}"
database = f"{basis_settings['couch']['database']}"

sub_dir = ["","_patients", "_lab_test_panels", "_lab_test_type", "_users"]

def ensure_database_exists(sub):
    database_name = f"{database}{sub}"
    address = f"{url}/{database_name}"

    try:
        response = requests.get(address, auth=HTTPBasicAuth(username, password))

        if response.status_code == 404:
            create_db_response = requests.put(address, auth=HTTPBasicAuth(username, password))

            if create_db_response.status_code == 201:
                logging.info(f"Database '{database_name}' created successfully.")
            else:
                logging.error(f"Failed to create database '{database_name}': {create_db_response.status_code} - {create_db_response.text}")
        elif response.status_code == 200:
            logging.info(f"Database '{database_name}' already exists.")
        else:
            logging.error(f"Error connecting to the database '{database_name}': {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while connecting to '{database_name}': {str(e)}")
        return False
    
    return True

if(__name__ == "__main__"):
    for dir in sub_dir:
        ensure_database_exists(dir)


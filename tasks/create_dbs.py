import requests
from requests.auth import HTTPBasicAuth
import logging
from utils import misc

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

settings = misc.initialize_settings()
url = f"http://{settings['couch']['host']}:{settings['couch']['port']}"
username = settings['couch']['user']
password = settings['couch']['passwd']
database = settings['couch']['database']

sub_dir = ["","_patients", "_lab_test_panels", "_lab_test_type", "_users", "_view_events"]

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

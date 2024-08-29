import os

url = os.getenv('COUCHDB_URL', "http://127.0.0.1:5984/")
DB = f"{url}/oerr"
username = os.getenv('COUCHDB_USERNAME', "admin")
password = os.getenv('COUCHDB_PASSWORD', "root")

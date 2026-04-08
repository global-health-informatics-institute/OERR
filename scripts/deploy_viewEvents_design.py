#!/usr/bin/env python
"""
Script to deploy the viewEvents design document to ****CouchDB****
This creates the log_tab_tap update handler that logs test view events.

Usage: python scripts/deploy_viewEvents_design.py
"""

import json
import sys
from couchdb import Server
from utils import misc

def deploy_design_document():
    
    settings = misc.initialize_settings()
    
    couch_connection = Server("http://%s:%s@%s:%s/" %
                              (settings["couch"]["user"], settings["couch"]["passwd"],
                               settings["couch"]["host"], settings["couch"]["port"]))
    
    db_name = settings["couch"]["database"] + "_view_events"
    
    try:
        db = couch_connection[db_name]
    except Exception as e:
        print(f"Error: Could not connect to database '{db_name}': {e}")
        sys.exit(1)
    
    
    with open('config/viewEvents_design.json') as f:
        design_doc = json.load(f)
    
    doc_id = design_doc["_id"]
    

    try:
        existing_doc = db[doc_id]
        design_doc["_rev"] = existing_doc["_rev"]
        print(f"Updating existing design document: {doc_id}")
    except:
        print(f"Creating new design document: {doc_id}")
    

    try:
        db.save(design_doc)
        print(f"Successfully deployed design document: {doc_id}")
        print("\nThe viewEvents view  is now available.")
        print("Usage: GET/{db}/_design/viewEvents/_view/by_test_id_and time")
        return True
    except Exception as e:
        print(f"Error saving design document: {e}")
        return False

if __name__ == "__main__":
    success = deploy_design_document()
    sys.exit(0 if success else 1)

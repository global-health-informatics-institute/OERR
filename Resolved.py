import json

import requests

url = "http://localhost:5984/mss_results_new/"
username = "admin"
password = "1234"

def resolve_conflicts():
    response = requests.get(url + "_all_docs?conflicts=true", auth=(username, password))
    conflicted_docs = response.json()["rows"]
    for doc in conflicted_docs:
        doc_id = doc["id"]
        print(f"Conflicted document: {doc_id}")


        response = requests.get(url + "/" + doc_id + "?open_revs=all", auth=(username, password))


        if response.status_code == 200:
            parts = response.text.split("--")[1:-1]


            for part in parts:
                if len(part.split("\r\n\r\n")) > 1:
                    revision_data = json.loads(part.split("\r\n\r\n")[1])
                    winning_rev = revision_data["_rev"]
                    data = {"_rev": winning_rev}

                update_response = requests.put(url + "/" + doc_id, json=data, auth=(username, password))
                if update_response.status_code == 200:
                    print(f"Conflict resolved for document: {doc_id}")
                else:
                    print(f"Failed to resolve conflict for document: {doc_id}")
        else:
            print(f"Failed to fetch revisions for document {doc_id}")

if __name__ == "__main__":
    resolve_conflicts()
import requests
import random
import json

url = "http://127.0.0.1:5984"
DB = "http://127.0.0.1:5984/mss_results_new"
username = "admin"
password = "1234"


def writem(docs):
    response = requests.post(f"{DB}/_bulk_docs", json={"docs": docs})
    response.raise_for_status()  # Raise error for non-200 status codes
    return response.json()


def write1(doc, id=None, rev=None):
    if id:
        doc["_id"] = id
    if rev:
        doc["_rev"] = rev
    return writem([doc])[0]["rev"]


def read1(id):
    retries = 0
    while True:
        try:
            response = requests.get(f"{DB}/{id}?conflicts=true", auth=(username, password))
            response.raise_for_status()
            data = response.json()
            if "_conflicts" in data:
                conflicts = data.pop("_conflicts")
                revisions = [data]
                for rev in conflicts:
                    response = requests.get(f"{DB}/{id}?rev={rev}", auth=(username, password))
                    response.raise_for_status()
                    revisions.append(response.json())
                return revisions
            else:
                return [data]
        except requests.exceptions.RequestException as e:
            retries += 1
            if retries >= 5:
                raise


def resolve_conflicts():
    response = requests.get(f"{DB}/_all_docs?conflicts=true", auth=(username, password))
    response.raise_for_status()
    conflicted_docs = response.json()["rows"]

    for doc in conflicted_docs:
        doc_id = doc["id"]
        print(f"Conflicted document: {doc_id}")

        try:
            # Check document existence before fetching revisions
            response = requests.get(f"{DB}/{doc_id}", auth=(username, password))
            if response.status_code == 200:
                # Document exists, proceed with conflict resolution

                try:
                    response = requests.get(url + "/" + doc_id + "?open_revs=all", auth=(username, password))
                    response.raise_for_status()

                    if response.status_code == 200:
                        parts = response.text.split("--")[1:-1]

                        # Choose a random revision (arbitrary selection)
                        if len(parts) > 0:
                            winning_rev_index = random.randrange(len(parts))
                            winning_rev_data = json.loads(parts[winning_rev_index].split("\r\n\r\n")[1])
                            winning_rev = winning_rev_data["_rev"]

                            data = {"_rev": winning_rev}
                            update_response = requests.put(url + "/" + doc_id, json=data, auth=(username, password))

                            if update_response.status_code == 200:
                                print(f"Conflict resolved for document: {doc_id}")
                            else:
                                print(f"Failed to update document: {doc_id}")
                    else:
                        print(f"Failed to fetch revisions for document {doc_id}")

                except requests.exceptions.RequestException as e:
                    print(f"Error resolving conflict for document {doc_id}: {e}")

            else:
                print(f"Document {doc_id} not found. Skipping conflict resolution.")

        except requests.exceptions.RequestException as e:
            print(f"Error checking document existence: {e}")


if __name__ == "__main__":
    resolve_conflicts()

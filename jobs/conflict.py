import subprocess

username = "admin"
password = "1234"
couch_server = "http://localhost:5984"
db_name = "mss_results_new"

def resolve_conflicts():
    command = f"curl -sSf -u '{username}:{password}' '{couch_server}/{db_name}/_all_docs?include_docs=true&conflicts=true' | jq '.rows[].id'"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()

    if err:
        print(f"Error retrieving conflicted documents: {err.decode()}")
        return

    conflicted_docs = out.decode().strip().split("\n")


    for doc_id in conflicted_docs:
        print(f"Conflicted document: {doc_id}")


        command = f"curl -sSf -u '{username}:{password}' '{couch_server}/{db_name}/{doc_id}?open_revs=all'"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()

        if err:
            print(f"Error retrieving revisions for document {doc_id}: {err.decode()}")
            continue

        revisions_json = out.decode()



if __name__ == "__main__":
    resolve_conflicts()

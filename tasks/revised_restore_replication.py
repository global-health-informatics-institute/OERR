import json
import subprocess
import datetime
import sys

now = datetime.datetime.now()

start_time = now.replace(hour=7, minute=30, second=0, microsecond=0)
end_time = now.replace(hour=8, minute=30, second=0, microsecond=0)

if start_time <= now <= end_time:
    sys.exit(0)

replications_file = "config/replications.config"
ward_file = "config/department.config"
log_file = "logs/replication_errors.log"

with open(replications_file) as json_file:
    replication_settings = json.load(json_file)

with open(ward_file) as json_file:
    wards_data = json.load(json_file)

department_name = replication_settings["specific_department"]["department"]
wards = []
for department in wards_data["departments"]:
    if department["name"] == department_name:
        wards = department["wards"]
        break

source_url = f"http://{replication_settings['source']['user']}:{replication_settings['source']['passwd']}@{replication_settings['source']['host']}:{replication_settings['source']['port']}/{replication_settings['source_base_db']['database']}"
target_url = f"http://{replication_settings['target']['user']}:{replication_settings['target']['password']}@{replication_settings['target']['host']}:{replication_settings['target']['port']}/{replication_settings['target_base_db']['database']}"
replicator_db_url = f"http://{replication_settings['source']['user']}:{replication_settings['source']['passwd']}@{replication_settings['source']['host']}:{replication_settings['source']['port']}/_replicator"

# Check if the replicator database already exists
check_replicator_db_cmd = ['curl', '-X', 'GET', replicator_db_url]
try:
    result = subprocess.run(check_replicator_db_cmd, check=True, capture_output=True, text=True)
    # If the GET request is successful, the database exists, so delete it
    delete_replicator_db_cmd = ['curl', '-X', 'DELETE', replicator_db_url]
    subprocess.run(delete_replicator_db_cmd, check=True, capture_output=True, text=True)
    with open(log_file, 'a') as log:
        log.write("Deleted existing _replicator database.\n")
except subprocess.CalledProcessError:
    # If the GET fails, the _replicator database doesn't exist; proceed without deleting
    with open(log_file, 'a') as log:
        log.write("No existing _replicator database found to delete.\n")

# Create the _replicator database
create_replicator_db_cmd = ['curl', '-X', 'PUT', replicator_db_url]
try:
    subprocess.run(create_replicator_db_cmd, check=True, capture_output=True, text=True)
    with open(log_file, 'a') as log:
        log.write("Created _replicator database.\n")
except subprocess.CalledProcessError as e:
    with open(log_file, 'a') as log:
        log.write(f"Error creating _replicator database: {e.stderr}\n")

design_id = (replication_settings["source"]["host"]).replace('.', '')

design_doc = {
    "filters": {
        f"ward_filter_{design_id}": f"function(doc, req) {{ var wards = {json.dumps(wards)}; return wards.includes(doc.ward); }}"
    }
}

#  check if design document already exists
check_design_doc_cmd = [
    'curl', '-X', 'GET', f"{target_url}/_design/ward_filter_{design_id}"
]
try:
    result = subprocess.run(check_design_doc_cmd, check=True, capture_output=True, text=True)
    if result.returncode == 0:
        # If the design document exists, delete it
        delete_design_doc_cmd = [
            'curl', '-X', 'DELETE', f"{target_url}/_design/ward_filter_{design_id}"
        ]
        subprocess.run(delete_design_doc_cmd, check=True, capture_output=True, text=True)
        with open(log_file, 'a') as log:
            log.write("Deleted existing design document.\n")
except subprocess.CalledProcessError:
    # If the GET fails, the design document doesn't exist; proceed without deleting
    with open(log_file, 'a') as log:
        log.write("No existing design document found to delete.\n")

# Create or update the design document
create_design_doc_cmd = [
    'curl', '-d', json.dumps(design_doc), '-H', 'Content-Type: application/json',
    '-X', 'PUT', f"{target_url}/_design/ward_filter_{design_id}"
]
# try:
#     result = subprocess.run(create_design_doc_cmd, check=True, capture_output=True, text=True)
#     with open(log_file, 'a') as log:
#         log.write("Design document created or updated successfully on the target database.\n")
# except subprocess.CalledProcessError as e:
#     with open(log_file, 'a') as log:
#         log.write(f"Error creating design document: {e.stderr}\n")

def execute_replication(command, log_message):
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        with open(log_file, 'a') as log:
            log.write(f"{log_message} succeeded.\n")
    except subprocess.CalledProcessError as e:
        with open(log_file, 'a') as log:
            log.write(f"Error: {log_message} failed.\n{e.stderr}\n")

source_to_target_cmd = [
    'curl', '-d', json.dumps({
        "_id": "base-source-to-target",
        "source": source_url,
        "target": target_url,
        "create_target": True,
        "continuous": True
    }), '-H', 'Content-Type: application/json', '-X', 'POST', replicator_db_url
]

target_to_source_cmd = [
    'curl', '-d', json.dumps({
        "_id": "target-to-source-filtered",
        "source": target_url,
        "target": source_url,
        "create_target": True,
        "continuous": True,
        "filter": f"ward_filter_{design_id}/ward_filter_{design_id}"
    }), '-H', 'Content-Type: application/json', '-X', 'POST', replicator_db_url
]

execute_replication(source_to_target_cmd, "Setting up replication from source to target")
execute_replication(target_to_source_cmd, "Setting up filtered replication from target to source")

sub_directories = ["_lab_test_panels", "_lab_test_type", "_patients", "_users"]

for suffix in sub_directories:
    source_suffix_url = f"{replication_settings['source_base_db']['database']}{suffix}"
    target_suffix_url = f"{replication_settings['target_base_db']['database']}{suffix}"
    
    source_url = f"http://{replication_settings['source']['user']}:{replication_settings['source']['passwd']}@{replication_settings['source']['host']}:{replication_settings['source']['port']}/{source_suffix_url}"
    target_url = f"http://{replication_settings['target']['user']}:{replication_settings['target']['password']}@{replication_settings['target']['host']}:{replication_settings['target']['port']}/{target_suffix_url}"

    source_to_target_cmd = [
        'curl', '-d', json.dumps({
            "_id": f"base-source-to-target{suffix}",
            "source": source_url,
            "target": target_url,
            "create_target": True,
            "continuous": True
        }), '-H', 'Content-Type: application/json', '-X', 'POST', replicator_db_url
    ]
    
    target_to_source_cmd_ltp = [
        'curl', '-d', json.dumps({
            "_id": f"base-target-to-source{suffix}",
            "source": target_url,
            "target": source_url,
            "create_target": True,
            "continuous": True,
        }), '-H', 'Content-Type: application/json', '-X', 'POST', replicator_db_url
    ]

    execute_replication(source_to_target_cmd, f"Replication setup from source to target for {suffix}")
    execute_replication(target_to_source_cmd_ltp, f"Replication setup from target to source for {suffix}")

import json
import subprocess

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



create_replicator_db_cmd = ['curl', '-X', 'PUT', replicator_db_url]
try:
    subprocess.run(create_replicator_db_cmd, check=True, capture_output=True, text=True)
    with open(log_file, 'a') as log:
        log.write(f"Created replicator database:\n")
except subprocess.CalledProcessError as e:
    with open(log_file, 'a') as log:
        log.write(f"Error creating _replicator database: {e.stderr}\n")

design_id = (replication_settings["source"]["host"]).replace('.', '')

design_doc = {
    "_id": f"_design/ward_filter_{design_id}",
    "filters": {
        "ward_filter": f"function(doc, req) {{ var wards = {json.dumps(wards)}; return wards.includes(doc.ward); }}"
    }
}

create_design_doc_cmd = [
    'curl', '-d', json.dumps(design_doc), '-H', 'Content-Type: application/json',
    '-X', 'PUT', f"{target_url}/_design/ward_filter_{design_id}"
]
try:
    result = subprocess.run(create_design_doc_cmd, check=True, capture_output=True, text=True)
    with open(log_file, 'a') as log:
        log.write(f"Design document created successfully on the target database\n")
except subprocess.CalledProcessError as e:
    with open(log_file, 'a') as log:
        log.write(f"Error creating design document: {e.stderr}\n")

def execute_replication(command, log_message):
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        with open(log_file, 'a') as log:
            log.write(f"{log_message} - Replication setup: {command}\n")
    except subprocess.CalledProcessError as e:
        with open(log_file, 'a') as log:
            log.write(f"Error: {log_message}\n{e.stderr}\n")


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
        "_id": "base-target-to-source",
        "source": target_url,
        "target": source_url,
        "create_target": True,
        "continuous": True,
        "filter": f"_design/ward_filter_{design_id}/ward_filter"
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
            "_id": f"base-source-to-target_{suffix}",
            "source": source_url,
            "target": target_url,
            "create_target": True,
            "continuous": True
        }), '-H', 'Content-Type: application/json', '-X', 'POST', replicator_db_url
    ]
    
    target_to_source_cmd_ltp = [
        'curl', '-d', json.dumps({
            "_id": f"base-target-to-source_{suffix}",
            "source": target_url,
            "target": source_url,
            "create_target": True,
            "continuous": True,
        }), '-H', 'Content-Type: application/json', '-X', 'POST', replicator_db_url
    ]

    execute_replication(source_to_target_cmd, f"Replication setup from source to target for {suffix}")
    execute_replication(target_to_source_cmd_ltp, f"Replication setup from target to source for {suffix}")


    source_url = f"http://{replication_settings['source']['user']}:{replication_settings['source']['passwd']}@{replication_settings['source']['host']}:{replication_settings['source']['port']}/{replication_settings['source_base_db']['database']}{suffix}"

    target_url = f"http://{replication_settings['target']['user']}:{replication_settings['target']['password']}@{replication_settings['target']['host']}:{replication_settings['target']['port']}/{replication_settings['target_base_db']['database']}{suffix}"

    target_to_source_cmd_ltp = [
        'curl', '-d', json.dumps({
            "_id": f"base-target-to-source_{suffix}",
            "source": target_url,
            "target": source_url,
            "create_target": True,
            "continuous": True,
        }), '-H', 'Content-Type: application/json', '-X', 'POST', replicator_db_url
    ]
    execute_replication(source_to_target_cmd, f"{suffix}")

    source_to_target_cmd = [
        'curl', '-d', json.dumps({
            "_id": f"base-source-to-target_{suffix}",
            "source": source_url,
            "target": target_url,
            "create_target": True,
            "continuous": True
        }), '-H', 'Content-Type: application/json', '-X', 'POST', replicator_db_url
    ]
    execute_replication(target_to_source_cmd, f"{suffix}")
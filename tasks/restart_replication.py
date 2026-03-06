import json
import subprocess
import datetime
import sys
import logging


logging.basicConfig(level=logging.INFO)

replications_file = "config/replications.config"
ward_file = "config/department.config"
log_file = "logs/restart_replication.log"

with open(replications_file) as json_file:
    replication_settings = json.load(json_file)

with open(ward_file) as json_file:
    wards_data = json.load(json_file)

START_HOUR = replication_settings["threshhold"]["start_hour"] | 1
START_MINUTE = replication_settings["threshhold"]["start_minute"] | 0
START_SECOND = replication_settings["threshhold"]["start_second"] | 0
START_MICROSECOND = replication_settings["threshhold"]["start_microsecond"] | 0

END_HOUR = replication_settings["threshhold"]["end_hour"] | 3
END_MINUTE = replication_settings["threshhold"]["end_minute"] | 0
END_SECOND = replication_settings["threshhold"]["end_second"]   | 0
END_MICROSECOND = replication_settings["threshhold"]["end_microsecond"] | 0

# wards list for the specific department to be used in the filter function of the replication
department_name = replication_settings["specific_department"]["department"]
wards = []
for department in wards_data["departments"]:
    if department["name"] == department_name:
        wards = department["wards"]
        break


now = datetime.datetime.now()

start_time = now.replace(hour=START_HOUR, minute=START_MINUTE, second=START_SECOND, microsecond=START_MICROSECOND)
end_time = now.replace(hour=END_HOUR, minute=END_MINUTE, second=END_SECOND, microsecond=END_MICROSECOND)

if start_time <= now  <= end_time:
    with open(log_file, 'a') as log:
        log.write(f"{datetime.datetime.now()} - Replication skipped at {now} as it is within the threshhold time window.\n")
        logging.info(f"{now} : as it is within the threshhold time window.")
    sys.exit(0)



source_url = f"http://{replication_settings['source']['user']}:{replication_settings['source']['passwd']}@{replication_settings['source']['host']}:{replication_settings['source']['port']}/{replication_settings['source_base_db']['database']}"
target_url = f"http://{replication_settings['target']['user']}:{replication_settings['target']['password']}@{replication_settings['target']['host']}:{replication_settings['target']['port']}/{replication_settings['target_base_db']['database']}"
replicator_db_url = f"http://{replication_settings['source']['user']}:{replication_settings['source']['passwd']}@{replication_settings['source']['host']}:{replication_settings['source']['port']}/_replicator"

# make log file empty at the start of each run
with open(log_file, 'w') as log:
    log.write(f"{datetime.datetime.now()} - Starting replication restart process...\n")
    logging.info(f"Starting replication restart process...")

# delete replicator database if it exists
delete_replicator_db_cmd = ['curl', '-X', 'DELETE', replicator_db_url]
try:
    subprocess.run(delete_replicator_db_cmd, check=True, capture_output=True, text=True)
    logging.info(f"Deleting _replicator database if it exists...")
    with open(log_file, 'a') as log:
        log.write(f"{datetime.datetime.now()} - Deleting _replicator database if it exists...\n")
except subprocess.CalledProcessError as e:
    with open(log_file, 'a') as log:
        log.write(f"{datetime.datetime.now()} - Error deleting _replicator database: {e.stderr}\n")


# create new replicator database
create_replicator_db_cmd = ['curl', '-X', 'PUT', replicator_db_url]
try:
    subprocess.run(create_replicator_db_cmd, check=True, capture_output=True, text=True)
    with open(log_file, 'a') as log:
        log.write(f"{datetime.datetime.now()} - Created replicator databese:\n")
        logging.info(f"Created replicator databese...")
except subprocess.CalledProcessError as e:
    with open(log_file, 'a') as log:
        log.write(f"{datetime.datetime.now()} - Error creating _replicator database: {e.stderr}\n")
        logging.error(f"Error creating _replicator database: {e.stderr}")
# create design document for filtered replication from target to source based on wards of the specific department
design_id = (replication_settings["source"]["host"]).replace('.','')

design_doc = {
    "filters": {
        f"ward_filter_{design_id}": f"function(doc, req) {{ var wards = {json.dumps(wards)}; return wards.includes(doc.ward); }}"
    }
}

create_design_doc_cmd = [
    'curl', '-d', json.dumps(design_doc), '-H', 'Content-Type: application/json',
    '-X', 'PUT', f"{target_url}/_design/ward_filter_{design_id}"
]
try:
    result = subprocess.run(create_design_doc_cmd, check=True, capture_output=True, text=True)
    with open(log_file, 'a') as log:
        log.write(f"{datetime.datetime.now()} - Design document created successfully on the target database\n")
        logging.info(f"Design document created successfully on the target database")

except subprocess.CalledProcessError as e:
    with open(log_file, 'a') as log:
        log.write(f"{datetime.datetime.now()} - Error creating design document: {e.stderr}\n")
        logging.error(f"Error creating design document: {e.stderr}")

def execute_replication(command, log_message):
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        with open(log_file, 'a') as log:
            log.write(f"{datetime.datetime.now()} - {log_message}:\n")
            logging.info(log_message)
    except subprocess.CalledProcessError as e:
        with open(log_file, 'a') as log:
            log.write(f"{datetime.datetime.now()} - Error: {log_message}\n{e.stderr}\n")
            logging.error(f"Error: {log_message}\n{e.stderr}")

source_to_target_cmd = [
    'curl', '-d', json.dumps({
        "_id": "base-source-to-target",
        "source": source_url,
        "target": target_url,
        "create_target": True,
        "continuous": True
    }), '-H', 'Content-Type: application/json', '-X', 'POST', replicator_db_url
]

target_to_source_cmd =[
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

# if suffix is "" use "primary"
    execute_replication(source_to_target_cmd, f"{datetime.datetime.now()} - Replication setup from source to target for {suffix if suffix else 'primary'}")
    execute_replication(target_to_source_cmd_ltp, f"{datetime.datetime.now()} - Replication setup from target to source for {suffix if suffix else 'primary'}")
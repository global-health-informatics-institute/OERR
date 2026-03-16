import json
import subprocess
import datetime
import sys
import logging

# CONFIGS
logging.basicConfig(level=logging.INFO)

replications_file = "config/replications.config"
archive_file = "config/archive.config"
ward_file = "config/department.config"
log_file = "logs/restart_replication.log"

with open(replications_file) as json_file:
    replication_settings = json.load(json_file)

with open(archive_file) as json_file:
    archive_settings = json.load(json_file)

with open(ward_file) as json_file:
    wards_data = json.load(json_file)

department_name = replication_settings["specific_department"]["department"]
wards = []
for department in wards_data["departments"]:
    if department["name"] == department_name:
        wards = department["wards"]
        break


# URL, PARAMS & TARGETS

source_pass = replication_settings['source']['passwd']
source_user = replication_settings['source']['user']
source_host = replication_settings['source']['host']
source_port = replication_settings['source']['port']
source_base_db = replication_settings['source_base_db']['database']

target_pass = replication_settings['target']['password']
target_user = replication_settings['target']['user']
target_host = replication_settings['target']['host']
target_port = replication_settings['target']['port']
target_base_db = replication_settings['target_base_db']['database']

source_url = f"http://{source_user}:{source_pass}@{source_host}:{source_port}/{source_base_db}"
target_url = f"http://{target_user}:{target_pass}@{target_host}:{target_port}/{target_base_db}"
replicator_db_url = f"http://{source_user}:{source_pass}@{source_host}:{source_port}/_replicator"

design_id = (source_host).replace('.','')
sub_directories = ["_lab_test_panels", "_lab_test_type", "_patients", "_users"]

# COMMANDS
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

# REPLICATION WINDOW
def _check_replication_window():
    now = datetime.datetime.now()

    START_HOUR = archive_settings["archive_window"]["start_hour"] | 1
    START_MINUTE = archive_settings["archive_window"]["start_minute"] | 0
    START_SECOND = archive_settings["archive_window"]["start_second"] | 0
    START_MICROSECOND = archive_settings["archive_window"]["start_microsecond"] | 0

    END_HOUR = archive_settings["archive_window"]["end_hour"] | 3
    END_MINUTE = archive_settings["archive_window"]["end_minute"] | 0
    END_SECOND = archive_settings["archive_window"]["end_second"]   | 0
    END_MICROSECOND = archive_settings["archive_window"]["end_microsecond"] | 0

    start_time = now.replace(hour=START_HOUR, minute=START_MINUTE, second=START_SECOND, microsecond=START_MICROSECOND)
    end_time = now.replace(hour=END_HOUR, minute=END_MINUTE, second=END_SECOND, microsecond=END_MICROSECOND)

    if start_time <= now  <= end_time:
        with open(log_file, 'a') as log:
            log.write(f"{datetime.datetime.now()} - Replication skipped at {now} as it is within the threshhold time window.\n")
            logging.info(f"{now} : as it is within the threshhold time window.")
        sys.exit(0)

def _clear_log_file():
    try:
        with open(log_file, "r") as f:
            lines = f.readlines()

        if len(lines) > 51:
            with open(log_file, "w") as f:
                f.write(f"{datetime.datetime.now()} - Log file rotated (50+)\n")

    except FileNotFoundError:
        with open(log_file, "w") as f:
            f.write(f"{datetime.datetime.now()} - Log file created\n")

def _delete_replicator_db():
    delete_replicator_db_cmd = ['curl', '-X', 'DELETE', replicator_db_url]
    try:
        subprocess.run(delete_replicator_db_cmd, check=True, capture_output=True, text=True)
        logging.info(f"Deleting _replicator database if it exists...")
        with open(log_file, 'a') as log:
            log.write(f"{datetime.datetime.now()} - Deleting _replicator database if it exists...\n")
    except subprocess.CalledProcessError as e:
        with open(log_file, 'a') as log:
            log.write(f"{datetime.datetime.now()} - Error deleting _replicator database: {e.stderr}\n")

def _create_replicator_db():
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

def _create_target_design_doc():
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
        subprocess.run(create_design_doc_cmd, check=True, capture_output=True, text=True)
        with open(log_file, 'a') as log:
            log.write(f"{datetime.datetime.now()} - Design document created successfully on the target database\n")
            logging.info(f"Design document created successfully on the target database")

    except subprocess.CalledProcessError as e:
        with open(log_file, 'a') as log:
            log.write(f"{datetime.datetime.now()} - Error creating design document: {e.stderr}\n")
            logging.error(f"Error creating design document: {e.stderr}")

def _create_replication(command,log_message):
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        with open(log_file, 'a') as log:
            log.write(f"{datetime.datetime.now()} - {log_message}:\n")
            logging.info(log_message)
    except subprocess.CalledProcessError as e:
        with open(log_file, 'a') as log:
            log.write(f"{datetime.datetime.now()} - Error: {log_message}\n{e.stderr}\n")
            logging.error(f"Error: {log_message}\n{e.stderr}")

def _create_replication_on_subdirs():
    for suffix in sub_directories:
        source_suffix_url = f"{suffix}"
        target_suffix_url = f"{suffix}"
        
        idx_source_url = f"{source_url}{source_suffix_url}"
        idx_target_url = f"{target_url}{target_suffix_url}"

        idx_source_to_target_cmd = [
            'curl', '-d', json.dumps({
                "_id": f"base-source-to-target{suffix}",
                "source": idx_source_url,
                "target": idx_target_url,
                "create_target": True,
                "continuous": True
            }), '-H', 'Content-Type: application/json', '-X', 'POST', replicator_db_url
        ]
        
        idx_target_to_source_cmd = [
            'curl', '-d', json.dumps({
                "_id": f"base-target-to-source{suffix}",
                "source": idx_target_url,
                "target": idx_source_url,
                "create_target": True,
                "continuous": True,
            }), '-H', 'Content-Type: application/json', '-X', 'POST', replicator_db_url
        ]

        _create_replication(
            idx_source_to_target_cmd,
            f"{datetime.datetime.now()} - Replication setup: source to target for {suffix if suffix else 'primary'}"
        )

        _create_replication(
            idx_target_to_source_cmd,
            f"{datetime.datetime.now()} - Replication setup: target to source for {suffix if suffix else 'primary'}"
        )

# RESTART REPLICATION 
_check_replication_window()
_clear_log_file()
_delete_replicator_db()
_create_replicator_db()
_create_target_design_doc()
_create_replication(
    source_to_target_cmd,
    "Setting up replication from source to target"
)
_create_replication(
    target_to_source_cmd,
    "Setting up replication from target to source"
)
_create_replication_on_subdirs()
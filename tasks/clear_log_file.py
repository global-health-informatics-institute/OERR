import time
import logging

log_file = "logs/synchronization.log"
log_file2 = "logs/replication_errors.log"
log_file3 = "logs/replication_restarts.log"
error_log = "logs/all_errors.log"


logging.basicConfig(filename=error_log, level=logging.ERROR,
                    format='%(asctime)s %(message)s')

def clear_log_file(file_path, file_path2, file_path3):
    """Clear the content of the given log files."""
    try:
        with open(file_path, 'w') as f:
            pass  #
        with open(file_path2, 'w') as f:
            pass
        with open(file_path3, 'w') as f:
            pass
        print(f"Cleared content of {file_path} + {file_path2} + {file_path3}")
    except FileNotFoundError as e:
        print(f"File {file_path} or {file_path2} or {file_path3} not found.")
        logging.error(f"File not found: {e}")
    except Exception as e:
        logging.error(f"Error while clearing logs: {e}")


try:
    while True:
        clear_log_file(log_file, log_file2, log_file3)
        time.sleep(43200)  # half a day
except KeyboardInterrupt:
    print("Stopping the log clearing process...")
except Exception as e:
    logging.error(f"Unexpected error: {e}")

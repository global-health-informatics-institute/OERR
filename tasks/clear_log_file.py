import os
log_file = "logs/synchronization.log"
log_file2 = "logs/replication_errors.log"
def clear_log_file(file_path, file_path2):

    try:
        with open(file_path, 'w') as f:
            pass
        with open(file_path2, 'w') as f:
            pass
        print(f"Cleared content of {file_path} + {file_path2}")
    except FileNotFoundError:
        print(f"File {file_path}, {file_path2} not found.")

if __name__ == "__main__":
    clear_log_file(log_file,log_file2 )
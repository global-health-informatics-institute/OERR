import os
log_file = "synchronization.log"
def clear_log_file(file_path):

    try:
        with open(file_path, 'w') as f:
            pass
        print(f"Cleared content of {file_path}")
    except FileNotFoundError:
        print(f"File {file_path} not found.")

if __name__ == "__main__":
    clear_log_file("synchronization.log")
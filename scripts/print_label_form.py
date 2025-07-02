'''
Modified by Ruth Chirwa

This script is to present estimated ages for all departments on the label form 
'''

import re
import os
import time
from datetime import datetime
from pathlib import Path
from config import PrinterConfiguration
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

LABEL_PRINTER_FILE_EXTENSION_PATTERN = r"\.(zpl|lbl)$"

class LabelPrinterHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.config = PrinterConfiguration().read()

    def get_receipt(self, file):
        self.update_lbl_with_dynamic_age(file)

        if "##########BEGIN FORM##########" in file:
            receipt = file.split("##########BEGIN FORM##########")[0]
            return receipt.strip()
        else:
            return file
   
     #for all departments to have estimated age
    def get_estimated_age(self, dob_str):
        try:
            dob = datetime.strptime(dob_str.strip(), "%d-%b-%Y")
            today = datetime.today()
            days = (today - dob).days 

            if dob > today:
                return "Invalid Patient DOB"

            delta = today - dob
            days = delta.days

            if days < 30:
                if days < 7:
                    return f"{days} day{'s' if days != 1 else ''} old"
                elif days % 7 == 0:
                    weeks = days // 7
                    return f"{weeks} week{'s' if weeks != 1 else ''} old"
                else:
                    return f"{days} days old"

            
            elif days < 365:
                months = days // 30
                return f"{months} month{'s' if months != 1 else ''} old"

            
            else:
                years = days // 365
                return f"{years} year{'s' if years != 1 else ''} old"

        except ValueError:
            print(f"Invalid Patient DOB format: {dob_str}. Expected format is 'DD-MMM-YYYY'.")
            return "Invalid Patient DOB"
        
    def update_lbl_with_dynamic_age(self, file):
        try:
            with open(file, "r") as f:
                lines = f.readlines()

            updated_lines = []
            dob_y = None
            age = None
            dob_raw = None
            est_age_line_index = None
            est_age_y = None
            shift_offset = 40
            separator_y = None

            # First pass: Find Patient DOB, Est. Age, and check separator Y (dotted line) if it exists
            for idx, line in enumerate(lines):
                if "Patient DOB:" in line and dob_y is None:
                    try:
                        parts = line.split(",")
                        dob_y = int(parts[1])
                        dob_raw = line.split("DOB:")[1].split("(")[0].strip().replace('"', '')
                        age = self.get_estimated_age(dob_raw)
                    except Exception as e:
                        print("Error parsing Patient DOB:", e)
                elif "Est. Age" in line:
                    est_age_line_index = idx
                    try:
                        est_age_y = int(line.split(",")[1])
                    except:
                        est_age_y = None
                elif "--------------------------------------------------------" in line:
                    try:
                        separator_y = int(line.split(",")[1])
                    except:
                        separator_y = None

            if dob_y is None or age is None:
                print("❌ Patient DOB not found and age could not be calculated.")
                return

            # If Est. Age line exists, age should be updated
            if est_age_line_index is not None:
                for i, line in enumerate(lines):
                    if i == est_age_line_index:
                        updated_line = f'A30,{est_age_y},0,4,1,1,N,"Est. Age   : {age}"\n'
                        updated_lines.append(updated_line)
                    else:
                        updated_lines.append(line)
                print("✅ Estimated Age has been updated")

            # If Est. Age line doesn't exist: insert it and shift lines below
            else:
                age_line_y = dob_y + shift_offset
                for line in lines:
                    # Patient DOB line
                    if "Patient DOB:" in line:
                        cleaned_dob = f'A30,{dob_y},0,4,1,1,N,"Patient DOB: {dob_raw}"\n'
                        updated_lines.append(cleaned_dob)
                        # Insert new Est. Age line just after Patient DOB
                        est_line = f'A30,{age_line_y},0,4,1,1,N,"Est. Age   : {age}"\n'
                        updated_lines.append(est_line)
                    elif line.startswith("A"):
                        try:
                            parts = line.split(",")
                            y_val = int(parts[1])
                            if y_val >= age_line_y:
                                # Shift once, only when Est. Age is not present
                                new_y = y_val + shift_offset
                                line = line.replace(f",{y_val},", f",{new_y},", 1)
                        except:
                            pass
                        updated_lines.append(line)
                    else:
                        updated_lines.append(line)
                print("✅ Est. Age inserted and lines below shifted.")

            with open(file, "w") as f:
                f.writelines(updated_lines)

        except FileNotFoundError:
            print("❌ File not found.")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


    def get_report(self, file):
        if "##########BEGIN FORM##########" in file:
            report = file.split("##########BEGIN FORM##########")[1]
            return report.strip()
        else:
            return "No delimiter found in file."
            

    def delete_file(self, file_path):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"{file_path} has been deleted.")
            except Exception as e:
                print(f"An error occurred while deleting {file_path}: {str(e)}")
        else:
            print(f"{file_path} does not exist.")

    def on_modified(self, event):
        if re.search(LABEL_PRINTER_FILE_EXTENSION_PATTERN, event.src_path):
            receipt = self.get_receipt(open(event.src_path).read())
            report = self.get_report(open(event.src_path).read())
            receipt_command = f"echo '{receipt}' > {self.config.get('DEFAULT', 'printer_1')}"
            report_command = f"echo '{report}' > {self.config.get('DEFAULT', 'printer_2')}"
        
            os.system(receipt_command)
            os.system(report_command)
            if self.config.getboolean('DEFAULT', 'delete_files', fallback=False):
                self.delete_file(event.src_path)



if __name__ == '__main__':
    
    print("✨️ Starting Label Printer Tracker Service")

# Create an instance of the class 
printhandler = LabelPrinterHandler()

# Process existing .lbl files in the Downloads directory
downloads_dir = Path.home() / "Downloads"
lbl_files = downloads_dir.glob("*.lbl")
for lbl_file in lbl_files:
    printhandler.get_receipt(str(lbl_file))
 

# Set up directory monitoring
folder_config_path = printhandler.config.get('DEFAULT', 'file_directory', fallback='Downloads')
target_directory = os.path.join(os.path.expanduser("~"), folder_config_path)

if not os.path.exists(target_directory):
    raise NameError(f"❌ Target directory {target_directory} does not exist!")

obs = Observer()
obs.schedule(printhandler, path=target_directory, recursive=False)
obs.start()

print(f"👀️ Monitoring directory: {target_directory}")

try:
    while 1:
        time.sleep(1)
except KeyboardInterrupt:
    print("✅️ Exiting Label Printer Tracker")
finally:
    obs.stop()
    obs.join()

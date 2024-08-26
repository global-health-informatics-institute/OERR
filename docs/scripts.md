# Script Documentation

## Table of Contents

- [Script Documentation](#script-documentation)
  - [Table of Contents](#table-of-contents)
  - [Tree](#tree)
  - [add\_pbf\_test](#add_pbf_test)
    - [Key Points:](#key-points)
  - [battery\_test](#battery_test)
    - [Key Points:](#key-points-1)
  - [check\_ip](#check_ip)
    - [Key Points:](#key-points-2)
  - [initialize](#initialize)
    - [Key Points:](#key-points-3)
  - [load\_dump](#load_dump)
    - [Key Points:](#key-points-4)
  - [local\_cleen\_up](#local_cleen_up)
  - [panels](#panels)
  - [purge](#purge)

---

## Tree

```bash
.
├── add_pbf_test.py
├── battery_test.py
├── check_ip.py
├── initialize.py
├── __init__.py
├── load_dump.py
├── local_clean_up.py
├── panels.py
├── purge.py
├── refactor_db.py
├── synchronizer.py
├── tests.json
└── undo_false_reviews.py
```

---

## add_pbf_test

This script adds a new laboratory test, "Manual Differential & Cell Morphology," to the system. It defines the specimen requirements, test details, and saves them to the database. Additionally, it creates a new test panel, "PBF," which includes this test and another test, "FBC." The panel is then saved to the database.

### Key Points:
- **LaboratoryTestType:** Handles test definitions, including specimen requirements and test measures.
- **LaboratoryTestPanel:** Defines a panel that groups multiple tests together.
- **Database Operations:** The script checks if the test exists, updates it if it does, or creates it if it doesn't, then saves everything to the database.

---

## battery_test

This script monitors the system's battery voltage and logs the information or triggers actions based on the voltage level. If the voltage drops below a certain threshold, it shuts down the system. It also generates and prints a label with the voltage details.

### Key Points:
- **Voltage Monitoring:** Continuously checks the battery voltage using the `CheckVoltage` utility.
- **Logging:** Writes the voltage data to a log file.
- **Shutdown Trigger:** If the voltage is too low, the system is shut down to prevent damage.
- **Label Printing:** Prints a label with the current voltage and percentage using a predefined format.

---

## check_ip

This script is responsible for managing CouchDB replication settings based on the IP address of the system. It deletes and recreates replication settings, ensuring the system's CouchDB instances replicate data correctly.

### Key Points:
- **CouchDB Connection:** Establishes a connection to the CouchDB server using credentials from a config file.
- **IP Address Handling:** Generates the IP address for replication.
- **Replication Setup:** Configures replication between local and remote databases using `curl` commands.

---

## initialize

This script initializes the data needed to run the application. It sets up databases, loads test types and panels, creates default users, and initializes CouchDB views.

### Key Points:
- **Database Initialization:** Creates and connects to the necessary databases in CouchDB.
- **Test Initialization:** Loads and saves test types and panels from CSV and JSON files.
- **User Creation:** Creates a default admin user if none exists.
- **View Initialization:** Sets up CouchDB views for efficient data querying.

---

## load_dump

This script restores data from a JSON dump into the CouchDB database. It reads the data from `db.json` and saves each record to the database.

### Key Points:
- **Database Restoration:** Handles the restoration of database records from a JSON dump.
- **Data Handling:** Removes the `_rev` field from documents to avoid conflicts during the restore process.

---

## local_cleen_up

- **Purpose**:  
  Archives patient records based on certain conditions, such as the age of the records.

- **Functionality**:  
  - Fetches patient records from the database.
  - Checks if any recent tests have been ordered for each patient.
  - Archives records by saving them to a JSON file and purging them from the database.

- **Key Points**:  
  - Designed to maintain database efficiency by archiving older, unused records.
  - The cutoff for archiving is set to 8 days since the last test order.

---

## panels

- **Purpose**:  
  Initializes and saves laboratory test panels to the database based on data from a CSV file.

- **Functionality**:  
  - Connects to CouchDB and creates test panels from `test_panels.csv`.
  - Assigns specimen types and tests to each panel.
  - Saves the panels to the database.

- **Key Points**:  
  - Handles CSV file parsing and database interactions.
  - Includes logic to mark panels as non-orderable based on CSV data.

---

## purge

- **Purpose**:  
  Purges non-patient records from the database, specifically targeting older data to free up space.

- **Functionality**:  
  - Connects to the specified CouchDB database.
  - Selects and purges records that are not of the "patient" type.

- **Key Points**:  
  - Focuses on cleaning up non-essential records.
  - Uses the `purge` method to permanently delete records from the database.
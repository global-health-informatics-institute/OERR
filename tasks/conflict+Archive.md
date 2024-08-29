
#### **1. CodeA: Database Initialization and Connection Setup**
   - **Purpose:** Establish connections to the CouchDB server and ensure the necessary databases are set up.
   - **Tasks:**
     - **Connect to CouchDB:** You'll initiate a connection to the CouchDB server using the provided credentials (`admin:root@localhost:5984`).
     - **Check Database Existence:** For each required database (`oerr`, `oerr_archived`, `oerr_pending`, `oerr_replica`), check if it exists. If not, create it.
   - **Outputs:** 
     - Established connections to all required databases.
     - Ready-to-use database references for subsequent operations.

#### **2. CodeB: Data Retrieval and Identification**
   - **Purpose:** Retrieve patient records and their test data from the main `oerr` database and categorize them based on their age.
   - **Tasks:**
     - **Fetch Patient IDs:** Retrieve a batch of patient IDs (9000 at a time) from the `oerr` database.
     - **Retrieve Test Records:** For each patient ID, fetch associated test records from the `oerr` database.
     - **Identify Old Records:** Classify records older than 8 days as "old" and others as "new" based on the `date_ordered` field.
       - Example: `"date_ordered": 1724675256`
   - **Outputs:**
     - **List of Records to Archive:** All records older than 8 days to be moved to the `oerr_archived` database.
     - **List of Active Records:** Records less than 8 days old to be kept active.

#### **3. CodeC: Archiving Old Data**
   - **Purpose:** Move old records to the `oerr_archived` database, with error handling to manage failed operations.
   - **Tasks:**
     - **Archive Old Records:** Transfer records older than 8 days to the `oerr_archived` database.
     - **Handle Failures:** If archiving fails, move these records to the `oerr_pending` database, tagging them with `"target": "archive"`.
   - **Outputs:**
     - **Successful Archive:** Data is safely archived in the `oerr_archived` database.
     - **Pending Records:** Any failures are logged in the `oerr_pending` database for later review.

#### **4. CodeD: Migrate New Records**
   - **Purpose:** Save newer records in the `oerr_replica` database while handling duplicates and failures.
   - **Tasks:**
     - **Save New Records:** Transfer newer records (less than 8 days old) to the `oerr_replica` database.
     - **Check for Duplicates:** Before saving, check for existing records with the same ID to prevent duplication.
       - **Handle Duplicates:** If a duplicate is found, move the record to `oerr_pending` with `"target":"duplicate"`.
     - **Handle Failures:** If the migration fails for any reason, move the record to `oerr_pending` with `"target":"active"`.
   - **Outputs:**
     - **Replica Database:** Newer records are saved in the `oerr_replica` database.
     - **Pending Records:** Any records that failed to migrate or were duplicates are moved to the `oerr_pending` database.

#### **5. CodeE: Database Cleanup, Replication, and Conflict Resolution**
   - **Purpose:** Prepare the main `oerr` database for new data, handle replication, and resolve conflicts.
   - **Tasks:**
     - **Drop Old `oerr`:** Delete the existing `oerr` database.
     - **Create New `oerr`:** Recreate the `oerr` database to receive the replicated data.
     - **Replicate Data:** Copy everything from `oerr_replica` to the newly created `oerr` database.
       - **Handle Conflicts:** If a conflict occurs during replication, resolve it by selecting a "winning" revision.
       - **Manage Pending Records:** Process the `oerr_pending` database:
         - **Archive Pending:** If labeled `"target": "archive"`, move to `oerr_archived`.
         - **Active Pending:** If labeled `"target": "active"`, move to `oerr`.
         - **Keep Duplicates:** Leave duplicates in `oerr_pending` for further review.
   - **Outputs:**
     - **Updated `oerr`:** The main database is updated with conflict-free, replicated data.
     - **Processed Pending Records:** Pending records are managed and moved to their appropriate databases.

#### **6. CodeF: PURGE**
   - **Purpose:** Final cleanup to ensure that only the necessary databases remain.
   - **Tasks:**
     - **Delete `oerr_replica`:** Remove the replica database after successful replication.
     - **Delete `oerr_pending`:** Remove the pending database, assuming all records have been handled.
   - **Outputs:** 
     - **Clean Database Environment:** The main database (`oerr`) is updated, and unnecessary databases (`oerr_replica`, `oerr_pending`) are removed.

- [Tree](#tree)
- [Archive Script](#archive-script)
  - [Code A: `initialize_setup()`](#code-a-initialize_setup)
  - [Code B: `fetch_entries(batch_size=9000)`](#code-b-fetch_entriesbatch_size9000)
  - [Code C: `filter_entries()`](#code-c-filter_entries)
  - [Code D: `save_active_entries()`](#code-d-save_active_entries)
  - [Code E: `house_keeping_please(db_name)`](#code-e-house_keeping_pleasedb_name)
  - [Code F: `exodus()`](#code-f-exodus)
  - [Script Workflow](#script-workflow)
  - [Execution](#execution)
- [Resolve Conflicts](#resolve-conflicts)
  - [Logging Configuration](#logging-configuration)
  - [`read1(id)`](#read1id)
  - [`resolve_conflicts()`](#resolve_conflicts)
  - [Main Execution Block](#main-execution-block)
  - [Script Workflow](#script-workflow-1)

## Tree
```bash
.
├── archive.py
├── config.py
├── __init__.py
└── resolve_conflicts.py

```

## Archive Script
### Code A: `initialize_setup()`
- **Purpose**: Initializes the required databases.
- **Details**: 
  - It ensures that two databases, `oerr` and `oerr_active`, exist.
  - Uses the `ensure_database_exists()` helper function to create these databases if they do not already exist.

### Code B: `fetch_entries(batch_size=9000)`
- **Purpose**: Fetches documents from the `oerr` database in batches.
- **Details**: 
  - It retrieves documents from the `oerr` database in bulks of up to 9000 documents.
    - why 9000, implementation by Timo but i suggest it was a good approach for compaseting for network, memory and performance
  - Handles pagination by keeping track of the last document fetched to continue fetching the next batch until all documents are retrieved.

### Code C: `filter_entries()`
- **Purpose**: Filters documents based on the `date_ordered` field.
- **Details**: ## Archive Script

  - It processes the documents fetched by `fetch_entries()`.
  - Filters out documents where `date_ordered` is within the last 8 days.
  - Returns the filtered list of "active" documents.

### Code D: `save_active_entries()`
- **Purpose**: Saves filtered documents to the `oerr_active` database.
- **Details**: 
  - Calls `filter_entries()` to get active documents.
  - Removes the `_rev` field from each document (to avoid conflicts) before saving.
  - Saves each active document to the `oerr_active` database using HTTP PUT requests.

### Code E: `house_keeping_please(db_name)`
- **Purpose**: Deletes a specified database.
- **Details**: 
  - Deletes the provided database (`db_name`) from CouchDB.
  - Used for cleaning up old databases to maintain a clean environment.

### Code F: `exodus()`
- **Purpose**: Migrates documents from `oerr_active` to `oerr`.
- **Details**: 
  - Fetches all documents from the `oerr_active` database in batches.
  - Removes the `_rev` field from each document to ensure a clean save.
  - Saves each document to the `oerr` database.
  - Ensures that `oerr` starts with only the active, cleaned documents after housekeeping.

### Script Workflow

1. **Initialize**: The script begins by ensuring the required databases exist (`oerr` and `oerr_active`).
2. **Filter and Save**: It fetches, filters, and saves documents based on the `date_ordered` field, storing recent entries in `oerr_active`.
3. **Housekeeping**: The `oerr` database is deleted to clean up old data.
4. **Migration**: Active documents are migrated back to a fresh `oerr` database from `oerr_active`.
5. **Cleanup**: Finally, the `oerr_active` database is deleted.

### Execution
- **Main Function**: The script's main block (`__main__`) runs the entire workflow in sequence, starting with database initialization and ending with the final cleanup.

- [archive script](../tasks/archive.py)

---
---


## Resolve Conflicts
### Logging Configuration
- **Purpose**: Sets up logging to monitor script activity.
- **Details**: 
  - Configures the logging level to `INFO` and initializes a logger named `__name__`.
  - This ensures that all key actions and errors are recorded.

### `read1(id)`
- **Purpose**: Reads a document from the CouchDB, including all its conflicting revisions.
- **Details**: 
  - Attempts to fetch a document by its `ID` up to 5 times if there are issues.
  - If conflicts are found, it retrieves all conflicting revisions.
  - Returns a list of document revisions (including the main document and its conflicting versions).
  - Logs information about conflicts and any retry attempts.

### `resolve_conflicts()`
- **Purpose**: Resolves conflicts by selecting the most recent revision of each conflicted document.
- **Details**: 
  - Starts by fetching all documents that may have conflicts.
  - Filters out documents that actually have conflicts.
  - For each conflicted document:
    - Calls `read1()` to retrieve all conflicting revisions.
    - Selects the latest revision based on the `_rev` field.
    - Updates the document in the database with the selected revision.
  - Logs the progress and results of the conflict resolution process.

### Main Execution Block
- **Purpose**: Initiates the conflict resolution process.
- **Details**: 
  - The `resolve_conflicts()` function is called when the script is executed as the main program.

### Script Workflow

1. **Conflict Detection**: The script starts by detecting any documents in the database that have conflicting revisions.
2. **Conflict Resolution**: For each document with conflicts:
   - The script retrieves all conflicting versions.
   - It selects the most recent version based on the revision ID.
   - Updates the document in the database with the chosen revision.
3. **Logging**: Throughout the process, the script logs key actions, including conflict detection, document processing, and any errors encountered.

- [Resolve Conflicts](../tasks/resolve_conflicts.py)

---
---
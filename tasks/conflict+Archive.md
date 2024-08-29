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
- **Details**: 
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

## Script Workflow

1. **Initialize**: The script begins by ensuring the required databases exist (`oerr` and `oerr_active`).
2. **Filter and Save**: It fetches, filters, and saves documents based on the `date_ordered` field, storing recent entries in `oerr_active`.
3. **Housekeeping**: The `oerr` database is deleted to clean up old data.
4. **Migration**: Active documents are migrated back to a fresh `oerr` database from `oerr_active`.
5. **Cleanup**: Finally, the `oerr_active` database is deleted.

## Execution
- **Main Function**: The script's main block (`__main__`) runs the entire workflow in sequence, starting with database initialization and ending with the final cleanup.

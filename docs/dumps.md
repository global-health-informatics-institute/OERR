## Tree
```bash
.
├── archived_records.json
├── couch_db.json
├── lab_test_panels.json
├── lab_test_type.json
├── patients.json
├── records.json
├── remaining_dumps.py
├── tests_dump.json
├── test_upload.py
└── users.json
```

- The tests_dump.json and the rest of the json files have different formats
- Run [test_upload](../dumps/test_upload.py) to load the tests dump
  - do not edit only the database configuration within the script
- Run the [remaining_dumps](../dumps/remaining_dumps.py) for all remaining dumps
  - Requires configuration of the file path and specified database configurations on each json file being uploaded
  - 
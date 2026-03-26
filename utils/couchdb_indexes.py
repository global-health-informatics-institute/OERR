import requests
from requests.auth import HTTPBasicAuth


def find_with_index(db, query, index_name=None):
    # Deprecated: prefer adding "use_index" directly to Mango queries.
    if not index_name:
        return db.find(query)
    indexed_query = dict(query)
    indexed_query["use_index"] = index_name
    try:
        return db.find(indexed_query)
    except Exception:
        return db.find(query)


def _build_index_payload(idx_name, index_def):
    idx_name = _normalize_index_name(idx_name)
    payload = {
        "index": {"fields": index_def["fields"]},
        "name": idx_name,
        "ddoc": idx_name,
        "type": "json",
    }
    if index_def.get("partial_filter_selector"):
        payload["partial_filter_selector"] = index_def["partial_filter_selector"]
    return payload


def _normalize_index_name(idx_name):
    return idx_name if idx_name.startswith("idx_") else f"idx_{idx_name}"


def _get_existing_index_names(base_url, db_name, auth, timeout):
    response = requests.get(f"{base_url}/{db_name}/_index", auth=auth, timeout=timeout)
    if response.status_code != 200:
        return set()
    indexes = response.json().get("indexes", [])
    return {idx.get("name") for idx in indexes if idx.get("type") == "json"}


def build_index_helpers(base_url, db_name, auth, existing, timeout=5):
    def check_index(idx_name):
        return _normalize_index_name(idx_name) in existing

    def create_index(idx_name, idx_object):
        payload = _build_index_payload(idx_name, idx_object)
        response = requests.post(
            f"{base_url}/{db_name}/_index",
            json=payload,
            auth=auth,
            timeout=timeout,
        )
        if response.status_code in (200, 201, 202):
            return True
        if "partial_filter_selector" in payload:
            fallback = dict(payload)
            fallback.pop("partial_filter_selector", None)
            response = requests.post(
                f"{base_url}/{db_name}/_index",
                json=fallback,
                auth=auth,
                timeout=timeout,
            )
            return response.status_code in (200, 201, 202)
        return False

    return check_index, create_index


def ensure_indexes(settings, timeout=5):
    couch = settings.get("couch")
    if not couch:
        return False

    base_url = f"http://{couch['host']}:{couch['port']}"
    auth = HTTPBasicAuth(couch["user"], couch["passwd"])
    base_db = couch["database"]

    main_db = base_db
    users_db = f"{base_db}_users"
    patients_db = f"{base_db}_patients"
    lab_test_type_db = f"{base_db}_lab_test_type"
    lab_test_panels_db = f"{base_db}_lab_test_panels"

    partial_tests = {"type": {"$in": ["test", "test panel"]}}

    index_plan = {
        main_db: [
            {
                "name": "idx_orders_by_ward_status_date",
                "fields": ["ward", "status", "date_ordered"],
                "partial_filter_selector": partial_tests,
            },
            {
                "name": "idx_orders_by_ordered_by_status_date",
                "fields": ["ordered_by", "status", "date_ordered"],
                "partial_filter_selector": partial_tests,
            },
            {
                "name": "idx_orders_by_patient_date",
                "fields": ["patient_id", "date_ordered"],
                "partial_filter_selector": partial_tests,
            },
            {
                "name": "idx_orders_by_collection_id",
                "fields": ["collection_id"],
                "partial_filter_selector": partial_tests,
            },
            {
                "name": "idx_orders_by_type_status",
                "fields": ["type", "status"],
                "partial_filter_selector": partial_tests,
            },
        ],
        users_db: [
            {"name": "idx_users_by_role_status", "fields": ["role", "status"]},
            {"name": "idx_users_by_team", "fields": ["team"]},
        ],
        lab_test_type_db: [
            {"name": "idx_lab_test_type_by_test_type_id", "fields": ["test_type_id"]},
            {"name": "idx_lab_test_type_by_availability", "fields": ["availability"]},
        ],
        lab_test_panels_db: [
            {"name": "idx_lab_test_panels_by_availability", "fields": ["availability"]},
        ],
    }

    created_any = False
    for db_name, indexes in index_plan.items():
        try:
            # Ensure database exists
            requests.put(f"{base_url}/{db_name}", auth=auth, timeout=timeout)
            existing = _get_existing_index_names(base_url, db_name, auth, timeout)
            check_index, create_index = build_index_helpers(
                base_url, db_name, auth, existing, timeout=timeout
            )
            for index_def in indexes:
                if check_index(index_def["name"]):
                    continue
                if create_index(index_def["name"], index_def):
                    created_any = True
        except requests.RequestException:
            # If CouchDB is unavailable, skip without crashing the app.
            continue

    return created_any

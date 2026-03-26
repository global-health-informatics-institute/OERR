import logging

import couchdb
import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


def _is_bad_request_error(exc):
    """Return True if *exc* is a CouchDB HTTP 400 bad_request error.

    The couchdb library raises ``ServerError((status, (error, reason)))`` for
    HTTP errors that are not otherwise mapped to a specific exception class.
    A 400 response from the Mango ``_find`` endpoint indicates that the
    ``use_index`` hint refers to an index that does not exist or cannot be
    applied to the given query.
    """
    if not exc.args or not isinstance(exc.args[0], tuple) or len(exc.args[0]) < 2:
        return False
    status, error_detail = exc.args[0]
    error_type = error_detail[0] if isinstance(error_detail, tuple) else None
    return status == 400 and error_type == "bad_request"


def find_with_index(db, query, index_name=None):
    if not index_name:
        return db.find(query)
    indexed_query = dict(query)
    indexed_query["use_index"] = index_name
    try:
        return db.find(indexed_query)
    except couchdb.ServerError as exc:
        # CouchDB returns HTTP 400 (bad_request) when the requested index does
        # not exist or cannot be used for the given query.  Re-raise for any
        # other server error so real problems are not silently swallowed.
        if not _is_bad_request_error(exc):
            raise
        logger.warning(
            "Index '%s' could not be used (bad_request); falling back to unindexed query. Error: %s",
            index_name,
            exc,
        )
        return db.find(query)


def _build_index_payload(index_def):
    payload = {
        "index": {"fields": index_def["fields"]},
        "name": index_def["name"],
        "type": "json",
    }
    if index_def.get("ddoc"):
        payload["ddoc"] = index_def["ddoc"]
    if index_def.get("partial_filter_selector"):
        payload["partial_filter_selector"] = index_def["partial_filter_selector"]
    return payload


def _get_existing_index_names(base_url, db_name, auth, timeout):
    response = requests.get(f"{base_url}/{db_name}/_index", auth=auth, timeout=timeout)
    if response.status_code != 200:
        return set()
    indexes = response.json().get("indexes", [])
    return {idx.get("name") for idx in indexes if idx.get("type") == "json"}


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

            for index_def in indexes:
                if index_def["name"] in existing:
                    continue
                payload = _build_index_payload(index_def)
                response = requests.post(
                    f"{base_url}/{db_name}/_index",
                    json=payload,
                    auth=auth,
                    timeout=timeout,
                )
                if response.status_code in (200, 201, 202):
                    created_any = True
                elif "partial_filter_selector" in payload:
                    fallback = dict(payload)
                    fallback.pop("partial_filter_selector", None)
                    response = requests.post(
                        f"{base_url}/{db_name}/_index",
                        json=fallback,
                        auth=auth,
                        timeout=timeout,
                    )
                    if response.status_code in (200, 201, 202):
                        created_any = True
        except requests.RequestException:
            # If CouchDB is unavailable, skip without crashing the app.
            continue

    return created_any

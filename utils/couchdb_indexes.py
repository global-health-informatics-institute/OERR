import json
import logging
import requests
from requests.auth import HTTPBasicAuth


logger = logging.getLogger(__name__)


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


def _normalize_index_fields(fields):
    normalized = []
    for field in fields or []:
        if isinstance(field, str):
            normalized.append(field)
        elif isinstance(field, dict):
            # CouchDB may return {"field": "asc"} objects; keep field order.
            for key in field.keys():
                normalized.append(key)
        else:
            normalized.append(str(field))
    return normalized


def _normalize_selector(value, parent_key=None):
    if isinstance(value, dict):
        return {k: _normalize_selector(v, k) for k, v in sorted(value.items())}
    if isinstance(value, list):
        items = [_normalize_selector(v, parent_key) for v in value]
        if parent_key in ("$in", "$or", "$and", "$nor"):
            return sorted(items, key=lambda x: json.dumps(x, sort_keys=True, default=str))
        return items
    return value


def _is_partial_rejection(response):
    if response is None:
        return False
    if response.status_code != 400:
        return False
    try:
        data = response.json()
    except ValueError:
        return False
    reason = str(data.get("reason", ""))
    return "partial_filter_selector" in reason


def _fetch_ddoc_indexes(base_url, db_name, ddoc, auth, timeout, log=None):
    if not ddoc:
        return None
    ddoc_short = ddoc.split("/", 1)[1] if ddoc.startswith("_design/") else ddoc
    response = requests.get(
        f"{base_url}/{db_name}/_design/{ddoc_short}",
        auth=auth,
        timeout=timeout,
    )
    if response.status_code != 200:
        if log:
            log.warning(
                "Failed to fetch design doc '%s' in '%s'. Status=%s Body=%s",
                ddoc_short,
                db_name,
                response.status_code,
                response.text,
            )
        return None
    return response.json().get("indexes", {})


def _delete_design_doc(base_url, db_name, ddoc, auth, timeout, log=None):
    if not ddoc:
        return False
    if ddoc.startswith("_design/"):
        ddoc = ddoc.split("/", 1)[1]
    response = requests.get(
        f"{base_url}/{db_name}/_design/{ddoc}",
        auth=auth,
        timeout=timeout,
    )
    if response.status_code == 404:
        return False
    if response.status_code != 200:
        if log:
            log.warning(
                "Failed to fetch design doc '%s' in '%s'. Status=%s Body=%s",
                ddoc,
                db_name,
                response.status_code,
                response.text,
            )
        return False
    rev = response.json().get("_rev")
    if not rev:
        if log:
            log.warning(
                "Design doc '%s' in '%s' missing _rev; cannot delete.",
                ddoc,
                db_name,
            )
        return False
    delete_response = requests.delete(
        f"{base_url}/{db_name}/_design/{ddoc}",
        params={"rev": rev},
        auth=auth,
        timeout=timeout,
    )
    if delete_response.status_code in (200, 202):
        return True
    if log:
        log.warning(
            "Failed to delete design doc '%s' in '%s'. Status=%s Body=%s",
            ddoc,
            db_name,
            delete_response.status_code,
            delete_response.text,
        )
    return False


def _get_existing_indexes(base_url, db_name, auth, timeout):
    response = requests.get(f"{base_url}/{db_name}/_index", auth=auth, timeout=timeout)
    if response.status_code != 200:
        return {}, False
    indexes = response.json().get("indexes", [])
    existing = {}
    ddoc_cache = {}
    for idx in indexes:
        if idx.get("type") != "json":
            continue
        idx_def = idx.get("def", {})
        partial = idx_def.get("partial_filter_selector")
        if partial is None:
            partial = idx.get("partial_filter_selector")
        existing[idx.get("name")] = {
            "fields": _normalize_index_fields(idx_def.get("fields", [])),
            "partial_filter_selector": partial,
            "ddoc": idx.get("ddoc"),
        }
        if existing[idx.get("name")]["partial_filter_selector"] is None:
            ddoc = idx.get("ddoc")
            if ddoc not in ddoc_cache:
                ddoc_cache[ddoc] = _fetch_ddoc_indexes(
                    base_url, db_name, ddoc, auth, timeout, log=logger
                )
            ddoc_indexes = ddoc_cache.get(ddoc) or {}
            ddoc_def = ddoc_indexes.get(idx.get("name"))
            if ddoc_def:
                if not existing[idx.get("name")]["fields"]:
                    existing[idx.get("name")]["fields"] = _normalize_index_fields(
                        ddoc_def.get("index", {}).get("fields", [])
                    )
                existing[idx.get("name")]["partial_filter_selector"] = ddoc_def.get(
                    "partial_filter_selector"
                )
    return existing, True


def _index_matches(existing_info, desired_fields, desired_partial):
    existing_fields = _normalize_index_fields(existing_info.get("fields"))
    desired_fields = _normalize_index_fields(desired_fields)
    existing_partial = _normalize_selector(existing_info.get("partial_filter_selector"))
    desired_partial = _normalize_selector(desired_partial)
    return existing_fields == desired_fields and existing_partial == desired_partial


def _delete_index(base_url, db_name, index_name, index_info, auth, timeout, log=None):
    ddoc = index_info.get("ddoc") or index_name
    candidates = []
    if ddoc:
        if ddoc.startswith("_design/"):
            ddoc_short = ddoc.split("/", 1)[1]
            candidates.append(ddoc_short)
            candidates.append(ddoc)
        else:
            candidates.append(ddoc)
            candidates.append(f"_design/{ddoc}")
    else:
        candidates.append(index_name)

    last_response = None
    for candidate in candidates:
        response = requests.delete(
            f"{base_url}/{db_name}/_index/{candidate}/{index_name}",
            auth=auth,
            timeout=timeout,
        )
        last_response = response
        if response.status_code in (200, 202):
            return True

    # Fallback: delete design doc directly (needed for older CouchDB versions)
    for candidate in candidates:
        if _delete_design_doc(base_url, db_name, candidate, auth, timeout, log=log):
            return True

    if log and last_response is not None:
        log.warning(
            "Failed to delete CouchDB index '%s' in '%s'. Status=%s Body=%s",
            index_name,
            db_name,
            last_response.status_code,
            last_response.text,
        )
    return False


def build_index_helpers(base_url, db_name, auth, existing, timeout=5, log=None):
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
            return True, False
        if "partial_filter_selector" in payload:
            partial_rejected = _is_partial_rejection(response)
            if log:
                log.warning(
                    "Partial index rejected for '%s' in '%s'. Status=%s Body=%s. Retrying without partial filter.",
                    payload.get("name"),
                    db_name,
                    response.status_code,
                    response.text,
                )
            fallback = dict(payload)
            fallback.pop("partial_filter_selector", None)
            response = requests.post(
                f"{base_url}/{db_name}/_index",
                json=fallback,
                auth=auth,
                timeout=timeout,
            )
            if response.status_code in (200, 201, 202):
                if log:
                    log.warning(
                        "Created index '%s' in '%s' without partial filter after rejection.",
                        payload.get("name"),
                        db_name,
                    )
                return True, partial_rejected
            if log:
                log.warning(
                    "Failed to create CouchDB index '%s' in '%s' (fallback). Status=%s Body=%s",
                    payload.get("name"),
                    db_name,
                    response.status_code,
                    response.text,
                )
            return False, partial_rejected
        if log:
            log.warning(
                "Failed to create CouchDB index '%s' in '%s'. Status=%s Body=%s",
                payload.get("name"),
                db_name,
                response.status_code,
                response.text,
            )
        return False, False

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
    lab_test_type_db = f"{base_db}_lab_test_type"
    lab_test_panels_db = f"{base_db}_lab_test_panels"

    partial_supported = not couch.get("disable_partial_indexes", False)
    partial_rejection_logged = False
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
    had_error = False
    for db_name, indexes in index_plan.items():
        try:
            # Ensure database exists
            db_response = requests.put(f"{base_url}/{db_name}", auth=auth, timeout=timeout)
            if db_response.status_code not in (200, 201, 202, 412):
                had_error = True
                logger.warning(
                    "Failed to ensure CouchDB database '%s'. Status=%s Body=%s",
                    db_name,
                    db_response.status_code,
                    db_response.text,
                )
                continue

            existing, ok = _get_existing_indexes(base_url, db_name, auth, timeout)
            if not ok:
                had_error = True
                logger.warning(
                    "Failed to fetch CouchDB indexes for '%s'.",
                    db_name,
                )
                continue
            check_index, create_index = build_index_helpers(
                base_url, db_name, auth, set(existing), timeout=timeout, log=logger
            )
            for index_def in indexes:
                index_name = _normalize_index_name(index_def["name"])
                existing_info = existing.get(index_name)
                desired_partial = index_def.get("partial_filter_selector") if partial_supported else None
                if existing_info and _index_matches(
                    existing_info, index_def["fields"], desired_partial
                ):
                    continue
                if existing_info:
                    logger.warning(
                        "Index drift detected in '%s' for '%s'. Existing fields=%s partial=%s; Desired fields=%s partial=%s",
                        db_name,
                        index_name,
                        existing_info.get("fields"),
                        existing_info.get("partial_filter_selector"),
                        index_def["fields"],
                        desired_partial,
                    )
                    deleted = _delete_index(
                        base_url,
                        db_name,
                        index_name,
                        existing_info,
                        auth,
                        timeout,
                        log=logger,
                    )
                    if not deleted:
                        # Re-check to confirm if index still exists before proceeding.
                        refreshed, ok = _get_existing_indexes(
                            base_url, db_name, auth, timeout
                        )
                        if ok and index_name not in refreshed:
                            logger.warning(
                                "Index '%s' in '%s' was already missing after delete attempt; recreating.",
                                index_name,
                                db_name,
                            )
                        else:
                            had_error = True
                            continue
                effective_def = dict(index_def)
                if not partial_supported:
                    effective_def.pop("partial_filter_selector", None)
                created, partial_rejected = create_index(index_name, effective_def)
                if partial_rejected and partial_supported:
                    partial_supported = False
                    if not partial_rejection_logged:
                        logger.warning(
                            "Partial indexes are not supported by this CouchDB instance. "
                            "Continuing without partial filters. "
                            "Set couch.disable_partial_indexes=true to skip partial attempts."
                        )
                        partial_rejection_logged = True
                if created:
                    created_any = True
                else:
                    had_error = True
        except requests.RequestException:
            # If CouchDB is unavailable, skip without crashing the app.
            had_error = True
            continue

    if had_error:
        return False
    return True if created_any or not had_error else False

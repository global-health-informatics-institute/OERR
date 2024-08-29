import requests
import logging
from config import DB, username, password

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read1(id):
    """Read a document from the database, returning all revisions if there are conflicts."""
    retries = 0
    while retries < 5:
        try:
            logger.info(f"Reading document with ID: {id}")
            response = requests.get(f"{DB}/{id}?conflicts=true", auth=(username, password))
            response.raise_for_status()
            data = response.json()
            if "_conflicts" in data:
                logger.info(f"Conflicts found for document ID: {id}")
                conflicts = data.pop("_conflicts")
                revisions = [data]
                for rev in conflicts:
                    response = requests.get(f"{DB}/{id}?rev={rev}", auth=(username, password))
                    response.raise_for_status()
                    revisions.append(response.json())
                return revisions
            else:
                logger.info(f"No conflicts found for document ID: {id}")
                return [data]
        except requests.exceptions.RequestException as e:
            retries += 1
            logger.warning(f"Retrying {retries}/5 after error: {e}")
    raise Exception("Max retries reached, unable to read document.")

def resolve_conflicts():
    """Resolve conflicts by selecting the last written revision."""
    logger.info("Starting conflict resolution process...")
    response = requests.get(f"{DB}/_all_docs?include_docs=true&conflicts=true", auth=(username, password))
    response.raise_for_status()
    conflicted_docs = response.json().get("rows", [])

    actual_conflicts = [doc for doc in conflicted_docs if "_conflicts" in doc["doc"]]

    if actual_conflicts:
        logger.info(f"Found {len(actual_conflicts)} documents with actual conflicts.")
    else:
        logger.info("No documents with conflicts found.")

    for doc in actual_conflicts:
        doc_id = doc["id"]
        logger.info(f"Processing conflicted document: {doc_id}")

        try:
            # Fetch the current document along with conflicting revisions
            revisions = read1(doc_id)

            # Identify the latest revision (last one in the list)
            winning_revision = max(revisions, key=lambda r: r['_rev'])

            # Prepare the document for update by keeping the winning revision
            data = {
                "_id": doc_id,
                "_rev": winning_revision["_rev"],
                **winning_revision  # Include all fields from the winning revision
            }

            update_response = requests.put(f"{DB}/{doc_id}", json=data, auth=(username, password))
            update_response.raise_for_status()

            if update_response.status_code == 201:
                logger.info(f"Conflict resolved for document: {doc_id}")
            else:
                logger.error(f"Failed to update document: {doc_id} with status code {update_response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error resolving conflict for document {doc_id}: {e}")

    logger.info("Conflict resolution process completed.")

if __name__ == "__main__":
    resolve_conflicts()

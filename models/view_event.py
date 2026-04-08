import time
import uuid

from models.database import DataAccess


class ViewEvent:
    def __init__(self, test_id, test_status, viewed_by, viewed_at=None, _id=None):
        self.database = DataAccess("view_events").db
        self.test_id = test_id
        self.test_status = test_status
        self.viewed_by = viewed_by
        self.viewed_at = int(viewed_at) if viewed_at is not None else int(time.time())
        self._id = _id if _id else f"view_event:{uuid.uuid4()}"

    @staticmethod
    def _is_valid_event_id(event_id):
        if not isinstance(event_id, str) or not event_id.startswith("view_event:"):
            return False

        raw_uuid = event_id.split(":", 1)[1]
        try:
            uuid.UUID(raw_uuid)
            return True
        except (ValueError, TypeError):
            return False

    def validate(self):
        if not self._is_valid_event_id(self._id):
            raise ValueError("_id must be in format 'view_event:<uuid>'")

        if not isinstance(self.test_id, str) or not self.test_id.strip():
            raise ValueError("test_id is required and must be a non-empty string")

        if not isinstance(self.test_status, str) or not self.test_status.strip():
            raise ValueError("test_status is required and must be a non-empty string")

        if not isinstance(self.viewed_by, str) or not self.viewed_by.strip():
            raise ValueError("viewed_by is required and must be a non-empty string")

        if not isinstance(self.viewed_at, int):
            raise ValueError("viewed_at must be an integer unix timestamp in seconds")

    def to_dict(self):
        return {
            "_id": self._id,
            "type": "view_event",
            "test_id": self.test_id,
            "test_status": self.test_status,
            "viewed_by": self.viewed_by,
            "viewed_at": self.viewed_at
        }

    def save(self):
        self.validate()
        self.database.save(self.to_dict())

    @staticmethod
    def from_dict(doc):
        if doc is None:
            return None

        return ViewEvent(
            test_id=doc.get("test_id"),
            test_status=doc.get("test_status"),
            viewed_by=doc.get("viewed_by"),
            viewed_at=doc.get("viewed_at"),
            _id=doc.get("_id")
        )

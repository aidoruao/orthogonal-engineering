import hashlib
import json


def _to_dict(record):
    """Pydantic v1/v2 compatible dict conversion."""
    if hasattr(record, "model_dump"):
        return record.model_dump()
    return record.dict()


def hash_records(records):
    hashed = []
    for record in records:
        d = _to_dict(record)
        serialized = json.dumps(d, sort_keys=True).encode("utf-8")
        digest = hashlib.sha256(serialized).hexdigest()
        hashed.append({"hash": digest, "record": d})
    return hashed


def hash_record(record):
    """Curated API entry point — hash a single record."""
    result = hash_records([record])
    return result[0] if result else None

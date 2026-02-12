from pydantic import BaseModel, ValidationError

class RecordModel(BaseModel):
    data: dict


def validate_records(records):
    validated = []
    for record in records:
        try:
            validated.append(RecordModel(data=record))
        except ValidationError:
            continue
    return validated


def validate_record(record):
    """Curated API entry point — validate a single record."""
    result = validate_records([record])
    return result[0] if result else None

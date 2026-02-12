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

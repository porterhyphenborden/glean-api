from datetime import datetime, tzinfo, timezone
import uuid

from models.events.api import EventRequest, EventType
from models.events.db import EventModel



def generate_test_request(user_id: uuid):
    return {
        "user_id": user_id,
        "event_type": EventType.DIRECT_SEED,
        "crop_name": "tomato",
        "event_date": "2024-05-01T00:00:00.000Z",
        "quantity": 10,
        "units": "each",
        "season": 2024,
    }


def test_valid_api_request():
    user_id = uuid.uuid4()
    request = generate_test_request(user_id)
    request_model = EventRequest(**request)

    expected_request_model = {
        "user_id": user_id,
        "event_type": EventType.DIRECT_SEED,
        "event_date": datetime(2024, 5, 1, 0, 0, tzinfo=timezone.utc),
        "crop_name": "tomato",
        "quantity": 10,
        "units": "each",
        "season": 2024,
        "varieties": []
    }

    assert expected_request_model == request_model.model_dump()


def test_db_model_from_api_request():
    user_id = uuid.uuid4()
    request = generate_test_request(user_id)
    event_request = EventRequest(**request)
    event_db_model = EventModel.from_api_request_model(event_request)

    expected_model = {
        "pk": str(user_id),
        "sk": "event#2024#tomato#2024-05-01#direct_seed",
        "event_type": EventType.DIRECT_SEED.value,
        "crop_name": "tomato",
        "event_date": datetime(2024, 5, 1, tzinfo=timezone.utc),
        "quantity": 10,
        "units": "each",
        "season": 2024,
        "varieties": [],
    }

    assert event_db_model.attribute_values == expected_model

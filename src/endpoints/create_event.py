import json
import jwt

from pydantic import ValidationError

from models.events.api import EventRequest
from models.events.db import EventModel
from models.events.repository import item_exists
from utils.auth import user_is_authorized_for_endpoint
from utils.logger import logger


def handler(event, _):
    """
    Validates POST request for garden events and inserts into database.
    """
    request = json.loads(event.get("body"))
    logger.info(f"Received request: {request}")

    # Check that user is authorized for this request
    path_params = event.get("pathParameters")
    token = event["headers"]["Authorization"].split(" ")[1]

    if not user_is_authorized_for_endpoint(path_params, token):
        response = {
            "message": "Forbidden",
            "details": "User is not authorized to make this request.",
        }
        return {
            "statusCode": 403,
            "body": json.dumps(response)
        }

    # Validate request
    try:
        event_request = EventRequest(**dict(request, user_id=path_params.get("user_id")))
    except ValidationError as exc:
        logger.warning(f"Received an invalid request: {request}")
        response = {
            "message": "Bad request",
            "details": str(exc),
        }
        return {
            "statusCode": 400,
            "body": json.dumps(response)
        }
    
    # Check if item already exists as DynamoDB will just overwrite if it does
    db_model = EventModel.from_api_request_model(event_request)
    if item_exists(db_model):
        response = {
            "message": "Item already exists",
            "details": f"An event for this crop {db_model.crop_name} and date {db_model.event_date} of type {db_model.event_type} already exists for this user.",
        }
        return {
            "statusCode": 409,
            "body": json.dumps(response)
        }

    # Save to table
    try:
        db_model.save()
    except Exception as exc:
        logger.exception(f"Failed to write item to DynamoDB table: {str(exc)}")
        response = {
            "message": "POST request failed unexpectedly",
        }
        return {
            "statusCode": 500,
            "body": json.dumps(response)
        }

    return {
        "statusCode": 201,
        "body": json.dumps({"event_id": db_model.sk})
    }

import json

from models.events.repository import get_events
from utils.auth import user_is_authorized_for_endpoint
from utils.logger import logger


def handler(event, _):
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
    
    user_id = path_params.get("user_id")
    path_params = event.get("pathParameters")
    season = path_params.get("season")
    crop = path_params.get("crop")

    logger.info(f"Fetching events from DynamoDB table for user {user_id}, season {season}, crop {crop}.")
    event_models = get_events(user_id, season, crop)
    events = [
        event.to_api_response()
        for event
        in event_models
    ]

    return {
        "statusCode": 200,
        "body": json.dumps(events)
    }

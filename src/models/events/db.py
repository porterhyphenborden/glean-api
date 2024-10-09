import os
from datetime import date

from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute, NumberAttribute, ListAttribute
from pynamodb.models import Model

from models.events.api import EventType, EventRequest


SORT_KEY_TEMPLATE = "event#{season}#{crop}#{event_date}#{event_type}"


class EventModel(Model):
    """
    A garden event, such as a planting or harvest. Used to iteract with DynamoDB table.
    """
    class Meta:
        table_name = os.getenv("GLEAN_TABLE_NAME")
        region = 'us-east-1'
    pk = UnicodeAttribute(hash_key=True)
    sk = UnicodeAttribute(range_key=True)
    event_type = UnicodeAttribute()
    event_date = UTCDateTimeAttribute()
    crop_name = UnicodeAttribute()
    quantity = NumberAttribute()
    units = UnicodeAttribute()
    season = NumberAttribute()
    varieties = ListAttribute()

    @staticmethod
    def generate_sort_key(season: int, crop_name: str, event_type: EventType, event_date: date) -> str:
        event_date_str = event_date.isoformat().split("T")[0]
        sort_key = SORT_KEY_TEMPLATE.format(
            season=season,
            crop=crop_name,
            event_date=event_date_str,
            event_type=event_type.value,
        )

        return sort_key

    @classmethod
    def from_api_request_model(cls, api_request: EventRequest) -> 'EventModel':
        sort_key = cls.generate_sort_key(
            api_request.season,
            api_request.crop_name,
            api_request.event_type,
            api_request.event_date,
        )
        return cls(
            pk=str(api_request.user_id),
            sk=sort_key,
            event_type=api_request.event_type.value,
            event_date=api_request.event_date,
            crop_name=api_request.crop_name,
            quantity=api_request.quantity,
            units=api_request.units,
            season=api_request.season,
            varieties=api_request.varieties,
        )
    
    def to_api_response(self):
        dict_response = self.attribute_values
        dict_response["event_date"] = dict_response["event_date"].isoformat()
        return dict_response

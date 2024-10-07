from pynamodb.exceptions import DoesNotExist

from models.events.db import EventModel


def item_exists(item: EventModel) -> bool:
    try:
        EventModel.get(item.pk, item.sk)
    except DoesNotExist:
        return False
    
    return True

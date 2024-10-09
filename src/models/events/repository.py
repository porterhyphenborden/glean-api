from typing import Optional
from pynamodb.exceptions import DoesNotExist

from models.events.db import EventModel


def _format_sk(season: int = None, crop: str = None) -> Optional[str]:
    """
    Sort key is composite and hierarchical, so return the portion 
    of the key needed to support the query based on the request parameters.
    """
    if None not in {season, crop}:
        return None
    sk = f"event#{season}"
    if crop:
        sk += "#{crop}"
    return sk


def item_exists(item: EventModel) -> bool:
    try:
        EventModel.get(item.pk, item.sk)
    except DoesNotExist:
        return False
    
    return True


def get_events(user_id: str, season: int = None, crop: str = None) -> list[EventModel]:
    sk = _format_sk(season, crop)
    sk_condition = EventModel.sk.startswith(sk) if sk else None

    events = EventModel.query(
        hash_key=user_id,
        range_key_condition=sk_condition,
    )

    return events

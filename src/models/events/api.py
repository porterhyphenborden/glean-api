from datetime import date, datetime
from enum import Enum
from typing import Any
from typing_extensions import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class EventType(Enum):
    DIRECT_SEED = "direct_seed"
    SEEDLNG_START = "seedling_start"
    TRANSPLANT = "transplant"
    HARVEST = "harvest"


class EventRequest(BaseModel):
    """
    Used to validate incoming API requests.
    """
    user_id: UUID
    event_type: EventType
    event_date: datetime
    crop_name: str
    quantity: int
    units: str
    season: Annotated[int, Field(strict=True, gt=1950, lte=date.today().year)]
    varieties: list = Field(default_factory=list)

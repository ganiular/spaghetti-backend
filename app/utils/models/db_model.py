from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field

from app.utils.models.py_object_id import PyObjectId


class DBModel(BaseModel):
    """
    Mixin class to add common configuration for database models.
    """

    id: PyObjectId = Field(
        default_factory=ObjectId, alias="_id", serialization_alias="id"
    )
    time_created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    time_updated: Optional[datetime] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_by_name=True,
        json_encoders={ObjectId: str},
    )

    def mongo_dump(self):
        data = self.model_dump()
        data["_id"] = data.pop("id")
        return data

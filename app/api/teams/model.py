from pydantic import BaseModel, Field

from app.utils.models.db_model import DBModel
from app.utils.models.py_object_id import PyObjectId
from app.utils.models.types import TrimedStr


class TeamCreateForm(BaseModel):
    name: TrimedStr = Field(..., min_length=2)


class TeamUpdateForm(TeamCreateForm):
    pass


class Team(DBModel):
    name: str
    creator_id: PyObjectId

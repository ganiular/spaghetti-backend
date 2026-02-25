from pydantic import BaseModel

from app.utils.models.db_model import DBModel
from app.utils.models.py_object_id import PyObjectId
from app.utils.models.types import OrderedStrEnum


class TeamCreateForm(BaseModel):
    name: str


class Team(DBModel, TeamCreateForm):
    creator_id: PyObjectId


class TeamMemberRole(OrderedStrEnum):
    CREATOR = "creator"
    ADMIN = "admin"
    MEMBER = "member"


class TeamMember(DBModel):
    team_id: PyObjectId
    member_id: PyObjectId
    role: TeamMemberRole

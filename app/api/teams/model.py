from enum import Enum

from pydantic import BaseModel

from app.utils.models.db_model import DBModel
from app.utils.models.py_object_id import PyObjectId


class TeamCreateForm(BaseModel):
    name: str


class Team(DBModel, TeamCreateForm):
    creator_id: PyObjectId


class TeamMemberRole(str, Enum):
    CREATOR = "creator"
    ADMIN = "admin"
    MEMBER = "member"


class TeamMember(DBModel):
    team_id: PyObjectId
    member_id: PyObjectId
    role: TeamMemberRole

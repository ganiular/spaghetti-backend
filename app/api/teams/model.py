from pydantic import BaseModel, Field

from app.utils.models.db_model import AppBaseModel, DBModel
from app.utils.models.py_object_id import PyObjectId
from app.utils.models.types import OrderedStrEnum, TrimedStr


class TeamCreateForm(BaseModel):
    name: TrimedStr = Field(..., min_length=2)


class Team(DBModel, TeamCreateForm):
    creator_id: PyObjectId


class TeamMemberRole(OrderedStrEnum):
    CREATOR = "creator"
    ADMIN = "admin"
    MEMBER = "member"


class TeamMemberInDB(DBModel):
    team_id: PyObjectId
    member_id: PyObjectId
    role: TeamMemberRole


class TeamMember(AppBaseModel):
    member_id: PyObjectId
    role: TeamMemberRole
    name: str
    email: str


class TeamMemberCollection(BaseModel):
    members: list[TeamMember]

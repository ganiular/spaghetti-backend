from pydantic import BaseModel

from app.utils.models.db_model import AppBaseModel, DBModel
from app.utils.models.py_object_id import PyObjectId
from app.utils.models.types import OrderedStrEnum


class TeamMemberRole(OrderedStrEnum):
    CREATOR = "creator"
    ADMIN = "admin"
    MEMBER = "member"


class TeamMemberUpdatableRole(OrderedStrEnum):
    ADMIN = "admin"
    MEMBER = "member"


class TeamMemberUpdateForm(BaseModel):
    role: TeamMemberUpdatableRole


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

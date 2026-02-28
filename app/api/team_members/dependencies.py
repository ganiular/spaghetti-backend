from typing import Annotated

from fastapi import Depends, HTTPException

from app.api.team_members.model import TeamMemberInDB, TeamMemberRole
from app.api.users.dependency import CurrentUser
from app.database import Database
from app.utils.models.py_object_id import PyObjectId


async def _require_team_role(
    team_id: PyObjectId,
    current_user: CurrentUser,
    min_role: TeamMemberRole,
    db: Database,
) -> TeamMemberInDB:
    member_doc = await db.team_members.find_one(
        {"team_id": team_id, "member_id": current_user.id, "deleted": {"$ne": True}}
    )

    if member_doc:
        member = TeamMemberInDB(**member_doc)
        if member.role >= min_role:
            return member

    raise HTTPException(status_code=403, detail=f"Action requires {min_role} role")


async def _require_team_creator(
    team_id: PyObjectId, current_user: CurrentUser, db: Database
):
    return await _require_team_role(team_id, current_user, TeamMemberRole.CREATOR, db)


async def _require_team_member(
    team_id: PyObjectId, current_user: CurrentUser, db: Database
):
    return await _require_team_role(team_id, current_user, TeamMemberRole.MEMBER, db)


async def _require_team_admin(
    team_id: PyObjectId, current_user: CurrentUser, db: Database
):
    return await _require_team_role(team_id, current_user, TeamMemberRole.ADMIN, db)


CurrentTeamCreator = Annotated[TeamMemberInDB, Depends(_require_team_creator)]
CurrentTeamAdmin = Annotated[TeamMemberInDB, Depends(_require_team_admin)]
CurrentTeamMember = Annotated[TeamMemberInDB, Depends(_require_team_member)]

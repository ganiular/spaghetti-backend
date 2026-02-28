from datetime import datetime, timezone
import re

from fastapi import HTTPException
from pymongo import ReturnDocument

from app.api.team_members.dependencies import CurrentTeamAdmin, CurrentTeamCreator
from app.api.team_members.model import TeamMemberInDB, TeamMemberRole
from app.api.teams.model import (
    Team,
    TeamCreateForm,
    TeamUpdateForm,
)
from app.api.users.dependency import CurrentUser
from app.database import Database
from app.exceptions import InvalidParameterException
from app.utils.models.py_object_id import PyObjectId


class TeamService:
    @staticmethod
    async def create_indexes(db: Database):
        await db.teams.create_index("creator_id")

    @staticmethod
    async def create_team(
        form: TeamCreateForm, creator: CurrentUser, db: Database
    ) -> Team:
        team = Team(creator_id=creator.id, **form.model_dump())

        # Check if user already create same name
        existing = await db.teams.find_one(
            {
                "creator_id": team.creator_id,
                "name": {"$regex": f"^{re.escape(team.name)}$", "$options": "i"},
                "deleted": {"$ne": True},
            }
        )
        if existing:
            raise InvalidParameterException({"name": ["Name already exist"]})

        await db.teams.insert_one(team.mongo_dump())

        # Add self as creator
        team_member = TeamMemberInDB(
            member_id=creator.id, team_id=team.id, role=TeamMemberRole.CREATOR
        )

        await db.team_members.insert_one(team_member.mongo_dump())

        return team

    @staticmethod
    async def my_teams(user: CurrentUser, db: Database) -> list[Team]:
        memberships = db.team_members.find(
            {"member_id": user.id, "deleted": {"$ne": True}}, {"team_id": 1}
        )

        team_ids = [doc["team_id"] async for doc in memberships]

        teams = db.teams.find({"_id": {"$in": team_ids}, "deleted": {"$ne": True}})

        return [Team(**doc) async for doc in teams]

    @staticmethod
    async def update_team(
        team_id: PyObjectId,
        form: TeamUpdateForm,
        db: Database,
        require_admin: CurrentTeamAdmin,
    ) -> Team:
        result = await db.teams.find_one_and_update(
            {"_id": team_id, "deleted": {"$ne": True}},
            {"$set": form.model_dump(exclude_unset=True)},
            return_document=ReturnDocument.AFTER,
        )

        if not result:
            raise HTTPException(404, "Team not found")
        return Team(**result)

    @staticmethod
    async def delete_team(
        team_id: PyObjectId, db: Database, reqiure_creator: CurrentTeamCreator
    ) -> None:
        result = await db.comments.update_one(
            {"_id": team_id},
            {
                "$set": {
                    "deleted": True,
                    "time_deleted": datetime.now(timezone.utc),
                    "deleted_by": reqiure_creator.member_id,
                }
            },
        )

        if result.modified_count == 0:
            raise HTTPException(404, "Team not found")

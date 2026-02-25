from typing import Annotated

from bson import ObjectId
from fastapi import Body, HTTPException
from pymongo.errors import DuplicateKeyError

from app.api.teams.model import (
    Team,
    TeamCreateForm,
    TeamMember,
    TeamMemberRole,
)
from app.api.users.dependency import CurrentUser
from app.api.users.service import UserService
from app.database import Database
from app.utils.models.py_object_id import PyObjectId
from app.utils.models.types import Email


class TeamService:
    @staticmethod
    async def create_indexes(db: Database):
        await db.team_members.create_index(
            [("team_id", 1), ("member_id", 1)], unique=True
        )
        await db.team_members.create_index("member_id")
        await db.team_members.create_index("team_id")

    @staticmethod
    async def create_team(
        form: TeamCreateForm, creator: CurrentUser, db: Database
    ) -> Team:
        team = Team(creator_id=creator.id, **form.model_dump())
        await db.teams.insert_one(team.mongo_dump())

        team_member = TeamMember(
            member_id=creator.id, team_id=team.id, role=TeamMemberRole.CREATOR
        )

        await db.team_members.insert_one(team_member.mongo_dump())

        return team

    @staticmethod
    async def my_teams(user: CurrentUser, db: Database) -> list[Team]:
        memberships = db.team_members.find({"member_id": user.id}, {"team_id": 1})

        team_ids = [doc["team_id"] async for doc in memberships]

        teams = db.teams.find({"_id": {"$in": team_ids}})

        return [Team(**doc) async for doc in teams]

    @staticmethod
    async def add_team_member(
        team_id: PyObjectId,
        member_email: Annotated[Email, Body(embed=False)],
        user: CurrentUser,
        db: Database,
    ) -> TeamMember:
        await TeamService.require_team_role(team_id, user.id, TeamMemberRole.ADMIN, db)

        member = await UserService.get_user_by_email(member_email, db)

        team_member = TeamMember(
            role=TeamMemberRole.MEMBER, team_id=team_id, member_id=member.id
        )

        try:
            await db.team_members.insert_one(team_member.mongo_dump())
        except DuplicateKeyError:
            raise HTTPException(
                status_code=400, detail="User is already a member of this team"
            )

        return team_member

    @staticmethod
    async def get_team_members(team_id: PyObjectId, user: CurrentUser, db: Database):
        # Authorization: must be at least MEMBER
        await TeamService.require_team_role(team_id, user.id, TeamMemberRole.MEMBER, db)

        pipeline = [
            {"$match": {"team_id": team_id}},
            {
                "$lookup": {
                    "from": "users",
                    "localField": "member_id",
                    "foreignField": "_id",
                    "as": "user",
                }
            },
            {"$unwind": "$user"},
            {
                "$project": {
                    "_id": 0,
                    "member_id": 1,
                    "role": 1,
                    "name": "$user.name",
                    "email": "$user.email",  # optional
                }
            },
        ]

        cursor = await db.team_members.aggregate(pipeline)
        return [doc async for doc in cursor]

    @staticmethod
    async def require_team_role(
        team_id: ObjectId, member_id: ObjectId, min_role: TeamMemberRole, db: Database
    ):
        member_doc = await db.team_members.find_one(
            {"team_id": team_id, "member_id": member_id}
        )

        if member_doc:
            member = TeamMember(**member_doc)
            if member.role >= min_role:
                return

        raise HTTPException(status_code=403)

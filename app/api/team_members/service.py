from typing import Annotated

from fastapi import Body, HTTPException
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.api.team_members.dependencies import CurrentTeamMember, CurrentTeamAdmin
from app.api.team_members.model import (
    TeamMemberCollection,
    TeamMemberInDB,
    TeamMemberRole,
    TeamMemberUpdateForm,
)
from app.api.users.service import UserService
from app.database import Database
from app.utils.models.py_object_id import PyObjectId
from app.utils.models.types import Email


class TeamMemberService:
    @staticmethod
    async def create_indexes(db: Database):
        await db.team_members.create_index(
            [("team_id", 1), ("member_id", 1)], unique=True
        )
        await db.team_members.create_index("member_id")
        await db.team_members.create_index("team_id")

    @staticmethod
    async def add_team_member(
        team_id: PyObjectId,
        member_email: Annotated[Email, Body(embed=False)],
        db: Database,
        # Require admin action
        current_admin: CurrentTeamAdmin,
    ) -> TeamMemberInDB:

        member = await UserService.get_user_by_email(member_email, db)

        team_member = TeamMemberInDB(
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
    async def get_team_members(
        team_id: PyObjectId,
        db: Database,
        # Authorization: must be at least MEMBER
        current_meber: CurrentTeamMember,
    ) -> TeamMemberCollection:

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
        team_members = TeamMemberCollection(members=await cursor.to_list(1000))
        return team_members

    @staticmethod
    async def update_member_role(
        team_id: PyObjectId,
        member_id: PyObjectId,
        form: TeamMemberUpdateForm,
        db: Database,
        # Require admin action
        current_admin: CurrentTeamAdmin,
    ) -> TeamMemberInDB:
        member_doc = await db.team_members.find_one(
            {"team_id": team_id, "member_id": member_id}
        )

        if member_doc:
            member = TeamMemberInDB(**member_doc)
            if member.role == TeamMemberRole.CREATOR:
                raise HTTPException(403, "Cannot change creator role")

            doc = await db.team_members.find_one_and_update(
                {"_id": member_doc["_id"]},
                {"$set": form.model_dump(exclude_unset=True)},
                return_document=ReturnDocument.AFTER,
            )
            if doc:
                return TeamMemberInDB(**doc)

        raise HTTPException(404, "Member not found")

    @staticmethod
    async def remove_team_member(
        team_id: PyObjectId,
        member_id: PyObjectId,
        db: Database,
        # Require admin action
        current_admin: CurrentTeamAdmin,
    ) -> str:

        result = await db.team_members.delete_one(
            {"team_id": team_id, "member_id": member_id}
        )
        if result.deleted_count == 0:
            raise HTTPException(404, "Team member not found")

        return "deleted"

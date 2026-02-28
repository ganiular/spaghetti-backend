from datetime import datetime, timezone

from app.api.comments.dependencies import MyComment
from app.api.comments.model import (
    CommentCollection,
    CommentCreateForm,
    Comment,
    CommentUpdateForm,
)
from app.api.team_members.dependencies import CurrentTeamAdmin, CurrentTeamMember
from app.database import Database
from app.utils.models.py_object_id import PyObjectId
from app.utils.models.types import Pagination, TrimedStr


class CommentService:
    @staticmethod
    async def create_indexes(db: Database) -> None:
        # For chat list (excluding deleted comments)
        await db.comments.create_index(
            [
                ("team_id", 1),
                ("endpoint_id", 1),
                ("time_created", -1),
            ],
            # partialFilterExpression={
            #     "$or": [{"deleted": {"$exists": False}}, {"deleted": False}]
            # },
        )

        # Get comments by author (excluding deleted)
        await db.comments.create_index([("author_id", 1), ("deleted", 1)])

        # For cleanup jobs - find old deleted comments
        await db.comments.create_index(
            "deleted",
            expireAfterSeconds=7776000,  # 90 days - automatically remove old deleted comments
        )

    @staticmethod
    async def create_comment(
        team_id: PyObjectId,
        endpoint_id: TrimedStr,
        form: CommentCreateForm,
        author: CurrentTeamMember,
        db: Database,
    ) -> Comment:
        data = form.model_dump()
        comment = Comment(
            author_id=author.member_id, team_id=team_id, endpoint_id=endpoint_id, **data
        )
        await db.comments.insert_one(comment.mongo_dump())
        return comment

    @staticmethod
    async def get_comments(
        team_id: PyObjectId,
        endpoint_id: str,
        db: Database,
        pagination: Pagination,
        require_member: CurrentTeamMember,
    ) -> CommentCollection:
        # not all the comment has deleted field
        filter = {
            "team_id": team_id,
            "endpoint_id": endpoint_id,
            "deleted": {"$ne": True},  # not equal to True
        }

        cursor = (
            db.comments.find(filter)
            .sort("time_created", 1)
            .skip(pagination.skip)
            .limit(pagination.limit)
        )

        total = await db.comments.count_documents(filter)

        return CommentCollection(
            comments=await cursor.to_list(pagination.limit),
            total=total,
            limit=pagination.limit,
            skip=pagination.skip,
        )

    @staticmethod
    async def update_comment(
        comment: MyComment, form: CommentUpdateForm, db: Database
    ) -> Comment:
        data = form.model_dump(exclude_unset=True)
        data["time_updated"] = datetime.now(timezone.utc)
        result = await db.comments.update_one(
            {"_id": comment.id},
            {"$set": data},
        )
        if result.modified_count == 0:
            return comment
        comment_data = comment.mongo_dump()
        comment_data.update(data)
        return Comment.model_construct(**comment_data)

    @staticmethod
    async def delete_comment_by_id(comment: MyComment, db: Database) -> None:
        await db.comments.update_one(
            {"_id": comment.id},
            {
                "$set": {
                    "deleted": True,
                    "time_deleted": datetime.now(timezone.utc),
                    "deleted_by": comment.author_id,
                }
            },
        )

    @staticmethod
    async def delete_comments_by_endpoint(
        team_id: PyObjectId,
        endpoint_id: str,
        db: Database,
        require_admin: CurrentTeamAdmin,
    ) -> int:
        result = await db.comments.update_many(
            {"team_id": team_id, "endpoint_id": endpoint_id, "deleted": False},
            {
                "$set": {
                    "deleted": True,
                    "time_deleted": datetime.now(timezone.utc),
                    "deleted_by": require_admin.member_id,
                }
            },
        )
        return result.modified_count

    @staticmethod
    async def delete_comments_by_team(
        team_id: PyObjectId, db: Database, require_admin: CurrentTeamAdmin
    ) -> int:
        result = await db.comments.update_many(
            {"team_id": team_id, "deleted": False},
            {
                "$set": {
                    "deleted": True,
                    "time_deleted": datetime.now(timezone.utc),
                    "deleted_by": require_admin.member_id,
                }
            },
        )
        return result.modified_count

from datetime import datetime, timezone

from app.api.comments.model import (
    CommentCollection,
    CommentCreateForm,
    Comment,
    CommentUpdateForm,
)
from app.api.users.dependency import CurrentUser
from app.database import Database
from app.utils.models.py_object_id import PyObjectId


class CommentService:
    @staticmethod
    async def create_indexes(db: Database) -> None:
        # For chat list
        await db.comments.create_index(
            [
                ("team_id", 1),
                ("endpoint_id", 1),
                ("time_created", -1),  # latest first
            ]
        )

        # Get get comments by author
        # await db.comments.create_index("author_id")

    @staticmethod
    async def create_comment(
        form: CommentCreateForm, author: CurrentUser, db: Database
    ) -> Comment:
        data = form.model_dump()
        comment = Comment(author_id=author.id, **data)
        await db.comments.insert_one(comment.mongo_dump())
        return comment

    @staticmethod
    async def get_comments(
        team_id: PyObjectId, endpoint_id: str, db: Database
    ) -> CommentCollection:
        cursor = db.comments.find(
            {"team_id": team_id, "endpoint_id": endpoint_id}
        ).sort("time_created", 1)

        return CommentCollection(comments=await cursor.to_list(1000))

    @staticmethod
    async def update_comment(
        comment_id: PyObjectId, form: CommentUpdateForm, db: Database
    ) -> bool:
        result = await db.comments.update_one(
            {"_id": comment_id},
            {
                "$set": {
                    "message": form.message,
                    "time_updated": datetime.now(timezone.utc),
                }
            },
        )
        return result.modified_count == 1

    @staticmethod
    async def delete_comment_by_id(comment_id: PyObjectId, db: Database) -> bool:
        result = await db.comments.delete_one({"_id": comment_id})
        return result.deleted_count == 1

    @staticmethod
    async def delete_comments_by_endpoint(
        team_id: PyObjectId, endpoint_id: str, db: Database
    ) -> int:
        result = await db.comments.delete_many(
            {"team_id": team_id, "endpoint_id": endpoint_id}
        )
        return result.deleted_count

    @staticmethod
    async def delete_comments_by_team(team_id: PyObjectId, db: Database) -> int:
        result = await db.comments.delete_many({"team_id": team_id})
        return result.deleted_count

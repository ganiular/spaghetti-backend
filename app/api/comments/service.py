from datetime import datetime, timezone

from app.api.comments.model import (
    CommentCollection,
    CommentCreateForm,
    Comment,
    CommentUpdateForm,
)
from app.database import db
from app.utils.models.py_object_id import PyObjectId


class CommentService:
    @staticmethod
    async def create_comment(form: CommentCreateForm) -> Comment:
        data = form.model_dump()
        comment = Comment(**data)
        await db.comments.insert_one(comment.mongo_dump())
        return comment

    @staticmethod
    async def get_comments(
        team_id: PyObjectId,
        endpoint_id: str,
    ) -> CommentCollection:
        cursor = db.comments.find(
            {"team_id": team_id, "endpoint_id": endpoint_id}
        ).sort("time_created", 1)

        return CommentCollection(comments=await cursor.to_list(1000))

    @staticmethod
    async def update_comment(comment_id: PyObjectId, form: CommentUpdateForm) -> bool:
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
    async def delete_comment_by_id(comment_id: PyObjectId) -> bool:
        result = await db.comments.delete_one({"_id": comment_id})
        return result.deleted_count == 1

    @staticmethod
    async def delete_comments_by_endpoint(team_id: PyObjectId, endpoint_id: str) -> int:
        result = await db.comments.delete_many(
            {"team_id": team_id, "endpoint_id": endpoint_id}
        )
        return result.deleted_count

    @staticmethod
    async def delete_comments_by_team(team_id: PyObjectId) -> int:
        result = await db.comments.delete_many({"team_id": team_id})
        return result.deleted_count

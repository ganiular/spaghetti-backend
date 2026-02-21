from app.api.comments.model import (
    CommentCollection,
    CommentCreateForm,
    Comment,
)
from app.api.utils.models.py_object_id import PyObjectId
from app.database import db


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

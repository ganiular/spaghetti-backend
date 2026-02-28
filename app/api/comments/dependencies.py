from typing import Annotated

from fastapi import Depends, HTTPException

from app.api.comments.model import Comment
from app.api.users.dependency import CurrentUser
from app.database import Database
from app.utils.models.py_object_id import PyObjectId


async def _my_comment(
    comment_id: PyObjectId, db: Database, current_user: CurrentUser
) -> Comment:
    doc = await db.comments.find_one({"_id": comment_id, "deleted": {"$ne": True}})
    if not doc:
        raise HTTPException(404, "Comment not found")

    comment = Comment(**doc)
    if comment.author_id != current_user.id:
        raise HTTPException(403, "Access denied")

    return comment


MyComment = Annotated[Comment, Depends(_my_comment)]

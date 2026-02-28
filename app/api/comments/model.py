from pydantic import BaseModel, Field

from app.utils.models.db_model import DBModel
from app.utils.models.py_object_id import PyObjectId
from app.utils.models.types import TrimedStr


class CommentCreateForm(BaseModel):
    message: TrimedStr = Field(..., min_length=1)


class CommentUpdateForm(CommentCreateForm):
    pass


class Comment(DBModel, CommentCreateForm):
    author_id: PyObjectId
    team_id: PyObjectId
    endpoint_id: str


class CommentCollection(BaseModel):
    comments: list[Comment]
    total: int
    skip: int
    limit: int

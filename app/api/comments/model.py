from pydantic import BaseModel

from app.utils.models.db_model import DBModel
from app.utils.models.py_object_id import PyObjectId


class CommentCreateForm(BaseModel):
    team_id: PyObjectId
    endpoint_id: str
    message: str


class CommentUpdateForm(BaseModel):
    message: str


class Comment(DBModel, CommentCreateForm):
    author_id: PyObjectId


class CommentCollection(BaseModel):
    comments: list[Comment]

from pydantic import BaseModel

from app.utils.models.db_model import DBModel
from app.utils.models.py_object_id import PyObjectId


class CommentCreateForm(BaseModel):
    team_id: PyObjectId
    endpoint_id: str
    message: str
    sender_id: str


class Comment(DBModel, CommentCreateForm):
    pass


class CommentCollection(BaseModel):
    comments: list[Comment]

from fastapi import APIRouter
from app.api.comments.service import CommentService

router = APIRouter(prefix="/comments", tags=["Comments"])


router.post("/")(CommentService.create_comment)
router.get("/{team_id}/{endpoint_id}")(CommentService.get_comments)

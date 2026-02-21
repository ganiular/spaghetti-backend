from fastapi import APIRouter
from app.api.comments.service import CommentService

router = APIRouter(prefix="/comments", tags=["Comments"])


router.post("/")(CommentService.create_comment)
router.get("/{team_id}/{endpoint_id}")(CommentService.get_comments)
router.put("/{comment_id}")(CommentService.update_comment)
router.delete("/{comment_id}")(CommentService.delete_comment_by_id)
router.delete("/endpoint/{team_id}/{endpoint_id}")(
    CommentService.delete_comments_by_endpoint
)
router.delete("/team/{team_id}")(CommentService.delete_comments_by_team)

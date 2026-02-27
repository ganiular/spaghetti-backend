from fastapi import APIRouter

from app.api.team_members.service import TeamMemberService

router = APIRouter(prefix="/teams/{team_id}/members", tags=["Team Members"])

router.post("/")(TeamMemberService.add_team_member)
router.get("/")(TeamMemberService.get_team_members)
router.put("/{member_id}")(TeamMemberService.update_member_role)
router.delete("/{member_id}")(TeamMemberService.remove_team_member)

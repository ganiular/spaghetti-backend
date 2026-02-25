from fastapi import APIRouter

from app.api.teams.service import TeamService

router = APIRouter(prefix="/teams", tags=["Teams"])

router.post("/")(TeamService.create_team)
router.get("/")(TeamService.my_teams)
router.post("/{team_id}/members")(TeamService.add_team_member)
router.get("/{team_id}/members")(TeamService.get_team_members)

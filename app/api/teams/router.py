from fastapi import APIRouter

from app.api.teams.service import TeamService

router = APIRouter(prefix="/teams", tags=["Teams"])

router.post("/")(TeamService.create_team)
router.get("/")(TeamService.my_teams)
router.put("/{team_id}")(TeamService.update_team)
router.delete("/{team_id}")(TeamService.delete_team)

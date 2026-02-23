from fastapi import APIRouter

from app.api.teams.service import TeamService

router = APIRouter(
    prefix="/teams", tags=["Teams"], on_startup=[TeamService.create_index]
)

router.post("/")(TeamService.create_team)
router.get("/")(TeamService.my_teams)
router.post("/{team_id}/members")(TeamService.add_team_member)

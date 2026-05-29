from pydantic import BaseModel
from uuid import UUID

class MatchCreate(BaseModel):
    tournament_id: UUID
    team_a_id: UUID
    team_b_id: UUID
    best_of: int = 1

class ResultSubmit(BaseModel):
    team_a_score: int
    team_b_score: int
    winner_team_id: UUID
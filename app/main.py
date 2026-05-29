from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from .database import get_db, engine, Base
from .schemas import MatchCreate, ResultSubmit
from .rabbitmq import publish_event

app = FastAPI(title="Match Engine Service", description="Manages match lifecycle and disputes")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# --- 1.1 Create Match Instance ---
@app.post("/matches/", status_code=status.HTTP_201_CREATED, tags=["Match Operations"])
async def create_match(match: MatchCreate, db: AsyncSession = Depends(get_db)):
    match_id = str(uuid4())
    # TODO: Збереження в базу
    await publish_event("match.created", {"match_id": match_id, "status": "scheduled"})
    return {"id": match_id, "status": "scheduled", "message": "Match created successfully"}

# --- 1.4 Retrieve Match Details ---
@app.get("/matches/{match_id}", tags=["Match Operations"])
async def get_match(match_id: str, db: AsyncSession = Depends(get_db)):
    # TODO: Запит до бази для отримання деталей
    return {
        "match_id": match_id,
        "status": "scheduled", # Заглушка
        "team_a": "Navi",
        "team_b": "Vitality",
        "best_of": 3
    }

# --- 1.3 Submit Match Result ---
@app.post("/matches/{match_id}/results", tags=["Result Processing"])
async def submit_result(match_id: str, result: ResultSubmit, db: AsyncSession = Depends(get_db)):
    # TODO: Перевірка авторизації та валідація рахунку
    event_payload = {
        "match_id": match_id,
        "winner_team_id": str(result.winner_team_id),
        "score": f"{result.team_a_score}:{result.team_b_score}"
    }
    await publish_event("match.finished", event_payload)
    return {"message": "Result processed and MatchFinished event published"}

# --- 1.5 Raise Dispute ---
@app.post("/matches/{match_id}/disputes", tags=["Arbitration & Disputes"])
async def raise_dispute(match_id: str, team_id: str, reason: str, db: AsyncSession = Depends(get_db)):
    dispute_id = str(uuid4())
    # TODO: Зміна статусу матчу на 'disputed' у БД
    await publish_event("dispute.raised", {
        "dispute_id": dispute_id,
        "match_id": match_id,
        "team_id": team_id,
        "reason": reason
    })
    return {"dispute_id": dispute_id, "status": "pending_review", "message": "Dispute raised successfully"}

# --- 1.8 Forfeit Match ---
@app.post("/matches/{match_id}/forfeit", tags=["Match Operations"])
async def forfeit_match(match_id: str, forfeited_team_id: str, reason: str, db: AsyncSession = Depends(get_db)):
    # TODO: Запис у таблицю forfeit_records та оновлення статусу
    await publish_event("match.forfeited", {
        "match_id": match_id,
        "forfeited_team": forfeited_team_id,
        "reason": reason
    })
    return {"message": f"Match forfeited by team {forfeited_team_id}"}
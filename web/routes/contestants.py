from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from tables.database import get_db
from web import schemas
from tables.database import Contestant, Vote

router = APIRouter(prefix="/contestants", tags=["contestants"])



@router.get("/top", response_model=list[schemas.ContestantSimpleResponse])
async def get_top_contestants(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    stmt = select(Contestant).order_by(Contestant.votes.desc()).limit(limit)
    result = await db.execute(stmt)
    contestants = result.scalars().all()
    return contestants


@router.post("/", response_model=schemas.ContestantDetailResponse, status_code=201)
async def create_contestant(
    contestant: schemas.ContestantCreate,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Contestant).where(Contestant.name == contestant.name)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Участник с таким именем уже существует")

    new_contestant = Contestant(**contestant.model_dump())
    db.add(new_contestant)
    await db.commit()
    await db.refresh(new_contestant)
    return new_contestant


@router.delete("/{contestant_id}")
async def delete_contestant(
    contestant_id: int,
    db: AsyncSession = Depends(get_db)
):
    await db.execute(delete(Vote).where(Vote.contestant_id == contestant_id))
    result = await db.execute(delete(Contestant).where(Contestant.id == contestant_id))
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Участник не найден")
    await db.commit()
    return {"ok": True, "message": "Участник удалён"}

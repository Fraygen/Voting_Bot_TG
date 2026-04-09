from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from tables.database import get_db
from web import schemas
from tables.database import Contestant, Vote

router = APIRouter(prefix="/votes", tags=["votes"])



@router.get("/all", response_model=list[schemas.VoteResponse])
async def get_votes(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    stmt = select(Vote).order_by(Vote.id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    votes = result.scalars().all()
    return votes


@router.post("/admin", response_model=schemas.VoteResponse, status_code=201)
async def admin_add_vote(
    vote: schemas.VoteCreate,
    amount: int,
    db: AsyncSession = Depends(get_db)
):
    stmt_cont = select(Contestant).where(Contestant.id == vote.contestant_id)
    result_cont = await db.execute(stmt_cont)
    contestant = result_cont.scalar_one_or_none()
    if not contestant:
        raise HTTPException(status_code=404, detail="Участник не найден")

    new_vote = Vote(**vote.model_dump())
    db.add(new_vote)

    await db.execute(
        update(Contestant)
        .where(Contestant.id == vote.contestant_id)
        .values(votes=Contestant.votes + 1 * amount)
    )

    await db.commit()
    await db.refresh(new_vote)
    return new_vote


@router.delete("/admin/{contestant_id}")
async def del_vote(
    contestant_id: str,
    amount: int,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Vote).where(Vote.contestant_id == contestant_id)
    result = await db.execute(stmt)
    vote = result.scalar_one_or_none()
    if not vote:
        raise HTTPException(status_code=404, detail="Голос не найден")

    contestant_id = vote.contestant_id

    await db.execute(delete(Vote).where(Vote.contestant_id == contestant_id))

    await db.execute(
        update(Contestant)
        .where(Contestant.id == contestant_id, Contestant.votes > 0)
        .values(votes=Contestant.votes - 1 * amount)
    )

    await db.commit()
    return {"ok": True, "message": f"Голос {contestant_id} удалён"}


@router.delete("/admin/contestant/{contestant_id}/votes")
async def del_amount_votes(
    contestant_id: int,
    amount: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Vote).where(Vote.contestant_id == contestant_id).limit(amount)
    result = await db.execute(stmt)
    votes = result.scalars().all()
    if not votes:
        raise HTTPException(status_code=404, detail="Голоса не найдены")
    actual_amount = len(votes)
    vote_ids = [v.id for v in votes]
    await db.execute(delete(Vote).where(Vote.id.in_(vote_ids)))
    await db.execute(
        update(Contestant)
        .where(Contestant.id == contestant_id, Contestant.votes >= actual_amount)
        .values(votes=Contestant.votes - actual_amount)
    )
    await db.commit()
    return {"ok": True, "message": f"Удалено {actual_amount} голосов за участника {contestant_id}"}
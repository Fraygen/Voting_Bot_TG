from sqlalchemy import select, update, delete
from tables.database import AsyncSessionLocal, UserState, Contestant, Vote
from redis.asyncio import Redis
import json

r = Redis(host="localhost", port = 6379, decode_responses=True)


async def user_state(user_id: int):
    async with AsyncSessionLocal() as session:
        stmt = select(UserState).where(UserState.user_id == user_id)
        result = await session.execute(stmt)
        state = result.scalar_one_or_none()
        if state:
            return state.state
        else:
            return 0
        

async def save_user_state(user_id: int, index: int):
    async with AsyncSessionLocal() as session:
        stmt = select(UserState).where(UserState.user_id == user_id)
        result = await session.execute(stmt)
        state = result.scalar_one_or_none()
        if state:
            state.state = index
        else:
            new_state = UserState(user_id=user_id, state=index)
            session.add(new_state)
        await session.commit()


async def get_contestants():
    try:
        cached = await r.get("contestants_cache")
        if cached:
            return json.loads(cached)
    except Exception as e:
        print(f"Redis не доступен: {e}")

    async with AsyncSessionLocal() as session:
        stmt = select(Contestant).order_by(Contestant.id)
        result = await session.execute(stmt)
        contestants = result.scalars().all()
        data = [
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "photo": c.photo,
                "votes": c.votes
            }
            for c in contestants
        ]
        
        try:
            await r.set("contestants_cache", json.dumps(data), ex=3600)
        except Exception as e:
            print(f"Не удалось записать в Redis: {e}")
        
        return data


async def clear_cache():
    await r.delete("contestant_cache")


async def add_vote(user_id, contestant_id):
    async with AsyncSessionLocal() as session:
        try:
            vote = Vote(user_id = user_id,
                        contestant_id = contestant_id)
            session.add(vote)

            await session.execute(
                update(Contestant)
                .where(Contestant.id == contestant_id)
                .values(votes=Contestant.votes + 1))
            await session.commit()
            return True
        
        except Exception as e:
            await session.rollback()
            print(f"Ошибка в добавлении голоса: {e}")
            return False
        


async def has_voted(user_id):
    async with AsyncSessionLocal() as session:
        stmt = select(Vote).where(Vote.user_id == user_id)
        result = await session.execute(stmt)
        vote = result.scalar_one_or_none()
        if vote:
            return True
        else:
            return False
        

async def del_vote(user_id):
    async with AsyncSessionLocal() as session:
        try:
            stmt = select(Vote).where(Vote.user_id == user_id)
            result = await session.execute(stmt)
            vote = result.scalar_one_or_none()

            if vote:
                contestant_id = vote.contestant_id
                await session.execute(
                    delete(Vote)
                    .where(Vote.user_id == user_id))
                
                await session.execute(
                    update(Contestant)
                    .where(Contestant.id == contestant_id,
                            Contestant.votes > 0)
                    .values(votes=Contestant.votes - 1))
                
                await session.commit()
                return True
            return False
        
        except Exception as e:
            await session.rollback()
            print(f"Ошибка ужаления голоса: {e}")
            return False



async def get_cont_name(user_id):
    async with AsyncSessionLocal() as session:
        stmt = select(Vote).where(Vote.user_id == user_id)
        result = await session.execute(stmt)
        vote = result.scalar_one_or_none()
        if vote:
            contestant_id = vote.contestant_id
            stmt_cont = select(Contestant).where(Contestant.id == contestant_id)
            result = await session.execute(stmt_cont)
            contestant = result.scalar_one_or_none()
            name = contestant.name
            return name if name else "без имени"
        return "без имени"


from sqlalchemy import String, BigInteger, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from datetime import datetime
from settings import config


engine = create_async_engine(
    url=config.DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)



async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


class Base(DeclarativeBase):
    pass


class Contestant(Base):
    __tablename__ = "contestants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(100))
    photo: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                  server_default=func.now())
    votes: Mapped[int] = mapped_column(default=0)


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]= mapped_column(BigInteger)
    contestant_id: Mapped[int]
    time: Mapped[datetime] = mapped_column(default=datetime.now)


class UserState(Base):
    __tablename__ = "user_states"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    state: Mapped[int] = mapped_column(default=0)


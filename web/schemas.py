from pydantic import BaseModel
from datetime import datetime

class ContestantCreate(BaseModel):
    name: str
    description: str | None = None
    photo: str

class ContestantDetailResponse(BaseModel):
    id: int
    name: str
    description: str | None
    photo: str
    votes: int
    created_at: datetime

class ContestantSimpleResponse(BaseModel):
    id: int
    name: str
    votes: int
    model_config = {"from_attributes": True}

class ContestantUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    photo: str | None = None

class VoteCreate(BaseModel):
    user_id: int
    contestant_id: int

class VoteResponse(BaseModel):
    id: int
    user_id: int
    contestant_id: int
    model_config = {"from_attributes": True}

class VoteStatusResponse(BaseModel):
    has_voted: bool
    contestant_name: str | None = None
    contestant_id: int | None = None
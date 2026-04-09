from fastapi import FastAPI
from web.routes import contestants, votes
import uvicorn

app = FastAPI(title="Admin Panel Miss Voting")


app.include_router(contestants.router)
app.include_router(votes.router)


from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import users
from .routers import events
from .db.database import create_db

@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(events.router)

# CORS Origin Allow
app.add_middleware(
    CORSMiddleware,
    allow_origins="http://localhost:5173",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

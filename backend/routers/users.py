from fastapi import APIRouter, status, Depends
from ..db.models import UserDb
from ..db import users_crud
from ..db.database import get_session
from sqlmodel import Session

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[UserDb])
def get_users(userId: int = 0, username: str = "", session: Session = Depends(get_session)):
    return users_crud.get_users(session, userId, username)

@router.post("/", response_model=UserDb, status_code=status.HTTP_201_CREATED)
def upsert_user(userId: int, username: str, session: Session = Depends(get_session)):
    return users_crud.upsert_user(session, userId, username)

@router.delete("/", status_code=status.HTTP_200_OK)
def delete_user(userId: int, session: Session = Depends(get_session)):
    return users_crud.delete_user(session, userId)
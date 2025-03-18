from fastapi import APIRouter, status
from ..db.models import UserDb
from ..db import users_crud

router = APIRouter(prefix="/user", tags=["users"])

@router.get("s/", response_model=list[UserDb])
def get_all_users():
    return users_crud.get_all_users()

@router.get("/", response_model=UserDb)
def get_user(userId: int = 0, username: str = ""):
    return users_crud.get_user(userId, username)

@router.post("/", status_code=status.HTTP_201_CREATED)
def update_user(userId: int, username: str):
    return users_crud.update_user()

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(userId: int):
    return users_crud.delete_user(userId)
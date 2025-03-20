from fastapi import status, HTTPException
from ..db.models import UserDb
from sqlmodel import Session, select


def get_users(session: Session, userId: int = 0, username: str = ""):
    
    # Define query based on parameters
    query = select(UserDb)
    if userId != 0:
        query = query.where(UserDb.userId == userId)
    if username != "":
        query = query.where(UserDb.username.collate("NOCASE").like(f"%{username}%"))

    # Run search
    users = session.exec(query).all()
    print(users)
    
    # Process result
    if users:
        return [user.model_dump() for user in users]
    else:
        raise HTTPException(detail=f"User not found.", status_code=status.HTTP_404_NOT_FOUND)


def upsert_user(session: Session, userId: int, username: str):
    user = session.exec(select(UserDb).filter_by(userId=userId)).first()

    if user:
        user.username = username
    else:
        user = UserDb(userId=userId, username=username)
        session.add(user)
    
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, userId: int):
    user = session.get(UserDb, userId)
    if not user:
        raise HTTPException(detail=f"User does not exist.", status_code=status.HTTP_404_NOT_FOUND)
    session.delete(user)
    session.commit()
    return {"message": f"User {userId} deleted"}
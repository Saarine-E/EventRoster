from fastapi import status, HTTPException
import redis
from redis.commands.search.field import NumericField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.exceptions import ResponseError
import json

db = redis.Redis(decode_responses=True)

### Index for searching users using userIds or usernames
try:
    userIndex = db.ft("user_index")
    userIndex.info()
except ResponseError:
    userIndex.create_index([
        NumericField("$.userId", as_name="userId"),
        TextField("$.username", as_name="username")
    ], definition=IndexDefinition(prefix=["user:"], index_type=IndexType.JSON))

def get_all_users():
    users = userIndex.search(Query("*")).docs
    user_list = [json.loads(user.json) for user in users]
    return user_list

def get_user(userId: int = 0, username: str = ""):
    
    # Define query based on parameter
    if userId != 0:
        query = Query(f"@userId:[{userId} {userId}]")
    elif username != "":
        query = Query(f"@username: *{username}*")
    else:
        raise HTTPException(detail=f"User not found, no query parameters given.", status_code=status.HTTP_404_NOT_FOUND)

    # Run search
    user = userIndex.search(query)

    # Process result
    if user and user.docs:
        return json.loads(user.docs[0].json)
    else:
        raise HTTPException(detail=f"User not found.", status_code=status.HTTP_404_NOT_FOUND)

def update_user(userId: int, username: str):
    db.json().set(f"user:{userId}", "$", {"userId": userId, "username": username})
    return {"userId": userId, "username": username}

def delete_user(userId: int):
    reply = db.delete(f"user:{userId}")
    if reply == 1:
        return
    else:
        raise HTTPException(detail=f"User does not exist.", status_code=status.HTTP_404_NOT_FOUND)
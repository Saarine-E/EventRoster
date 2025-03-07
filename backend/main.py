from fastapi import FastAPI, status, HTTPException
from models import User,UserDb,Slot,SlotDb,Group,GroupDb,Event,EventDb
import utils
from datetime import datetime, date, time, timezone
import redis
from redis.commands.search.field import NumericField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.exceptions import ResponseError
import json

app = FastAPI()
db = redis.Redis(decode_responses=True)

# Search Indices
### Index for searching users using userIds or usernames
try:
    userIndex = db.ft("user_index")
    userIndex.info()
except ResponseError:
    userIndex.create_index([
        NumericField("$.userId", as_name="userId"),
        TextField("$.username", as_name="username")
    ], definition=IndexDefinition(prefix=["user:"], index_type=IndexType.JSON))

### Index for searching events using eventIds, titles or dates
try:
    eventIndex = db.ft("event_index")
    eventIndex.info()
except ResponseError:
    eventIndex.create_index([
        NumericField("$.eventId", as_name="eventId"),
        TextField("$.title", as_name="title"),
        TextField("$.eventDatetime", as_name="eventDatetime")
    ], definition=IndexDefinition(prefix=["event:"], index_type=IndexType.JSON))


# Endpoints
### Users
@app.get("/users", response_model=list[UserDb])
def get_all_users():
    users = userIndex.search(Query("*")).docs
    user_list = [json.loads(user.json) for user in users]
    return user_list

@app.get("/user", response_model=UserDb)
def get_user(userId: int = 0, username: str = ""):
    
    # Define query based on parameter
    if userId != 0:
        query = Query(f"@userId:[{userId} {userId}]")
    elif username != "":
        query = Query(f"@username:{username}*")
    else:
        raise HTTPException(detail=f"User not found, no query parameters given.", status_code=status.HTTP_404_NOT_FOUND)

    # Run search
    user = userIndex.search(query)

    # Process result
    if user and user.docs:
        return json.loads(user.docs[0].json)
    else:
        raise HTTPException(detail=f"User not found.", status_code=status.HTTP_404_NOT_FOUND)

@app.post("/user", status_code=status.HTTP_201_CREATED)
def update_user(userId: int, username: str):
    db.json().set(f"user:{userId}", "$", {"userId": userId, "username": username})
    return {"userId": userId, "username": username}

@app.delete("/user", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(eventId: int):
    reply = db.delete(f"user:{eventId}")
    if reply == 1:
        return
    else:
        raise HTTPException(detail=f"User does not exist.", status_code=status.HTTP_404_NOT_FOUND)


### Events
@app.get("/events", response_model=list[EventDb])
def get_all_events():
    events = eventIndex.search(Query("*")).docs
    event_list = [json.loads(event.json) for event in events]
    return event_list

@app.get("/event", response_model=EventDb)
def get_event(eventId: int = 0, title: str = "", eventDateTime: str = ""):
    
    # Define query based on parameter
    if eventId != 0:
        query = Query(f"@eventId:[{eventId} {eventId}]")
    elif title != "":
        query = Query(f"@title: *{title}*")
    elif eventDateTime != "":
        query = Query(f"@eventDateTime:{eventDateTime}*")
    else:
        raise HTTPException(detail=f"Event not found, no query parameters given.", status_code=status.HTTP_404_NOT_FOUND)
    
    # Run search
    event = eventIndex.search(query)

    # Process result
    if event and event.docs:
        return json.loads(event.docs[0].json)
    else:
        raise HTTPException(detail=f"No event found.", status_code=status.HTTP_404_NOT_FOUND)

@app.post("/events", status_code=status.HTTP_201_CREATED)
def new_event(title: str, eventDateTime: str, duration: float, description: str, groups: list[Group]):
    # Increase ID counter
    eventId = db.incr("eventCounter")
    
    # Convert list[Group] to list[GroupDb]
    groups_db = utils.ConvertToDbFormat(groups)

    # Compose JSON
    event = {"eventId": eventId, "title": title, "eventDatetime": eventDateTime, "duration": duration, "description": description, "groups": groups_db}
    
    # Set JSON
    db.json().set(f"event:{eventId}", "$", event)
    
    # Trigger async save to disk, to avoid overriding id numbers should redis crash before saving
    db.bgsave()
    return event

@app.delete("/events", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(eventId: int):
    reply = db.delete(f"event:{eventId}")
    if reply == 1:
        return
    else:
        raise HTTPException(detail=f"Event does not exist.", status_code=status.HTTP_404_NOT_FOUND)
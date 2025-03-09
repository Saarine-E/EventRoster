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
import operator
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
db = redis.Redis(decode_responses=True)


# CORS Origin Allow
app.add_middleware(
    CORSMiddleware,
    allow_origins="http://localhost:5173",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    event_list.sort(key=operator.itemgetter('eventDatetime'))
    return event_list

@app.get("/event", response_model=EventDb)
def get_event(eventId: int = 0, title: str = "", eventDatetime: str = ""):
    
    event = utils.fetch_event(eventId, title, eventDatetime)

    # Process result
    if event is None:
        raise HTTPException(detail=f"No event found.", status_code=status.HTTP_404_NOT_FOUND)
    return event
        

@app.post("/event", status_code=status.HTTP_201_CREATED)
def new_event(
    title: str, 
    eventDatetime: str, 
    duration: float, 
    description: str, 
    groups: list[Group]
):
    # Increase ID counter
    eventId = db.incr("eventCounter")
    
    # Convert list[Group] to list[GroupDb]
    groups_db = utils.ConvertToDbFormat(groups)

    # Compose JSON
    event = {"eventId": eventId, "title": title, "eventDatetime": eventDatetime, "duration": duration, "description": description, "groups": groups_db}
    
    # Set JSON
    db.json().set(f"event:{eventId}", "$", event)
    
    # Trigger async save to disk, to avoid overriding id numbers should redis crash before saving
    db.bgsave()
    return event


@app.patch("/event", status_code=status.HTTP_200_OK)
def update_event(
    eventId: int, 
    title: str = "", 
    eventDatetime: str = "", 
    duration: float = -1, 
    description: str = "", 
    groups: list[Group] = []
):
    
    # Get unmodified event
    currentEvent = utils.fetch_event(eventId=eventId)

    # If the unmodified event doesn't exist, return 404
    if not currentEvent:
        raise HTTPException(detail=f"Event does not exist.", status_code=status.HTTP_404_NOT_FOUND)

    # Get values depending on whether they were altered or not
    tempTitle = title if title != "" else currentEvent["title"]
    tempEventDateTime = eventDatetime if eventDatetime != "" else currentEvent["eventDatetime"]
    tempDuration = duration if duration != -1 else currentEvent["duration"]
    tempDescription = description if description != "" else currentEvent["description"]
    if groups != []:
        tempGroups = utils.ConvertToDbFormat(groups)
    else:
        tempGroups = currentEvent["groups"]

    # Combine to dictionary
    updatedEvent = {"eventId": eventId, "title": tempTitle, "eventDatetime": tempEventDateTime, "duration": tempDuration, "description": tempDescription, "groups": tempGroups}

    # Save modified event
    db.json().set(f"event:{eventId}", "$", updatedEvent)

    return updatedEvent


@app.delete("/event", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(eventId: int):
    reply = db.delete(f"event:{eventId}")
    if reply == 1:
        return
    else:
        raise HTTPException(detail=f"Event does not exist.", status_code=status.HTTP_404_NOT_FOUND)
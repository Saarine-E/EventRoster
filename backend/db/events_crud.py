from fastapi import FastAPI, status, HTTPException, APIRouter
from ..db.models import Group,EventDb
from ..db import utils
import redis
from redis.commands.search.field import NumericField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.exceptions import ResponseError
import json
import operator

db = redis.Redis(decode_responses=True)

### Index for searching users using userIds or usernames
try:
    eventIndex = db.ft("event_index")
    eventIndex.info()
except ResponseError:
    eventIndex.create_index([
        NumericField("$.eventId", as_name="eventId"),
        TextField("$.title", as_name="title"),
        TextField("$.eventDatetime", as_name="eventDatetime")
    ], definition=IndexDefinition(prefix=["event:"], index_type=IndexType.JSON))


def get_all_events():
    events = eventIndex.search(Query("*")).docs
    event_list = [json.loads(event.json) for event in events]
    event_list.sort(key=operator.itemgetter('eventDatetime'))
    return event_list

def get_event(eventId: int = 0, title: str = "", eventDatetime: str = ""):
    
    event = utils.fetch_event(eventId, title, eventDatetime)

    # Process result
    if event is None:
        raise HTTPException(detail=f"No event found.", status_code=status.HTTP_404_NOT_FOUND)
    return event
        

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


def delete_event(eventId: int):
    reply = db.delete(f"event:{eventId}")
    if reply == 1:
        return
    else:
        raise HTTPException(detail=f"Event does not exist.", status_code=status.HTTP_404_NOT_FOUND)
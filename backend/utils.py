from models import Group, GroupDb, SlotDb
from redis.commands.search.query import Query
import redis
import json

db = redis.Redis(decode_responses=True)


def ConvertToDbFormat(groups: list[Group]):
    converted = [
        GroupDb(
            name=group.name, 
            slots=[SlotDb(slotName=slot.slotName) for slot in group.slots],
            maxMembers=len(group.slots)
        ) for group in groups
    ]
    return [group.model_dump() for group in converted]


def fetch_event(eventId: int = 0, title: str = "", eventDateTime: str = ""):
    # The search index is created in main.py
    eventIndex = db.ft("event_index")

    # Get query
    if eventId != 0:
        query = Query(f"@eventId:[{eventId} {eventId}]")
    elif title != "":
        query = Query(f"@title: *{title}*")
    elif eventDateTime != "":
        query = Query(f"@eventDateTime:{eventDateTime}*")
    else:
        return None
    
    # Run search
    event = eventIndex.search(query)
    
    # Return event json, or None if event wasn't found
    return json.loads(event.docs[0].json) if event and event.docs else None
from fastapi import status, HTTPException
from ..db.models import Group,EventDb, TextInput
from sqlmodel import Session, select


def get_events(session: Session, eventId: int = 0, title: str = "", eventDatetime: str = ""):
    # Define query based on parameters
    query = select(EventDb)
    if eventId != 0:
        query = query.where(EventDb.eventId == eventId)
    if title != "":
        query = query.where(EventDb.title.collate("NOCASE").like(f"%{title}%"))

    # Execute search
    events = session.exec(query).all()

    # Process result
    if events:
        return [event.model_dump() for event in events]
    else:
        raise HTTPException(detail=f"No event found.", status_code=status.HTTP_404_NOT_FOUND)
        

def new_event(
    session: Session,
    title: str, 
    eventDatetime: str, 
    duration: float, 
    description: TextInput, 
    groups: list[Group]
):
    event = EventDb(title=title, eventDatetime=eventDatetime, duration=duration, description=description, groups=groups)
    
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def update_event(
    session: Session,
    eventId: int, 
    title: str = "", 
    eventDatetime: str = "", 
    duration: float = -1, 
    description: TextInput = {""}, 
    groups: list[Group] = []
):
    event = session.exec(select(EventDb).filter_by(eventId=eventId)).first()

    if title != "":
        event.title = title
    if eventDatetime != "":
        event.eventDatetime = eventDatetime
    if duration != -1:
        event.duration = duration
    if description != "":
        event.description = description
    if groups != []:
        event.groups = groups
    
    session.commit()
    session.refresh(event)
    return event


def delete_event(session: Session, eventId: int):
    event = session.get(EventDb, eventId)
    if not event:
        raise HTTPException(detail=f"Event does not exist.", status_code=status.HTTP_404_NOT_FOUND)
    session.delete(event)
    session.commit()
    return {"message": f"Event {eventId} deleted"}
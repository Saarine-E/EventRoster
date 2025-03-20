from fastapi import APIRouter, status, Depends
from ..db.models import Group,EventDb, TextInput
from ..db import events_crud
from ..db.database import get_session
from sqlmodel import Session


router = APIRouter(prefix="/event", tags=["events"])


@router.get("/", response_model=list[EventDb])
def get_events(eventId: int = 0, title: str = "", eventDatetime: str = "", session: Session = Depends(get_session)):
    return events_crud.get_events(session, eventId, title, eventDatetime)


@router.post("/", response_model=EventDb, status_code=status.HTTP_201_CREATED)
def new_event(
    title: str, 
    eventDatetime: str, 
    duration: float, 
    description: TextInput, 
    groups: list[Group],
    session: Session = Depends(get_session)
):
    return events_crud.new_event(title, eventDatetime, duration, description, groups, session)


@router.patch("/", status_code=status.HTTP_200_OK)
def update_event(
    eventId: int, 
    title: str = "", 
    eventDatetime: str = "", 
    duration: float = -1, 
    description: TextInput = {""}, 
    groups: list[Group] = [],
    session: Session = Depends(get_session)
):
    return events_crud.update_event(eventId,title,eventDatetime,duration,description,groups)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(eventId: int, session: Session = Depends(get_session)):
    return events_crud.delete_event(session, eventId)
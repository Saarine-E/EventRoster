from fastapi import APIRouter, status
from ..db.models import Group,EventDb
from ..db import events_crud

router = APIRouter(prefix="/event", tags=["events"])


@router.get("s/", response_model=list[EventDb])
def get_all_events():
    return events_crud.get_all_events()

@router.get("/", response_model=EventDb)
def get_event(eventId: int = 0, title: str = "", eventDatetime: str = ""):
    return events_crud.get_event(eventId, title, eventDatetime)
        

@router.post("/", status_code=status.HTTP_201_CREATED)
def new_event(
    title: str, 
    eventDatetime: str, 
    duration: float, 
    description: str, 
    groups: list[Group]
):
    return events_crud.new_event(title,eventDatetime,duration,description,groups)


@router.patch("/", status_code=status.HTTP_200_OK)
def update_event(
    eventId: int, 
    title: str = "", 
    eventDatetime: str = "", 
    duration: float = -1, 
    description: str = "", 
    groups: list[Group] = []
):
    return events_crud.update_event(eventId,title,eventDatetime,duration,description,groups)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(eventId: int):
    return events_crud.delete_event()
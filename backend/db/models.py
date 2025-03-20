from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


### Misc
class TextInput(SQLModel):
    text: str


### Users
class UserDb(SQLModel, table=True):
    userId: int = Field(default=None, primary_key=True)
    username: str = Field(index=True)

    slots: List["SlotDb"] = Relationship(back_populates="user")


### Slots
class Slot(SQLModel):
    slotName: str

class SlotDb(Slot, table=True):
    slotId: int = Field(default=None, primary_key=True)
    userId: int = Field(default=None, foreign_key="userdb.userId")
    groupId: Optional[int] = Field(default=None, foreign_key="groupdb.groupId")

    user: Optional["UserDb"] = Relationship(back_populates="slots")
    group: Optional["GroupDb"] = Relationship(back_populates="groupSlots")


### Groups
class Group(SQLModel):
    name: str
    groupSlots: List["Slot"] = []

class GroupDb(Group, table=True):
    groupId: int = Field(default=None, primary_key=True)
    maxMembers: int
    eventId: Optional[int] = Field(default=None, foreign_key="eventdb.eventId")
    
    groupSlots: List["SlotDb"] = Relationship(back_populates="group")
    events: List["EventDb"] = Relationship(back_populates="groups")


### Events
class Event(SQLModel):
    title: str = Field(index=True)
    eventDatetime: str = Field(index=True)
    duration: float
    description: str = Field(index=True)

class EventDb(Event, table=True):
    eventId: int = Field(default=None, primary_key=True, index=True)
    
    groups: List["GroupDb"] = Relationship(back_populates="events", sa_relationship_kwargs={"cascade": "all, delete"})
    # groups: List["GroupDb"] = Relationship(cascade_delete=True)
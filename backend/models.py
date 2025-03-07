from pydantic import BaseModel

# Classes for schemas and data validation
### Users
class User(BaseModel):
    userId: int
class UserDb(User):
    username: str

### Slots
class Slot(BaseModel):
    slotName: str
class SlotDb(Slot):
    userId: int = 0

### Groups
class Group(BaseModel):
    name: str
    slots: list[Slot]
class GroupDb(Group):
    maxMembers: int
    slots: list[SlotDb]

### Events
class Event(BaseModel):
    title: str
    eventDatetime: str
    duration: float
    description: str
    groups: list[GroupDb]
class EventDb(Event):
    eventId: int
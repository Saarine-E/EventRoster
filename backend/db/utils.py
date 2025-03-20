from ..db.models import Group, GroupDb, SlotDb

def ConvertToDbFormat(groups: list[Group]):
    converted = [
        GroupDb(
            name=group.name, 
            slots=[SlotDb(slotName=slot.slotName) for slot in group.slots],
            maxMembers=len(group.slots)
        ) for group in groups
    ]
    return [group.model_dump() for group in converted]
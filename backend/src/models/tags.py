from enum import Enum
from src.models.entity import Entity

class StampType(Enum):
    """
    """
    APPEARANCE = "APPEARANCE"
    INTERNAL = "INTERNAL"
    ACTION = "ACTION"
    DIALOGUE = "DIALOGUE"
    VALUES = "VALUES"
    EQUIPMENT = "EQUIPMENT"
    BACKGROUND = "BACKGROUND"
    MENTION = "MENTION"
    
class Stamp:
    """
    An AI Stamp
    """
    def __init__(self, type: StampType, primary: Entity, secondary: list[Entity] = []):
        self.type = StampType
        self.primary = primary
        self.secondary = secondary
        
    def as_dict(self) -> dict:
        return {
            "type": self.type,
            "primary": self.primary.name,
            "secondary": (list(map(lambda e: e.name(), self.secondary)))
        }
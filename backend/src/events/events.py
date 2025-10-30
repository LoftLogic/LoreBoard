from enum import Enum
from abc import ABC, abstractmethod

# Interface
class UserEvent(ABC):
    """
    Behavior of a user driven event (not a system event like a user making an account) 
    """
    
    @abstractmethod
    def ai_content(self) -> bool:
        pass
    
    @abstractmethod
    def type(self):
        pass
    
    
"""
For changes:
- Input/Event Layer
- Change representation Layer
- Document Mutation Layer
- Event dispatch layer
- Versioning Layer
"""
class ChangeType(Enum):
    ADDITION = "ADDITION"
    DELETION = "DELETION"
    MODIFICATION = "MODIFICATION"

class TextChangeEvent(UserEvent):
    """
    Event triggered to signify a change in text content
    """
    
    
class NewEntityEvent(UserEvent):
    """
    Event triggered when the user registers a new entity
    """
    def __init__(self, entity_name):
        """
        """
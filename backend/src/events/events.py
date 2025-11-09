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
    
    

class TextChangeEvent(UserEvent):
    """
    Event triggered to signify a change in text content
    """
    
    
class NewEntityEvent(UserEvent):
    """
    Event triggered when the user registers a new entity,potnhun
    """
    def __init__(self, entity_name):
        """
        """
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
    
    
    

class TextEditEvent(UserEvent):
    """
    """
    
class NewEntityEvent(UserEvent):
    """
    """
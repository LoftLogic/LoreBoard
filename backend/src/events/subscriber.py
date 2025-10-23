"""
Represents the receivers of events from publishers
"""
from abc import ABC, abstractmethod
from src.events.events import Event

class Subscriber(ABC):
    """
    Interface for a subscriber
    """
    
    @abstractmethod
    def notify(self, event: Event) -> None:
        """
        Notify the subscriber of an event
        """
        pass
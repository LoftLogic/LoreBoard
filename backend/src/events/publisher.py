"""
Publishes events to subscription
"""
from typing import Any, Dict
from src.events.subscriber import Subscriber
from src.events.events import Event
from src.types.stack import Stack

class Publisher:
    """
    Publishes events to subscribers
    """
    
    def __init__(self):
        self.subscribers = dict.fromkeys(Event, set())
        self.event_log = Stack(max_size=100)

    def add_subscriber(self, event: Event, subscriber: Subscriber) -> None:
        """
        Add a subscriber to the event publisher
        """
        if not isinstance(subscriber, Subscriber):
            raise TypeError("Subscriber must be an instance of Subscriber")
        
        self.subscribers[event].add(subscriber)
        
    def receive_event(self, event: Event) -> None:
        """
        Notify all subscribers of an event
        """
        if not isinstance(event, Event):
            raise TypeError("Event must be an instance of Event")
        
        self.log.push(event)
        self.subscribers[event].notify(event)
    
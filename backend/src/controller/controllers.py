from src.events.events import UserEvent
from src.events.publisher import Publisher
from src.events.subscriber import Subscriber
from src.services.stamper import Stamper    
from src.types.stack import Stack
from src.models.story import Story
from src.events.events import UserEvent, TextChangeEvent, ChangeType
from src.models.nodes import Node, DocumentNode

import time

class CentralController(Subscriber):
    """
    Central controller for managing events.
    Primary subscriber to all events. (?)
    """
    
    def __init__(self, model: Story):
        self.model = model
        self.node_parser = None
        
        self.llm_controller = LLMController()
        
        self.log = Stack(max_size=100)
        CentralController.number_of_instances += 1
        
        

    def notify(self, event: UserEvent) -> None:
        if isinstance(event, TextChangeEvent):
            if event.change_type == ChangeType.ADD:
                pass
            elif event.change_type == ChangeType.REMOVE:
                pass
            elif event.change_type == ChangeType.MODIFY:
                pass

class LLMController:
    """
    Maps all interactions between model and LLM services.
    """      
    def __init__(self):
        self.last_diff: DocumentNode = None
        
        
class LLMStorage:
    """
    """
    
    def __init__(self):
        self.entries = []
        
    def __update_log(self, node: Node):
        self.entries.append( (time.time(), ) )
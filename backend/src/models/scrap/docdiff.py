"""
Changes in the document

For changes:
- Input/Event Layer
- Change representation Layer
- Document Mutation Layer
- Event dispatch layer
- Versioning Layer
"""

from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass

from backend.src.models.scrap.nodes import Node

class ChangeType(Enum):
    ADDITION = ("Text being added", {"op": "insert"})
    DELETION = ("Text being deleted", {"op": "delete"})
    ATTRIBUTE = ("Attribute change", {"new_attribute": ""})

    def __new__(cls, description, meta):
        obj = object.__new__(cls)
        obj._value_ = description
        obj.meta = meta
        return obj


class Change(ABC):
    """
    """
    
    @abstractmethod
    def get_index(self, index):
        pass
    
    
@dataclass(frozen=True)
class AdditionChange(Change):
    """
    """
    
    def __init__(self, index: int, new_text: str):
        self.index = index
        self.new_text = new_text
    
    
@dataclass(frozen=True)
class DeletionChange(Change):
    """
    """
    
    def __init__(self, index: int, removed_text: str):
        self.index = index
        self.removed_text = removed_text
    
    
@dataclass(frozen=True)
class AttributeChange(Change):
    """
    """
    def __init__(self, index: int, new_attrs: set[ChangeType]):
        self.index = index
        self.new_attrs = new_attrs

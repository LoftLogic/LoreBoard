from abc import ABC, abstractmethod
from __future__ import annotations

import json
# from langchain_openai import ChatOpenAI


"""
File for all pages for the assistant. Includes entities, metadata, etc.
"""

class Entity(ABC):
    
    @abstractmethod
    def add_alias(self, new_alias: str):
        """
        Adds an alias for the entity.
        Aliases are any text that refers to the entity.
        """
        raise NotImplementedError("Must be overriden by subclass")
    
    @abstractmethod
    def removes_alias(self, to_remove: str):
        """
        Removes an alias for the entity.
        Aliases are any text that refers to the entity.
        """
        raise NotImplementedError("Must be overriden by subclass")
        
        
    @abstractmethod
    def update(self):
        """
        Updates the sheet for the specific entity.
        Invokes a specific LLM chain.
        """
        raise NotImplementedError("Must be overriden by subclass")
    
    @abstractmethod
    def as_dict(self) -> dict:
        raise NotImplementedError()
    
    @abstractmethod
    def as_json(self) -> str:
        raise NotImplementedError("Must be overridden by subclass")


class Character(Entity):
    """
    An entity representing any character
    """
    def __init__(self, name: str):
        self.name = name
        self.aliases = {name}
        self.physical_traits: str = "Physical Traits:\n To be created. (Call an update to create)"
        self.personality_traits: str = "Personality Traits:\n To be created. (Call an update to create)"
        self.actions: str = "Actions:\n To be created. (Call an update to create)"
        self.relationships: str = "Relationships: To be created. (Call an update to create)"

    def add_alias(self, new_alias):
        self.aliases.add(new_alias)
        
    def removes_alias(self, to_remove):
        self.aliases.remove(to_remove)

    def update(self):
        raise NotImplementedError

    def as_dict(self) -> dict:
        character_dict = {
                "name": self.name,
                "physical_traits": self.physical_traits,
                "personality_traits": self.personality_traits,
                "actions": self.actions,
                "relationships": self.relationships,
        }
        return character_dict
    
    def as_json(self) -> str:
        return json.dumps(self.as_dict, indent=4)
    
class Setting(Entity):
    """
    An entity representing any location or place in the story.
    """
    def __init__(self, name: str):
        self.name = name
        self.aliases = {name}
        self.description = "Description: \n To be Created (Call an update to create)"
        self.special_traits = "Special Traits: \n To be Created (Call an update to create)"
        self.story_relevance = "Story Relevance: \n To be Created (Call an update to create)"
        self.general_location = "General Location: \n To be Created (Call an update to create)"
        
    def add_alias(self, new_alias):
        self.aliases.add(new_alias)
        
    def removes_alias(self, to_remove):
        self.aliases.remove(to_remove)

    def update(self):
        raise NotImplementedError

    def as_dict(self) -> dict:
        setting_dict = {
                "name": self.name,
                "description": self.description,
                "special_traits": self.special_traits,
                "story_relevance": self.story_relevance,
                "general_location": self.general_location
        }
        return setting_dict
    
    def as_json(self) -> str:
        return json.dumps(self.as_dict, indent=4)

class Macro:
    """
    A macro is a word that refers to an entity.
    """
    def __init__(self, text: str, entity: Entity):
        self.text = text
        self.entity = entity
        
    def same_entity(self, other: Macro):
        return self.entity == other.entity


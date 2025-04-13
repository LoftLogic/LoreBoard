from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.db import models

# Character CRUD operations
def create_character(db: Session, character_data: Dict[str, Any]) -> models.Character:
    db_character = models.Character(
        name=character_data["name"],
        physical=character_data.get("physical", ""),
        personality=character_data.get("personality", ""),
        background=character_data.get("background", ""),
        goals=character_data.get("goals", ""),
        relationships=character_data.get("relationships", "")
    )
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    
    # If the character has a first name (space in the name), add it as an alias
    if " " in character_data["name"]:
        first_name = character_data["name"].split(" ")[0]
        create_alias(db, "character", db_character.id, first_name)
    
    return db_character

def get_character(db: Session, character_id: int) -> Optional[models.Character]:
    return db.query(models.Character).filter(models.Character.id == character_id).first()

def get_all_characters(db: Session, skip: int = 0, limit: int = 100) -> List[models.Character]:
    return db.query(models.Character).offset(skip).limit(limit).all()

def update_character(db: Session, character_id: int, updates: Dict[str, Any]) -> Optional[models.Character]:
    db_character = get_character(db, character_id)
    if not db_character:
        return None
    
    for key, value in updates.items():
        if hasattr(db_character, key):
            if key in ["physical", "personality", "background", "goals", "relationships"] and getattr(db_character, key):
                # For text fields, append new information
                current_value = getattr(db_character, key)
                if current_value and value:
                    setattr(db_character, key, f"{current_value}\n\n{value}")
                else:
                    setattr(db_character, key, value)
            else:
                setattr(db_character, key, value)
    
    db.commit()
    db.refresh(db_character)
    return db_character

def delete_character(db: Session, character_id: int) -> bool:
    db_character = get_character(db, character_id)
    if not db_character:
        return False
    
    db.delete(db_character)
    db.commit()
    return True

# Place CRUD operations
def create_place(db: Session, place_data: Dict[str, Any]) -> models.Place:
    db_place = models.Place(
        name=place_data["name"],
        physical=place_data.get("physical", ""),
        environment=place_data.get("environment", ""),
        purpose=place_data.get("purpose", ""),
        history=place_data.get("history", ""),
        location=place_data.get("location", "")
    )
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place

def get_place(db: Session, place_id: int) -> Optional[models.Place]:
    return db.query(models.Place).filter(models.Place.id == place_id).first()

def get_all_places(db: Session, skip: int = 0, limit: int = 100) -> List[models.Place]:
    return db.query(models.Place).offset(skip).limit(limit).all()

def update_place(db: Session, place_id: int, updates: Dict[str, Any]) -> Optional[models.Place]:
    db_place = get_place(db, place_id)
    if not db_place:
        return None
    
    for key, value in updates.items():
        if hasattr(db_place, key):
            if key in ["physical", "environment", "purpose", "history", "location"] and getattr(db_place, key):
                # For text fields, append new information
                current_value = getattr(db_place, key)
                if current_value and value:
                    setattr(db_place, key, f"{current_value}\n\n{value}")
                else:
                    setattr(db_place, key, value)
            else:
                setattr(db_place, key, value)
    
    db.commit()
    db.refresh(db_place)
    return db_place

def delete_place(db: Session, place_id: int) -> bool:
    db_place = get_place(db, place_id)
    if not db_place:
        return False
    
    db.delete(db_place)
    db.commit()
    return True

# Item CRUD operations
def create_item(db: Session, item_data: Dict[str, Any]) -> models.Item:
    db_item = models.Item(
        name=item_data["name"],
        physical=item_data.get("physical", ""),
        function=item_data.get("function", ""),
        origin=item_data.get("origin", ""),
        ownership=item_data.get("ownership", ""),
        properties=item_data.get("properties", "")
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_item(db: Session, item_id: int) -> Optional[models.Item]:
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def get_all_items(db: Session, skip: int = 0, limit: int = 100) -> List[models.Item]:
    return db.query(models.Item).offset(skip).limit(limit).all()

def update_item(db: Session, item_id: int, updates: Dict[str, Any]) -> Optional[models.Item]:
    db_item = get_item(db, item_id)
    if not db_item:
        return None
    
    for key, value in updates.items():
        if hasattr(db_item, key):
            if key in ["physical", "function", "origin", "ownership", "properties"] and getattr(db_item, key):
                # For text fields, append new information
                current_value = getattr(db_item, key)
                if current_value and value:
                    setattr(db_item, key, f"{current_value}\n\n{value}")
                else:
                    setattr(db_item, key, value)
            else:
                setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int) -> bool:
    db_item = get_item(db, item_id)
    if not db_item:
        return False
    
    db.delete(db_item)
    db.commit()
    return True

# Alias CRUD operations
def create_alias(db: Session, entity_type: str, entity_id: int, alias_text: str) -> models.Alias:
    db_alias = models.Alias(
        entity_type=entity_type,
        entity_id=entity_id,
        alias=alias_text
    )
    db.add(db_alias)
    db.commit()
    db.refresh(db_alias)
    return db_alias

def get_aliases(db: Session, entity_type: str, entity_id: int) -> List[models.Alias]:
    return db.query(models.Alias).filter(
        models.Alias.entity_type == entity_type,
        models.Alias.entity_id == entity_id
    ).all()

def delete_alias(db: Session, alias_id: int) -> bool:
    db_alias = db.query(models.Alias).filter(models.Alias.id == alias_id).first()
    if not db_alias:
        return False
    
    db.delete(db_alias)
    db.commit()
    return True

# Entity detection helpers
def get_all_entities(db: Session) -> Dict[str, List[Dict[str, Any]]]:
    """Get all entities and their aliases for entity detection"""
    result = {"characters": [], "places": [], "items": []}
    
    characters = db.query(models.Character).all()
    for char in characters:
        aliases = [a.alias for a in char.aliases]
        result["characters"].append({
            "id": char.id,
            "name": char.name,
            "aliases": aliases
        })
    
    places = db.query(models.Place).all()
    for place in places:
        aliases = [a.alias for a in place.aliases]
        result["places"].append({
            "id": place.id,
            "name": place.name,
            "aliases": aliases
        })
    
    items = db.query(models.Item).all()
    for item in items:
        aliases = [a.alias for a in item.aliases]
        result["items"].append({
            "id": item.id,
            "name": item.name,
            "aliases": aliases
        })
    
    return result

def get_entities_by_ids(db: Session, entity_ids: List[int]) -> Dict[str, List[Dict[str, Any]]]:
    """Get specific entities by IDs for bulk updates"""
    result = {"characters": [], "places": [], "items": []}
    
    # Try to find in characters
    characters = db.query(models.Character).filter(models.Character.id.in_(entity_ids)).all()
    for char in characters:
        result["characters"].append({
            "id": char.id,
            "name": char.name,
            "aliases": [a.alias for a in char.aliases]
        })
    
    # Try to find in places
    places = db.query(models.Place).filter(models.Place.id.in_(entity_ids)).all()
    for place in places:
        result["places"].append({
            "id": place.id,
            "name": place.name,
            "aliases": [a.alias for a in place.aliases]
        })
    
    # Try to find in items
    items = db.query(models.Item).filter(models.Item.id.in_(entity_ids)).all()
    for item in items:
        result["items"].append({
            "id": item.id,
            "name": item.name,
            "aliases": [a.alias for a in item.aliases]
        })
    
    return result
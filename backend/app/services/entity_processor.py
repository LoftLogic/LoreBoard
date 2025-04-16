from typing import Dict, Any, List, Optional, Tuple
from app.services import openai_service
from app.db import crud, models
from sqlalchemy.orm import Session

def get_context_paragraphs(text: str, position: Optional[int] = None) -> str:
    """
    Get context paragraphs around a position in text.
    
    Args:
        text: The full text
        position: Position of cursor/entity (optional)
        
    Returns:
        Context text with surrounding paragraphs
    """
    # Split text into paragraphs
    paragraphs = text.split('\n\n')
    
    # If no position is provided or text is short, return the full text
    if not position or len(text) < 500:
        return text
    
    # Find which paragraph contains the position
    current_pos = 0
    target_para_index = 0
    
    for i, para in enumerate(paragraphs):
        current_pos += len(para) + 2  # +2 for '\n\n'
        if current_pos >= position:
            target_para_index = i
            break
    
    # Get surrounding paragraphs
    start_idx = max(0, target_para_index - 1)  # One paragraph before
    end_idx = min(len(paragraphs), target_para_index + 2)  # One paragraph after
    
    # Join the relevant paragraphs
    context = '\n\n'.join(paragraphs[start_idx:end_idx])
    return context

def create_entity(db: Session, entity_type: str, name: str, text: str, position: Optional[int] = None) -> Tuple[Dict[str, Any], str]:
    """
    Create a new entity by processing text through LLM.
    
    Args:
        db: Database session
        entity_type: Type of entity to create (character, place, item)
        name: Name of the entity
        text: Text context
        position: Position in text (optional)
        
    Returns:
        Tuple of (created entity, entity type)
    """
    # Get context paragraphs
    context = get_context_paragraphs(text, position)
    
    # Extract attributes using LLM
    attributes = openai_service.extract_entity_attributes(entity_type, name, context)
    
    # Create entity in database
    entity_data = {"name": name, **attributes}
    
    if entity_type == "character":
        entity = crud.create_character(db, entity_data)
        return entity, "character"
    elif entity_type == "place":
        entity = crud.create_place(db, entity_data)
        return entity, "place"
    elif entity_type == "item":
        entity = crud.create_item(db, entity_data)
        return entity, "item"
    else:
        raise ValueError(f"Invalid entity type: {entity_type}")

def update_entity(db: Session, entity_type: str, entity_id: int, text: str, category: Optional[str] = None) -> Tuple[Dict[str, Any], str]:
    """
    Update an existing entity by processing text through LLM.
    
    Args:
        db: Database session
        entity_type: Type of entity to update (character, place, item)
        entity_id: ID of the entity
        text: Text context
        category: Specific category to update (optional)
        
    Returns:
        Tuple of (updated entity, entity type)
    """
    # Get the existing entity
    if entity_type == "character":
        entity = crud.get_character(db, entity_id)
        if not entity:
            raise ValueError(f"Character with ID {entity_id} not found")
        
        # Get aliases
        aliases = crud.get_aliases(db, "character", entity_id)
        entity_data = {
            "name": entity.name,
            "physical": entity.physical,
            "personality": entity.personality,
            "background": entity.background,
            "goals": entity.goals,
            "relationships": entity.relationships,
            "aliases": [a.alias for a in aliases]
        }
        
    elif entity_type == "place":
        entity = crud.get_place(db, entity_id)
        if not entity:
            raise ValueError(f"Place with ID {entity_id} not found")
        
        # Get aliases
        aliases = crud.get_aliases(db, "place", entity_id)
        entity_data = {
            "name": entity.name,
            "physical": entity.physical,
            "environment": entity.environment,
            "purpose": entity.purpose,
            "history": entity.history,
            "location": entity.location,
            "aliases": [a.alias for a in aliases]
        }
        
    elif entity_type == "item":
        entity = crud.get_item(db, entity_id)
        if not entity:
            raise ValueError(f"Item with ID {entity_id} not found")
        
        # Get aliases
        aliases = crud.get_aliases(db, "item", entity_id)
        entity_data = {
            "name": entity.name,
            "physical": entity.physical,
            "function": entity.function,
            "origin": entity.origin,
            "ownership": entity.ownership,
            "properties": entity.properties,
            "aliases": [a.alias for a in aliases]
        }
        
    else:
        raise ValueError(f"Invalid entity type: {entity_type}")
    
    # Get context text (full text for updates)
    context = text
    
    # Extract updates using LLM
    updates = openai_service.update_entity_attributes(
        entity_type, entity_data["name"], entity_data, context, category
    )
    
    # Update entity in database
    if entity_type == "character":
        updated_entity = crud.update_character(db, entity_id, updates)
        return updated_entity, "character"
    elif entity_type == "place":
        updated_entity = crud.update_place(db, entity_id, updates)
        return updated_entity, "place"
    elif entity_type == "item":
        updated_entity = crud.update_item(db, entity_id, updates)
        return updated_entity, "item"

def detect_entities(db: Session, text: str) -> List[Dict[str, Any]]:
    """
    Detect known entities in text.
    
    Args:
        db: Database session
        text: Text to analyze
        
    Returns:
        List of detected entities with positions
    """
    # Get all known entities
    entities = crud.get_all_entities(db)
    
    # Detect entities in text
    detected = openai_service.detect_entities_in_text(text, entities)
    
    return detected

def bulk_update_entities(db: Session, text: str, entity_ids: Optional[List[int]] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Process text to update multiple entities.
    
    Args:
        db: Database session
        text: Text to analyze
        entity_ids: Optional list of entity IDs to update
        
    Returns:
        Dictionary of updated entities by type
    """
    # Get entities to update
    if entity_ids:
        entities_to_update = crud.get_entities_by_ids(db, entity_ids)
    else:
        # Detect entities in text
        detected = detect_entities(db, text)
        entity_ids = [entity["id"] for entity in detected]
        entities_to_update = crud.get_entities_by_ids(db, entity_ids)
    
    # Flatten the entities for processing
    entities_flat = []
    for entity_type, entities in entities_to_update.items():
        for entity in entities:
            entities_flat.append({
                "id": entity["id"],
                "name": entity["name"],
                "type": entity_type[:-1]  # Remove 's' from type
            })
    
    # No entities to update
    if not entities_flat:
        return {"characters": [], "places": [], "items": []}
    
    # Process text for updates
    updates = openai_service.process_text_for_entity_updates(text, entities_flat)
    
    # Apply updates to database
    updated_entities = {"characters": [], "places": [], "items": []}
    
    for entity_id, update_data in updates.items():
        entity_type = update_data["type"]
        update_values = update_data["updates"]
        
        if entity_type == "character":
            entity = crud.update_character(db, int(entity_id), update_values)
            if entity:
                updated_entities["characters"].append(entity)
        elif entity_type == "place":
            entity = crud.update_place(db, int(entity_id), update_values)
            if entity:
                updated_entities["places"].append(entity)
        elif entity_type == "item":
            entity = crud.update_item(db, int(entity_id), update_values)
            if entity:
                updated_entities["items"].append(entity)
    
    return updated_entities
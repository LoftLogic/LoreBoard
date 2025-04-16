from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from app.db import schemas, crud
from app.services import entity_processor

router = APIRouter(tags=["entities"])

# Create entity endpoint
@router.post("/entities/{entity_type}", response_model=schemas.Character | schemas.Place | schemas.Item)
def create_entity(
    entity_type: str,
    entity_data: schemas.CharacterCreate | schemas.PlaceCreate | schemas.ItemCreate,
    db: Session = Depends(get_db)
):
    # Validate entity type
    if entity_type not in ["character", "place", "item"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type: {entity_type}. Must be 'character', 'place', or 'item'."
        )
    
    try:
        # Process text and create entity
        entity, created_type = entity_processor.create_entity(
            db, 
            entity_type, 
            entity_data.name, 
            entity_data.selected_text,
            entity_data.position
        )
        return entity
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Update entity endpoint
@router.put("/entities/{entity_type}/{entity_id}", response_model=schemas.Character | schemas.Place | schemas.Item)
def update_entity(
    entity_type: str,
    entity_id: int,
    update_data: schemas.CharacterUpdate | schemas.PlaceUpdate | schemas.ItemUpdate,
    db: Session = Depends(get_db)
):
    # Validate entity type
    if entity_type not in ["character", "place", "item"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type: {entity_type}. Must be 'character', 'place', or 'item'."
        )
    
    try:
        # Process text and update entity
        entity, updated_type = entity_processor.update_entity(
            db, 
            entity_type, 
            entity_id, 
            update_data.selected_text,
            update_data.category
        )
        return entity
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# Bulk update entities endpoint
@router.post("/entities/bulk-update", response_model=Dict[str, List[Any]])
def bulk_update_entities(
    update_data: schemas.BulkUpdateRequest,
    db: Session = Depends(get_db)
):
    try:
        # Process text and update multiple entities
        updated_entities = entity_processor.bulk_update_entities(
            db,
            update_data.selected_text,
            update_data.entity_ids
        )
        return updated_entities
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Get entity details endpoint
@router.get("/entities/{entity_type}/{entity_id}", response_model=schemas.Character | schemas.Place | schemas.Item)
def get_entity(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db)
):
    # Validate entity type
    if entity_type not in ["character", "place", "item"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type: {entity_type}. Must be 'character', 'place', or 'item'."
        )
    
    # Get entity from database
    if entity_type == "character":
        entity = crud.get_character(db, entity_id)
    elif entity_type == "place":
        entity = crud.get_place(db, entity_id)
    elif entity_type == "item":
        entity = crud.get_item(db, entity_id)
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_type.capitalize()} with ID {entity_id} not found"
        )
    
    return entity

# Get all entities endpoint
@router.get("/entities", response_model=Dict[str, List[Any]])
def get_all_entities(
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    print("tryna get all entities")
    result = {}
    
    # Get entities based on type filter
    if not entity_type or entity_type == "character":
        result["characters"] = crud.get_all_characters(db)
    
    if not entity_type or entity_type == "place":
        result["places"] = crud.get_all_places(db)
    
    if not entity_type or entity_type == "item":
        result["items"] = crud.get_all_items(db)
    
    return result

# Detect entities in text endpoint
@router.post("/detect-entities", response_model=schemas.EntityDetectionResponse)
def detect_entities_in_text(
    detection_data: schemas.EntityDetectionRequest,
    db: Session = Depends(get_db)
):
    detected_entities = entity_processor.detect_entities(db, detection_data.selected_text)
    return {"entities": detected_entities}
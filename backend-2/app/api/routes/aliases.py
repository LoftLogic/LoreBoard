from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.db import schemas, crud, models

router = APIRouter(tags=["aliases"])

# Add alias endpoint
@router.post("/entities/{entity_type}/{entity_id}/aliases", response_model=List[schemas.Alias])
def add_alias(
    entity_type: str,
    entity_id: int,
    alias_data: schemas.AliasCreate,
    db: Session = Depends(get_db)
):
    # Validate entity type
    if entity_type not in ["character", "place", "item"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type: {entity_type}. Must be 'character', 'place', or 'item'."
        )
    
    # Verify entity exists
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
    
    # Create the alias
    alias = crud.create_alias(db, entity_type, entity_id, alias_data.alias)
    
    # Return all aliases for this entity
    return crud.get_aliases(db, entity_type, entity_id)

# Get aliases endpoint
@router.get("/entities/{entity_type}/{entity_id}/aliases", response_model=List[schemas.Alias])
def get_aliases(
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
    
    # Verify entity exists
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
    
    # Return all aliases for this entity
    return crud.get_aliases(db, entity_type, entity_id)

# Delete alias endpoint
@router.delete("/entities/{entity_type}/{entity_id}/aliases/{alias_id}", response_model=List[schemas.Alias])
def delete_alias(
    entity_type: str,
    entity_id: int,
    alias_id: int,
    db: Session = Depends(get_db)
):
    # Validate entity type
    if entity_type not in ["character", "place", "item"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type: {entity_type}. Must be 'character', 'place', or 'item'."
        )
    
    # Verify entity exists
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
    
    # Delete the alias
    success = crud.delete_alias(db, alias_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alias with ID {alias_id} not found"
        )
    
    # Return remaining aliases for this entity
    return crud.get_aliases(db, entity_type, entity_id)
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ValidationError

# Alias schemas
class AliasBase(BaseModel):
    alias: str

class AliasCreate(AliasBase):
    pass

class Alias(AliasBase):
    id: int
    entity_type: str
    entity_id: int
    
    class Config:
        orm_mode = True

# Character schemas
class CharacterBase(BaseModel):
    name: str

class CharacterCreate(CharacterBase):
    selected_text: str
    position: Optional[int] = None

class CharacterUpdate(BaseModel):
    selected_text: str
    category: Optional[str] = None

class Character(CharacterBase):
    id: int
    physical: str
    personality: str
    background: str
    goals: str
    relationships: str
    created_at: datetime
    updated_at: datetime
    aliases: List[Alias] = []
    
    class Config:
        orm_mode = True

# Place schemas
class PlaceBase(BaseModel):
    name: str

class PlaceCreate(PlaceBase):
    selected_text: str
    position: Optional[int] = None

class PlaceUpdate(BaseModel):
    selected_text: str
    category: Optional[str] = None

class Place(PlaceBase):
    id: int
    physical: str
    environment: str
    purpose: str
    history: str
    location: str
    created_at: datetime
    updated_at: datetime
    aliases: List[Alias] = []
    
    class Config:
        orm_mode = True

# Item schemas
class ItemBase(BaseModel):
    name: str

class ItemCreate(ItemBase):
    selected_text: str
    position: Optional[int] = None

class ItemUpdate(BaseModel):
    selected_text: str
    category: Optional[str] = None

class Item(ItemBase):
    id: int
    physical: str
    function: str
    origin: str
    ownership: str
    properties: str
    created_at: datetime
    updated_at: datetime
    aliases: List[Alias] = []
    
    class Config:
        orm_mode = True

# Bulk update schema
class BulkUpdateRequest(BaseModel):
    selected_text: str
    entity_ids: Optional[List[int]] = None

# Entity detection schemas
class EntityDetectionRequest(BaseModel):
    selected_text: str

class DetectedEntity(BaseModel):
    id: int
    name: str
    type: str
    position: int

class EntityDetectionResponse(BaseModel):
    entities: List[DetectedEntity]



class EntityBase(BaseModel):
    id: int
    name: str
    
    class Config:
        orm_mode = True

class CharacterSummary(EntityBase):
    pass

class PlaceSummary(EntityBase):
    pass

class ItemSummary(EntityBase):
    pass

class AllEntitiesResponse(BaseModel):
    characters: List[CharacterSummary] = []
    places: List[PlaceSummary] = []
    items: List[ItemSummary] = []
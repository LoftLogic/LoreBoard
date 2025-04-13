from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Character(Base):
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    physical = Column(Text, default="")
    personality = Column(Text, default="")
    background = Column(Text, default="")
    goals = Column(Text, default="")
    relationships = Column(Text, default="")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship with aliases
    aliases = relationship("Alias", primaryjoin="and_(Character.id == Alias.entity_id, Alias.entity_type == 'character')",
                           back_populates="character", cascade="all, delete-orphan")

class Place(Base):
    __tablename__ = "places"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    physical = Column(Text, default="")
    environment = Column(Text, default="")
    purpose = Column(Text, default="")
    history = Column(Text, default="")
    location = Column(Text, default="")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship with aliases
    aliases = relationship("Alias", primaryjoin="and_(Place.id == Alias.entity_id, Alias.entity_type == 'place')",
                          back_populates="place", cascade="all, delete-orphan")

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    physical = Column(Text, default="")
    function = Column(Text, default="")
    origin = Column(Text, default="")
    ownership = Column(Text, default="")
    properties = Column(Text, default="")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship with aliases
    aliases = relationship("Alias", primaryjoin="and_(Item.id == Alias.entity_id, Alias.entity_type == 'item')",
                          back_populates="item", cascade="all, delete-orphan")

class Alias(Base):
    __tablename__ = "aliases"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    alias = Column(String(255), nullable=False)
    
    # Relationships with entities
    character = relationship("Character", foreign_keys=[entity_id],
                            primaryjoin="and_(Alias.entity_id == Character.id, Alias.entity_type == 'character')",
                            back_populates="aliases")
    place = relationship("Place", foreign_keys=[entity_id],
                        primaryjoin="and_(Alias.entity_id == Place.id, Alias.entity_type == 'place')",
                        back_populates="aliases")
    item = relationship("Item", foreign_keys=[entity_id],
                       primaryjoin="and_(Alias.entity_id == Item.id, Alias.entity_type == 'item')",
                       back_populates="aliases")
"""
Entity models for LoreBoard
Following MVC pattern - this is the Model layer
"""

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
import uuid


class EntityType(models.TextChoices):
    """Entity type choices"""
    CHARACTER = 'character', 'Character'
    LOCATION = 'location', 'Location'
    ITEM = 'item', 'Item'
    EVENT = 'event', 'Event'
    CUSTOM = 'custom', 'Custom'


class Entity(models.Model):
    """
    Base entity model for tracking story elements
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entities')
    name = models.CharField(max_length=255, db_index=True)
    type = models.CharField(max_length=20, choices=EntityType.choices, default=EntityType.CUSTOM)
    description = models.TextField(blank=True)
    
    # Flexible attributes stored as JSON
    attributes = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Search optimization
    search_vector = models.TextField(blank=True)  # For full-text search
    
    class Meta:
        verbose_name_plural = "Entities"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'type']),
            models.Index(fields=['user', 'name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.type})"
    
    def update_search_vector(self):
        """Update search vector for full-text search"""
        # Combine searchable fields
        search_text = f"{self.name} {self.description} {' '.join(str(v) for v in self.attributes.values())}"
        self.search_vector = search_text.lower()
        self.save(update_fields=['search_vector'])


class EntityRelationship(models.Model):
    """
    Relationships between entities
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    from_entity = models.ForeignKey(
        Entity, 
        on_delete=models.CASCADE, 
        related_name='outgoing_relationships'
    )
    to_entity = models.ForeignKey(
        Entity, 
        on_delete=models.CASCADE, 
        related_name='incoming_relationships'
    )
    relationship_type = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['from_entity', 'to_entity', 'relationship_type']
        indexes = [
            models.Index(fields=['from_entity', 'relationship_type']),
            models.Index(fields=['to_entity', 'relationship_type']),
        ]
    
    def __str__(self):
        return f"{self.from_entity.name} -> {self.relationship_type} -> {self.to_entity.name}"


class EntityAttribute(models.Model):
    """
    Predefined attribute templates for entity types
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=20, choices=EntityType.choices)
    attribute_name = models.CharField(max_length=100)
    attribute_type = models.CharField(max_length=50)  # text, number, date, etc.
    is_required = models.BooleanField(default=False)
    default_value = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['entity_type', 'attribute_name']
    
    def __str__(self):
        return f"{self.entity_type} - {self.attribute_name}"


class EntityMention(models.Model):
    """
    Track where entities are mentioned in content
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='mentions')
    content = models.ForeignKey('content.Content', on_delete=models.CASCADE, related_name='entity_mentions')
    position_start = models.IntegerField()  # Character position in content
    position_end = models.IntegerField()
    context = models.TextField()  # Surrounding text for context
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['content', 'position_start']
        indexes = [
            models.Index(fields=['entity', 'content']),
        ]
    
    def __str__(self):
        return f"{self.entity.name} mentioned in {self.content.title}"

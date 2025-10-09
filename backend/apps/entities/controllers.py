"""
Entity controllers for LoreBoard
Following MVC pattern - this is the Controller layer
Business logic and orchestration
"""

from typing import List, Dict, Optional
from django.db.models import Q, Prefetch
from django.core.cache import cache
from django.db import transaction
import logging

from .models import Entity, EntityRelationship, EntityMention
from apps.llm.services import LLMService

logger = logging.getLogger(__name__)


class EntityController:
    """
    Controller for entity-related business logic
    """
    
    def __init__(self):
        self.llm_service = LLMService()
    
    @staticmethod
    def search_entities(
        user, 
        query: Optional[str] = None,
        entity_type: Optional[str] = None,
        attributes: Optional[Dict] = None
    ) -> List[Entity]:
        """
        Search entities with various filters
        """
        queryset = Entity.objects.filter(user=user)
        
        if entity_type:
            queryset = queryset.filter(type=entity_type)
        
        if query:
            # Full-text search on name, description, and search_vector
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(search_vector__icontains=query.lower())
            )
        
        if attributes:
            # Filter by JSON attributes
            for key, value in attributes.items():
                queryset = queryset.filter(attributes__contains={key: value})
        
        return queryset.select_related('user').prefetch_related('outgoing_relationships')
    
    @transaction.atomic
    def create_entity_with_relationships(
        self,
        user,
        entity_data: Dict,
        relationships: Optional[List[Dict]] = None
    ) -> Entity:
        """
        Create entity and its relationships atomically
        """
        # Create the entity
        entity = Entity.objects.create(
            user=user,
            name=entity_data['name'],
            type=entity_data.get('type', 'custom'),
            description=entity_data.get('description', ''),
            attributes=entity_data.get('attributes', {})
        )
        
        # Update search vector
        entity.update_search_vector()
        
        # Create relationships if provided
        if relationships:
            for rel_data in relationships:
                EntityRelationship.objects.create(
                    from_entity=entity,
                    to_entity_id=rel_data['to_entity_id'],
                    relationship_type=rel_data['relationship_type'],
                    description=rel_data.get('description', '')
                )
        
        # Clear relevant caches
        self._clear_entity_cache(user.id)
        
        logger.info(f"Created entity {entity.id} with {len(relationships or [])} relationships")
        return entity
    
    def get_entity_with_context(self, entity_id: str, user) -> Dict:
        """
        Get entity with all its relationships and mentions
        """
        # Try cache first
        cache_key = f"entity_context_{entity_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        entity = Entity.objects.select_related('user').prefetch_related(
            Prefetch('outgoing_relationships', 
                     queryset=EntityRelationship.objects.select_related('to_entity')),
            Prefetch('incoming_relationships',
                     queryset=EntityRelationship.objects.select_related('from_entity')),
            Prefetch('mentions',
                     queryset=EntityMention.objects.select_related('content'))
        ).get(id=entity_id, user=user)
        
        # Build context dictionary
        context = {
            'entity': entity,
            'outgoing_relationships': [
                {
                    'id': rel.id,
                    'to_entity': rel.to_entity,
                    'type': rel.relationship_type,
                    'description': rel.description
                }
                for rel in entity.outgoing_relationships.all()
            ],
            'incoming_relationships': [
                {
                    'id': rel.id,
                    'from_entity': rel.from_entity,
                    'type': rel.relationship_type,
                    'description': rel.description
                }
                for rel in entity.incoming_relationships.all()
            ],
            'mentions': [
                {
                    'content_id': mention.content.id,
                    'content_title': mention.content.title,
                    'context': mention.context,
                    'position': mention.position_start
                }
                for mention in entity.mentions.all()[:10]  # Limit to recent mentions
            ],
            'mention_count': entity.mentions.count()
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, context, 300)
        
        return context
    
    async def extract_entities_from_text(self, text: str, user) -> List[Dict]:
        """
        Use LLM to extract potential entities from text
        """
        try:
            # Use LLM service to extract entities
            extracted = await self.llm_service.extract_entities(text)
            
            # Match with existing entities
            existing_entities = Entity.objects.filter(
                user=user,
                name__in=[e['name'] for e in extracted]
            ).values_list('name', flat=True)
            
            # Mark which are new vs existing
            for entity_data in extracted:
                entity_data['is_new'] = entity_data['name'] not in existing_entities
            
            return extracted
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return []
    
    @transaction.atomic
    def merge_entities(self, primary_id: str, secondary_ids: List[str], user) -> Entity:
        """
        Merge multiple entities into one
        """
        primary = Entity.objects.get(id=primary_id, user=user)
        secondaries = Entity.objects.filter(id__in=secondary_ids, user=user)
        
        # Merge attributes
        for secondary in secondaries:
            # Merge attributes, keeping primary's values in case of conflicts
            for key, value in secondary.attributes.items():
                if key not in primary.attributes:
                    primary.attributes[key] = value
            
            # Transfer relationships
            EntityRelationship.objects.filter(from_entity=secondary).update(from_entity=primary)
            EntityRelationship.objects.filter(to_entity=secondary).update(to_entity=primary)
            
            # Transfer mentions
            EntityMention.objects.filter(entity=secondary).update(entity=primary)
        
        # Delete secondary entities
        secondaries.delete()
        
        # Update search vector
        primary.update_search_vector()
        primary.save()
        
        # Clear caches
        self._clear_entity_cache(user.id)
        
        logger.info(f"Merged {len(secondary_ids)} entities into {primary_id}")
        return primary
    
    def get_entity_graph(self, entity_id: str, depth: int = 2) -> Dict:
        """
        Get entity relationship graph up to specified depth
        """
        # Implementation for graph traversal
        # This would build a graph structure for visualization
        pass
    
    @staticmethod
    def _clear_entity_cache(user_id: int):
        """Clear entity-related caches for a user"""
        cache.delete_many([
            f"entities_user_{user_id}",
            f"entity_types_user_{user_id}",
        ])

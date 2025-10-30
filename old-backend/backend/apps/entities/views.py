"""
Entity views for LoreBoard
Following MVC pattern - this is the View layer (API endpoints)
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
import logging

from .models import Entity, EntityRelationship
from .serializers import (
    EntitySerializer, 
    EntityDetailSerializer,
    EntityRelationshipSerializer,
    EntityCreateSerializer
)
from .controllers import EntityController

logger = logging.getLogger(__name__)


class EntityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Entity CRUD operations and related actions
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EntitySerializer
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = EntityController()
    
    def get_queryset(self):
        """Filter entities by authenticated user"""
        return Entity.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'retrieve':
            return EntityDetailSerializer
        elif self.action == 'create':
            return EntityCreateSerializer
        return EntitySerializer
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='search', type=str, description='Search query'),
            OpenApiParameter(name='type', type=str, description='Entity type filter'),
        ]
    )
    def list(self, request):
        """List entities with optional filtering"""
        entities = self.controller.search_entities(
            user=request.user,
            query=request.query_params.get('search'),
            entity_type=request.query_params.get('type')
        )
        
        page = self.paginate_queryset(entities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(entities, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """Create new entity with optional relationships"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract relationships from request
        relationships = request.data.get('relationships', [])
        
        # Use controller to create entity
        entity = self.controller.create_entity_with_relationships(
            user=request.user,
            entity_data=serializer.validated_data,
            relationships=relationships
        )
        
        # Return created entity
        response_serializer = EntityDetailSerializer(entity)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        """Get entity with full context"""
        context = self.controller.get_entity_with_context(pk, request.user)
        return Response(context)
    
    @action(detail=True, methods=['GET'])
    def relationships(self, request, pk=None):
        """Get all relationships for an entity"""
        entity = self.get_object()
        
        outgoing = EntityRelationship.objects.filter(from_entity=entity).select_related('to_entity')
        incoming = EntityRelationship.objects.filter(to_entity=entity).select_related('from_entity')
        
        return Response({
            'outgoing': EntityRelationshipSerializer(outgoing, many=True).data,
            'incoming': EntityRelationshipSerializer(incoming, many=True).data
        })
    
    @action(detail=False, methods=['POST'])
    def extract_from_text(self, request):
        """Extract entities from provided text"""
        text = request.data.get('text', '')
        if not text:
            return Response(
                {'error': 'Text is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # This would be async in production
        extracted = self.controller.extract_entities_from_text(text, request.user)
        return Response({'entities': extracted})
    
    @action(detail=False, methods=['POST'])
    def merge(self, request):
        """Merge multiple entities into one"""
        primary_id = request.data.get('primary_id')
        secondary_ids = request.data.get('secondary_ids', [])
        
        if not primary_id or not secondary_ids:
            return Response(
                {'error': 'primary_id and secondary_ids are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            merged_entity = self.controller.merge_entities(
                primary_id, 
                secondary_ids, 
                request.user
            )
            serializer = EntityDetailSerializer(merged_entity)
            return Response(serializer.data)
        except Entity.DoesNotExist:
            return Response(
                {'error': 'One or more entities not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['GET'])
    def graph(self, request, pk=None):
        """Get entity relationship graph"""
        depth = int(request.query_params.get('depth', 2))
        graph_data = self.controller.get_entity_graph(pk, depth)
        return Response(graph_data)
    
    @action(detail=True, methods=['POST'])
    def add_relationship(self, request, pk=None):
        """Add a relationship to another entity"""
        from_entity = self.get_object()
        to_entity_id = request.data.get('to_entity_id')
        relationship_type = request.data.get('relationship_type')
        
        if not to_entity_id or not relationship_type:
            return Response(
                {'error': 'to_entity_id and relationship_type are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            to_entity = Entity.objects.get(id=to_entity_id, user=request.user)
            relationship = EntityRelationship.objects.create(
                from_entity=from_entity,
                to_entity=to_entity,
                relationship_type=relationship_type,
                description=request.data.get('description', '')
            )
            serializer = EntityRelationshipSerializer(relationship)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Entity.DoesNotExist:
            return Response(
                {'error': 'Target entity not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

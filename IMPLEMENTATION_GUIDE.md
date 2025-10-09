# LoreBoard Implementation Guide

## Overview
This guide provides step-by-step instructions for implementing the remaining features of LoreBoard. The skeleton code provides the foundation - this guide helps you complete the implementation.

## Project Setup

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file with:
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=loreboard
DB_USER=postgres
DB_PASSWORD=your-password
OPENAI_API_KEY=your-openai-key
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Implementation Tasks

### 1. Complete Django Setup

#### Create Django apps structure:
```bash
cd backend
python manage.py startapp entities
python manage.py startapp content
python manage.py startapp llm
python manage.py startapp api
```

#### Move the model files into their respective apps and create migrations:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 2. Implement Serializers

Create `serializers.py` in each app. Example for entities:

```python
# backend/apps/entities/serializers.py
from rest_framework import serializers
from .models import Entity, EntityRelationship

class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ['id', 'name', 'type', 'description', 'attributes', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class EntityCreateSerializer(serializers.ModelSerializer):
    relationships = serializers.ListField(
        child=serializers.DictField(), 
        required=False
    )
    
    class Meta:
        model = Entity
        fields = ['name', 'type', 'description', 'attributes', 'relationships']
```

### 3. Complete URL Configuration

```python
# backend/loreboard/urls.py
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# backend/apps/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.entities.views import EntityViewSet
from apps.content.views import ContentViewSet

router = DefaultRouter()
router.register(r'entities', EntityViewSet, basename='entity')
router.register(r'content', ContentViewSet, basename='content')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('apps.authentication.urls')),
    path('llm/', include('apps.llm.urls')),
]
```

### 4. Implement Frontend Context and State Management

Create a context for global state:

```typescript
// frontend/src/contexts/AppContext.tsx
import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Entity, Content, UserPreferences } from '@types/index';

interface AppContextType {
  entities: Entity[];
  setEntities: (entities: Entity[]) => void;
  currentContent: Content | null;
  setCurrentContent: (content: Content | null) => void;
  preferences: UserPreferences;
  setPreferences: (prefs: UserPreferences) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [entities, setEntities] = useState<Entity[]>([]);
  const [currentContent, setCurrentContent] = useState<Content | null>(null);
  const [preferences, setPreferences] = useState<UserPreferences>({
    theme: 'light',
    autoSaveInterval: 30,
    llmProvider: 'openai',
    writingMode: 'assisted'
  });

  return (
    <AppContext.Provider value={{
      entities, setEntities,
      currentContent, setCurrentContent,
      preferences, setPreferences
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};
```

### 5. Implement Auto-fill Detection

Create a content editor that detects the auto-fill trigger:

```typescript
// frontend/src/components/ContentEditor.tsx
import React, { useState, useRef } from 'react';
import { AutoFillSlot } from './AutoFillSlot';

export const ContentEditor: React.FC = () => {
  const [content, setContent] = useState('');
  const [autoFillSlot, setAutoFillSlot] = useState<any>(null);
  const editorRef = useRef<HTMLTextAreaElement>(null);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    // Detect trigger key (e.g., ___ or specific key combination)
    if (e.key === '_' && e.shiftKey && e.ctrlKey) {
      e.preventDefault();
      const position = editorRef.current?.selectionStart || 0;
      
      // Create auto-fill slot
      const slot = {
        id: Date.now().toString(),
        position,
        context: content.substring(Math.max(0, position - 100), position + 100)
      };
      
      setAutoFillSlot(slot);
    }
  };

  const handleAutoFill = (slotId: string, text: string) => {
    // Insert text at position
    const position = autoFillSlot.position;
    const newContent = 
      content.substring(0, position) + 
      text + 
      content.substring(position);
    
    setContent(newContent);
    setAutoFillSlot(null);
  };

  return (
    <div className="relative">
      <textarea
        ref={editorRef}
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={handleKeyPress}
        className="w-full h-96 p-4 border-2 border-loreboard-200 
                   focus:border-loreboard-500 rounded-lg resize-none"
      />
      
      {autoFillSlot && (
        <div className="absolute" style={{ 
          top: '100px', // Calculate based on cursor position
          left: '100px' 
        }}>
          <AutoFillSlot
            slot={autoFillSlot}
            onFill={handleAutoFill}
            onCancel={() => setAutoFillSlot(null)}
          />
        </div>
      )}
    </div>
  );
};
```

### 6. Implement Entity Tracking in Content

Add functionality to track entity mentions:

```python
# backend/apps/content/controllers.py
import re
from typing import List, Tuple

class ContentController:
    def extract_entity_mentions(self, content: str, entities: List[Entity]) -> List[Tuple[Entity, int, int]]:
        """
        Find all entity mentions in content
        Returns list of (entity, start_pos, end_pos)
        """
        mentions = []
        
        for entity in entities:
            # Simple name matching - can be enhanced with NLP
            pattern = r'\b' + re.escape(entity.name) + r'\b'
            for match in re.finditer(pattern, content, re.IGNORECASE):
                mentions.append((entity, match.start(), match.end()))
        
        # Sort by position
        mentions.sort(key=lambda x: x[1])
        return mentions
```

### 7. Implement WebSocket for Real-time Updates

```python
# backend/apps/content/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ContentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.content_id = self.scope['url_route']['kwargs']['content_id']
        self.room_group_name = f'content_{self.content_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Handle different message types
        # Broadcast updates to group
```

### 8. Implement Celery Tasks for Async Operations

```python
# backend/apps/llm/tasks.py
from celery import shared_task
from .services import LLMService

@shared_task
def extract_entities_task(content_id: str):
    """Background task to extract entities from content"""
    from apps.content.models import Content
    
    content = Content.objects.get(id=content_id)
    llm_service = LLMService()
    
    # Extract entities
    entities = llm_service.extract_entities(content.body)
    
    # Save extracted entities
    # Update content with entity references
    
    return f"Extracted {len(entities)} entities"
```

### 9. Testing Strategy

#### Backend Tests
```python
# backend/apps/entities/tests.py
from django.test import TestCase
from rest_framework.test import APITestCase
from .models import Entity

class EntityModelTest(TestCase):
    def test_entity_creation(self):
        # Test entity creation
        pass

class EntityAPITest(APITestCase):
    def test_entity_list(self):
        # Test API endpoints
        pass
```

#### Frontend Tests
```typescript
// frontend/src/components/__tests__/EntityCard.test.tsx
import { render, screen } from '@testing-library/react';
import { EntityCard } from '../EntityCard';

test('renders entity card', () => {
  const entity = {
    id: '1',
    name: 'Test Entity',
    type: 'character',
    // ...
  };
  
  render(<EntityCard entity={entity} />);
  expect(screen.getByText('Test Entity')).toBeInTheDocument();
});
```

## Deployment Considerations

### Production Settings
- Use environment variables for sensitive data
- Configure CORS properly
- Set up SSL certificates
- Use production database (PostgreSQL)
- Configure static file serving

### Docker Setup
```dockerfile
# Dockerfile for backend
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "loreboard.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Performance Optimization
1. Implement caching (Redis)
2. Optimize database queries
3. Use pagination
4. Implement lazy loading
5. Compress static assets

## Next Steps

1. **Version Control System**: Implement full version control for content
2. **Entity Refactoring**: Build UI for bulk entity updates
3. **Advanced LLM Features**: Style analysis, plot suggestions
4. **Collaboration**: Multi-user support with permissions
5. **Export Options**: Various export formats (PDF, EPUB, etc.)

## Resources

- Django Documentation: https://docs.djangoproject.com/
- React Documentation: https://react.dev/
- LangChain Documentation: https://python.langchain.com/
- Tailwind CSS: https://tailwindcss.com/

## Support

For questions or issues:
1. Check the API documentation at `/api/docs`
2. Review error logs
3. Consult the architecture documentation

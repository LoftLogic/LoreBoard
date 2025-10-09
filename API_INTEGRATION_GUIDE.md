# LoreBoard API Integration Guide

## Overview
This guide provides comprehensive documentation for integrating the LoreBoard frontend with the backend API. All API endpoints follow RESTful conventions and return JSON responses.

## Base Configuration

### API Base URL
```
Development: http://localhost:8000/api
Production: https://api.loreboard.com/api
```

### Authentication
LoreBoard uses JWT (JSON Web Token) authentication. Include the token in the Authorization header for all authenticated requests:

```typescript
headers: {
  'Authorization': 'Bearer <your-jwt-token>',
  'Content-Type': 'application/json'
}
```

## Authentication Endpoints

### Login
```
POST /api/auth/login
```

Request Body:
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "email": "user@example.com"
  }
}
```

### Refresh Token
```
POST /api/auth/token/refresh
```

Request Body:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Entity Management API

### List Entities
```
GET /api/entities?search=<query>&type=<entity_type>&page=<page_number>
```

Query Parameters:
- `search` (optional): Search term for entity name/description
- `type` (optional): Filter by entity type (character, location, item, event, custom)
- `page` (optional): Page number for pagination
- `page_size` (optional): Items per page (default: 20)

Response:
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/entities?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid-here",
      "name": "Aragorn",
      "type": "character",
      "description": "Ranger of the North",
      "attributes": {
        "race": "Human",
        "title": "King of Gondor"
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get Entity Details
```
GET /api/entities/{entity_id}
```

Response includes full context with relationships and mentions:
```json
{
  "entity": {
    "id": "uuid-here",
    "name": "Aragorn",
    "type": "character",
    "description": "Ranger of the North",
    "attributes": {
      "race": "Human",
      "title": "King of Gondor"
    }
  },
  "outgoing_relationships": [
    {
      "id": "rel-uuid",
      "to_entity": {
        "id": "uuid2",
        "name": "Arwen",
        "type": "character"
      },
      "type": "spouse",
      "description": "Married after the War of the Ring"
    }
  ],
  "incoming_relationships": [],
  "mentions": [
    {
      "content_id": "content-uuid",
      "content_title": "Chapter 1",
      "context": "...Aragorn stepped forward...",
      "position": 1250
    }
  ],
  "mention_count": 45
}
```

### Create Entity
```
POST /api/entities
```

Request Body:
```json
{
  "name": "Gandalf",
  "type": "character",
  "description": "A wizard of Middle-earth",
  "attributes": {
    "race": "Maiar",
    "aliases": ["Mithrandir", "Stormcrow"]
  },
  "relationships": [
    {
      "to_entity_id": "frodo-uuid",
      "relationship_type": "mentor",
      "description": "Guides Frodo on his quest"
    }
  ]
}
```

### Update Entity
```
PUT /api/entities/{entity_id}
```

Request Body (partial update supported):
```json
{
  "description": "Updated description",
  "attributes": {
    "new_attribute": "value"
  }
}
```

### Delete Entity
```
DELETE /api/entities/{entity_id}
```

### Extract Entities from Text
```
POST /api/entities/extract_from_text
```

Request Body:
```json
{
  "text": "Frodo and Sam traveled to Mount Doom with the One Ring..."
}
```

Response:
```json
{
  "entities": [
    {
      "name": "Frodo",
      "type": "character",
      "confidence": 0.95,
      "is_new": false
    },
    {
      "name": "Mount Doom",
      "type": "location",
      "confidence": 0.90,
      "is_new": true
    }
  ]
}
```

## Content Management API

### List Content
```
GET /api/content?search=<query>&entity_id=<entity_id>
```

### Get Content
```
GET /api/content/{content_id}
```

### Create Content
```
POST /api/content
```

Request Body:
```json
{
  "title": "Chapter 1: A Long-Expected Party",
  "body": "When Mr. Bilbo Baggins of Bag End announced...",
  "entities": ["bilbo-uuid", "gandalf-uuid"],
  "metadata": {
    "tags": ["hobbits", "shire", "birthday"]
  }
}
```

### Update Content
```
PUT /api/content/{content_id}
```

### Auto-save Content
```
POST /api/content/{content_id}/autosave
```

Request Body:
```json
{
  "body": "Updated content text..."
}
```

## LLM Integration API

### Generate Auto-fill Suggestions
```
POST /api/llm/autofill
```

Request Body:
```json
{
  "position": 1234,
  "context": "The hero drew his ___ and faced the dragon"
}
```

Response:
```json
{
  "suggestions": [
    "sword",
    "blade",
    "weapon"
  ]
}
```

### Get Entity Summary
```
POST /api/llm/entity-summary/{entity_id}
```

Request Body:
```json
{
  "query": "What is this character's appearance?"
}
```

Response:
```json
{
  "summary": "Based on the text, this character is described as tall with dark hair..."
}
```

### Analyze Content Consistency
```
POST /api/llm/analyze-consistency/{content_id}
```

Response:
```json
{
  "inconsistencies": [
    {
      "type": "character_attribute",
      "entity": "Character Name",
      "issue": "Eye color changes from blue to green",
      "locations": [
        {"position": 123, "text": "blue eyes"},
        {"position": 456, "text": "green eyes"}
      ]
    }
  ]
}
```

## Error Handling

All API errors follow a consistent format:

```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "code": "ERROR_CODE"
}
```

Common HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Frontend Integration Examples

### Using the API Service (React/TypeScript)

```typescript
import { entityApi, contentApi, llmApi } from '@services/api';

// Get entities
const entities = await entityApi.getAll({ 
  search: 'gandalf', 
  type: 'character' 
});

// Create entity with relationships
const newEntity = await entityApi.create({
  name: 'New Character',
  type: 'character',
  description: 'A mysterious figure',
  attributes: { age: 'unknown' },
  relationships: [
    {
      to_entity_id: 'existing-entity-id',
      relationship_type: 'ally'
    }
  ]
});

// Auto-fill suggestion
const suggestions = await llmApi.generateAutoFill({
  position: cursorPosition,
  context: getSurroundingText(cursorPosition, 100)
});
```

### Error Handling Example

```typescript
try {
  const entity = await entityApi.getById(entityId);
  setEntity(entity);
} catch (error) {
  if (error.response?.status === 404) {
    showError('Entity not found');
  } else {
    showError('An error occurred while loading the entity');
  }
}
```

### Real-time Updates (WebSocket)

```typescript
// Connect to WebSocket for real-time updates
const ws = new WebSocket('ws://localhost:8000/ws/content/');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'entity_update') {
    updateEntityInUI(data.entity);
  }
};
```

## Rate Limiting

API requests are rate-limited to prevent abuse:
- Authenticated users: 1000 requests per hour
- LLM endpoints: 100 requests per hour
- Bulk operations: 10 requests per minute

## Best Practices

1. **Caching**: Cache entity lists and details for 5 minutes
2. **Pagination**: Always use pagination for list endpoints
3. **Error Retry**: Implement exponential backoff for failed requests
4. **Batch Operations**: Use bulk endpoints when available
5. **Optimistic Updates**: Update UI before API confirmation for better UX

## API Versioning

The API uses URL versioning. Current version: v1
Future versions will be available at `/api/v2/...`

## Need Help?

- Check the OpenAPI documentation at `/api/docs`
- Review error logs in the browser console
- Contact support with the request ID from error responses

# views.py
# Django view to receive and process Lexical editor content from TypeScript frontend

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class LexicalTextNode:
    """Represents a text node with formatting from Lexical editor"""
    type: str  # Always 'text'
    text: str
    format: int  # Bitmask: bold=1, italic=2, underline=8
    version: int


@dataclass
class LexicalElementNode:
    """Represents an element node (paragraph, heading, etc.) from Lexical editor"""
    type: str  # 'paragraph', 'heading', 'subtitle', etc.
    children: List[Any]  # Can be TextNode or ElementNode
    format: Optional[str] = None
    indent: Optional[int] = None
    tag: Optional[str] = None  # For headings: 'h1', 'h2', etc.
    version: int = 1


class LexicalTreeProcessor:
    """
    Processes Lexical editor tree structure and extracts meaningful information
    """
    
    @staticmethod
    def extract_plain_text(node: Dict[str, Any]) -> str:
        """
        Recursively extracts plain text from a Lexical node tree
        
        Args:
            node: Dictionary representing a Lexical node
            
        Returns:
            Plain text content as string
        """
        if node.get('type') == 'text':
            return node.get('text', '')
        
        if 'children' in node:
            texts = [
                LexicalTreeProcessor.extract_plain_text(child) 
                for child in node['children']
            ]
            return ''.join(texts)
        
        return ''
    
    @staticmethod
    def analyze_formatting(format_value: int) -> Dict[str, bool]:
        """
        Decodes the format bitmask into individual formatting flags
        
        Format bitmask values:
        - bold: 1
        - italic: 2
        - underline: 8
        
        Args:
            format_value: Integer bitmask representing formatting
            
        Returns:
            Dictionary with boolean flags for each format type
        """
        return {
            'bold': bool(format_value & 1),
            'italic': bool(format_value & 2),
            'underline': bool(format_value & 8),
        }
    
    @staticmethod
    def get_node_metadata(node: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts metadata from a node
        
        Args:
            node: Dictionary representing a Lexical node
            
        Returns:
            Dictionary containing node metadata
        """
        metadata = {
            'type': node.get('type'),
            'has_children': bool(node.get('children')),
            'child_count': len(node.get('children', [])),
        }
        
        # Add heading-specific metadata
        if node.get('type') == 'heading':
            metadata['tag'] = node.get('tag', 'h1')
        
        # Add text-specific metadata
        if node.get('type') == 'text':
            format_value = node.get('format', 0)
            metadata['formatting'] = LexicalTreeProcessor.analyze_formatting(format_value)
            metadata['text_length'] = len(node.get('text', ''))
        
        return metadata
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text"""
        return len([word for word in text.split() if word])
    
    @staticmethod
    def process_tree(content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the entire Lexical editor tree and extract analytics
        
        Args:
            content: The full Lexical editor state
            
        Returns:
            Dictionary containing processed content and analytics
        """
        root = content.get('root', {})
        children = root.get('children', [])
        
        # Extract all text
        full_text = LexicalTreeProcessor.extract_plain_text(root)
        
        # Count different node types
        node_counts = {}
        for child in children:
            node_type = child.get('type', 'unknown')
            node_counts[node_type] = node_counts.get(node_type, 0) + 1
        
        return {
            'plain_text': full_text,
            'word_count': LexicalTreeProcessor.count_words(full_text),
            'character_count': len(full_text),
            'paragraph_count': node_counts.get('paragraph', 0),
            'heading_count': node_counts.get('heading', 0),
            'node_types': node_counts,
            'total_nodes': len(children),
        }


@csrf_exempt  # Remove this in production and use proper CSRF handling
@require_http_methods(["POST"])
def receive_story(request):
    """
    API endpoint to receive story content from TypeScript frontend
    
    Endpoint: POST /api/story/
    
    Expected JSON payload:
    {
        "content": {
            "root": {
                "children": [...],
                "direction": "ltr",
                "format": "",
                "indent": 0,
                "type": "root",
                "version": 1
            }
        },
        "timestamp": "2025-11-06T12:34:56.789Z",
        "metadata": {  # Optional
            "title": "Story Title",
            "author": "Author Name",
            "tags": ["fantasy", "adventure"]
        }
    }
    
    Returns:
        JsonResponse with success status and story ID
    """
    try:
        # Parse request body
        data = json.loads(request.body)
        
        # Extract components
        content = data.get('content')
        timestamp = data.get('timestamp')
        metadata = data.get('metadata', {})
        
        # Validate required fields
        if not content:
            return JsonResponse({
                'success': False,
                'error': 'Missing content field',
                'code': 'MISSING_CONTENT'
            }, status=400)
        
        if not content.get('root'):
            return JsonResponse({
                'success': False,
                'error': 'Invalid content structure - missing root node',
                'code': 'INVALID_STRUCTURE'
            }, status=400)
        
        # Process the Lexical tree
        processor = LexicalTreeProcessor()
        analytics = processor.process_tree(content)
        
        # Here you would typically save to database
        # Example (pseudo-code):
        # story = Story.objects.create(
        #     content_json=content,
        #     plain_text=analytics['plain_text'],
        #     word_count=analytics['word_count'],
        #     title=metadata.get('title', 'Untitled'),
        #     author=metadata.get('author', 'Anonymous'),
        #     created_at=timezone.now()
        # )
        # story_id = str(story.id)
        
        # For now, generate a mock ID
        story_id = f"story_{int(timezone.now().timestamp())}"
        
        # Log received data (useful for debugging)
        print(f"Received story: {story_id}")
        print(f"Word count: {analytics['word_count']}")
        print(f"Node types: {analytics['node_types']}")
        print(f"Metadata: {metadata}")
        
        # Return success response
        return JsonResponse({
            'success': True,
            'storyId': story_id,
            'message': 'Story saved successfully',
            'analytics': {
                'word_count': analytics['word_count'],
                'character_count': analytics['character_count'],
                'paragraph_count': analytics['paragraph_count'],
            }
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body',
            'code': 'INVALID_JSON'
        }, status=400)
        
    except KeyError as e:
        return JsonResponse({
            'success': False,
            'error': f'Missing required field: {str(e)}',
            'code': 'MISSING_FIELD'
        }, status=400)
        
    except Exception as e:
        # Log the error in production
        print(f"Error processing story: {str(e)}")
        
        return JsonResponse({
            'success': False,
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }, status=500)


# Additional utility view for testing
@csrf_exempt
@require_http_methods(["GET"])
def story_api_info(request):
    """
    Returns API documentation and status
    Endpoint: GET /api/story/info/
    """
    return JsonResponse({
        'api_version': '1.0',
        'endpoint': '/api/story/',
        'methods': ['POST'],
        'description': 'Receives Lexical editor content from frontend',
        'content_format': 'Lexical EditorState JSON',
        'example_payload': {
            'content': {
                'root': {
                    'children': [],
                    'direction': 'ltr',
                    'format': '',
                    'indent': 0,
                    'type': 'root',
                    'version': 1
                }
            },
            'timestamp': '2025-11-06T12:34:56.789Z',
            'metadata': {
                'title': 'Example Story',
                'author': 'John Doe'
            }
        }
    })


# urls.py configuration (add this to your Django urls.py):
"""
from django.urls import path
from . import views

urlpatterns = [
    path('api/story/', views.receive_story, name='receive_story'),
    path('api/story/info/', views.story_api_info, name='story_api_info'),
]
"""

# settings.py CORS configuration (if frontend is on different port):
"""
# Install django-cors-headers first: pip install django-cors-headers

INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

# Development only - restrict in production!
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default
]

CORS_ALLOW_CREDENTIALS = True
"""
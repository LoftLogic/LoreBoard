# LoreBoard Architecture Overview

## Project Description
LoreBoard is an agentic creative writing application that leverages Large Language Models (LLMs) to help writers organize and access information about their novels. The app tracks entities (characters, locations, etc.) and provides intelligent writing assistance.

## Core Features
1. **Entity Management System**: Track characters, locations, and other story elements
2. **Intelligent Content Organization**: LLM-powered categorization and retrieval of story information
3. **Auto-fill Writing Assistant**: Smart slot completion for continuous writing flow
4. **Version Control**: Track changes and revisions (future feature)
5. **Entity Refactoring**: Bulk updates to entity attributes (future feature)

## Technology Stack

### Frontend
- **Framework**: React 18+ with TypeScript
- **Styling**: Tailwind CSS with custom purple theme
- **State Management**: React Context API (upgradeable to Redux if needed)
- **HTTP Client**: Axios
- **Rich Text Editor**: Draft.js or Slate.js (TBD)

### Backend
- **Framework**: Django 4.2+ with Django REST Framework
- **Language**: Python 3.10+
- **LLM Integration**: LangChain
- **Database**: PostgreSQL (optional, can start with SQLite)
- **Architecture**: Model-View-Controller (MVC) pattern

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   UI Layer  │  │ State Mgmt   │  │  API Service     │  │
│  │  Components │  │   Context     │  │    Layer         │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │ REST API
┌─────────────────────────────┴───────────────────────────────┐
│                      Backend (Django)                        │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  API Views  │  │  Controllers │  │   LangChain      │  │
│  │    (DRF)    │  │   Business   │  │  Integration     │  │
│  │             │  │    Logic     │  │                  │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                    Models (ORM)                      │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │   PostgreSQL DB    │
                    └────────────────────┘
```

## Data Flow

1. **User Input** → React Components → API Service Layer
2. **API Request** → Django Views → Controllers
3. **LLM Processing** → LangChain → Response Generation
4. **Data Storage** → Models → PostgreSQL
5. **Response** → API → Frontend State → UI Update

## Key Design Decisions

1. **MVC Pattern**: Clear separation of concerns in backend
2. **RESTful API**: Standard HTTP methods for all operations
3. **Component-Based Frontend**: Reusable UI components
4. **Entity-Centric Design**: All story elements are entities with relationships
5. **Async Processing**: LLM operations run asynchronously

## Directory Structure

```
loreboard/
├── frontend/               # React application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API integration
│   │   ├── contexts/      # State management
│   │   ├── types/         # TypeScript definitions
│   │   └── styles/        # Global styles
│   └── public/
├── backend/               # Django application
│   ├── loreboard/         # Main Django project
│   ├── apps/
│   │   ├── entities/      # Entity management
│   │   ├── content/       # Content processing
│   │   ├── llm/          # LangChain integration
│   │   └── api/          # API endpoints
│   └── requirements.txt
├── docs/                  # Documentation
└── docker-compose.yml     # Container orchestration
```

## Security Considerations

1. **Authentication**: JWT tokens for API access
2. **Rate Limiting**: Prevent LLM abuse
3. **Data Privacy**: User content never leaves the system
4. **Input Validation**: Sanitize all user inputs

## Scalability Plan

1. **Caching**: Redis for frequently accessed data
2. **Queue System**: Celery for async LLM tasks
3. **Load Balancing**: Nginx for production
4. **Database Optimization**: Indexing and query optimization

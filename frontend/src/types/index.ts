// Entity Types
export interface Entity {
  id: string;
  name: string;
  type: EntityType;
  description: string;
  attributes: Record<string, any>;
  relationships: EntityRelationship[];
  createdAt: Date;
  updatedAt: Date;
}

export enum EntityType {
  CHARACTER = 'character',
  LOCATION = 'location',
  ITEM = 'item',
  EVENT = 'event',
  CUSTOM = 'custom'
}

export interface EntityRelationship {
  id: string;
  fromEntityId: string;
  toEntityId: string;
  relationshipType: string;
  description?: string;
}

// Content Types
export interface Content {
  id: string;
  title: string;
  body: string;
  entities: string[]; // Entity IDs referenced in this content
  metadata: ContentMetadata;
  createdAt: Date;
  updatedAt: Date;
}

export interface ContentMetadata {
  wordCount: number;
  lastEditedPosition?: number;
  tags: string[];
}

// Auto-fill Types
export interface AutoFillSlot {
  id: string;
  position: number; // Position in the text
  context: string; // Surrounding text for context
  suggestions?: string[];
  selectedSuggestion?: string;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
}

// Writing Session Types
export interface WritingSession {
  id: string;
  contentId: string;
  startTime: Date;
  endTime?: Date;
  wordsWritten: number;
  autoFillsUsed: number;
}

// User Preferences
export interface UserPreferences {
  theme: 'light' | 'dark';
  autoSaveInterval: number; // in seconds
  llmProvider: 'openai' | 'anthropic' | 'local';
  writingMode: 'focused' | 'assisted';
}

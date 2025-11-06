// storyApi.ts
// TypeScript API handler for sending Lexical editor content to Django backend

/**
 * Represents a Lexical text node with formatting
 */
interface LexicalTextNode {
  type: 'text';
  text: string;
  format: number; // Bitmask: bold=1, italic=2, underline=8
  version: number;
}

/**
 * Represents a Lexical element node (paragraph, heading, etc.)
 */
interface LexicalElementNode {
  type: string; // 'paragraph', 'heading', 'subtitle', etc.
  children: (LexicalTextNode | LexicalElementNode)[];
  format?: string;
  indent?: number;
  tag?: string; // For headings: 'h1', 'h2', etc.
  version: number;
}

/**
 * Root node structure from Lexical editor
 */
interface LexicalEditorState {
  root: {
    children: LexicalElementNode[];
    direction: string;
    format: string;
    indent: number;
    type: 'root';
    version: number;
  };
}

/**
 * Request payload sent to Django backend
 */
interface StorySubmission {
  content: LexicalEditorState;
  timestamp: string;
  metadata?: {
    title?: string;
    author?: string;
    tags?: string[];
  };
}

/**
 * Response from Django backend
 */
interface StoryApiResponse {
  success: boolean;
  storyId?: string;
  message?: string;
  error?: string;
  code?: string;
}

/**
 * Configuration for API calls
 */
interface ApiConfig {
  baseUrl: string;
  timeout?: number;
  headers?: Record<string, string>;
}

/**
 * Default API configuration
 * Update baseUrl to match your Django server
 */
const DEFAULT_CONFIG: ApiConfig = {
  baseUrl: 'http://localhost:8000', // Django default
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
};

/**
 * Custom error class for API failures
 */
class StoryApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public responseData?: any
  ) {
    super(message);
    this.name = 'StoryApiError';
  }
}

/**
 * Sends story content to Django backend
 * 
 * @param editorState - The Lexical editor state JSON
 * @param metadata - Optional metadata (title, author, tags)
 * @param config - Optional API configuration override
 * @returns Promise with the API response
 * 
 * @throws StoryApiError if the request fails
 * 
 * @example
 * ```typescript
 * try {
 *   const result = await sendStory(editorState, {
 *     title: 'My Story',
 *     author: 'John Doe'
 *   });
 *   console.log('Story ID:', result.storyId);
 * } catch (error) {
 *   console.error('Failed to send story:', error);
 * }
 * ```
 */
export async function sendStory(
  editorState: LexicalEditorState,
  metadata?: StorySubmission['metadata'],
  config: Partial<ApiConfig> = {}
): Promise<StoryApiResponse> {
  const finalConfig = { ...DEFAULT_CONFIG, ...config };
  const url = `${finalConfig.baseUrl}/api/story/`;

  // Construct the payload
  const payload: StorySubmission = {
    content: editorState,
    timestamp: new Date().toISOString(),
    metadata,
  };

  // Create AbortController for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), finalConfig.timeout);

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        ...finalConfig.headers,
        ...(config.headers || {}),
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Parse response
    const data = await response.json();

    // Handle non-OK responses
    if (!response.ok) {
      throw new StoryApiError(
        data.error || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        data
      );
    }

    return data;
  } catch (error) {
    clearTimeout(timeoutId);

    // Handle different error types
    if (error instanceof StoryApiError) {
      throw error;
    }

    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new StoryApiError('Request timeout - server took too long to respond');
    }

    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new StoryApiError('Network error - unable to reach server');
    }

    throw new StoryApiError(
      `Unexpected error: ${error instanceof Error ? error.message : String(error)}`
    );
  }
}

/**
 * Validates that the editor state has the expected structure
 * 
 * @param editorState - The editor state to validate
 * @returns true if valid, false otherwise
 */
export function validateEditorState(editorState: any): editorState is LexicalEditorState {
  return (
    editorState &&
    typeof editorState === 'object' &&
    editorState.root &&
    typeof editorState.root === 'object' &&
    Array.isArray(editorState.root.children) &&
    editorState.root.type === 'root'
  );
}

/**
 * Extracts plain text from Lexical editor state (useful for previews)
 * 
 * @param editorState - The Lexical editor state
 * @returns Plain text content
 */
export function extractPlainText(editorState: LexicalEditorState): string {
  const extractFromNode = (node: LexicalElementNode | LexicalTextNode): string => {
    if (node.type === 'text') {
      return (node as LexicalTextNode).text;
    }

    if ('children' in node && Array.isArray(node.children)) {
      return node.children.map(extractFromNode).join('');
    }

    return '';
  };

  return editorState.root.children.map(extractFromNode).join('\n');
}

/**
 * Counts words in the editor content
 * 
 * @param editorState - The Lexical editor state
 * @returns Word count
 */
export function getWordCount(editorState: LexicalEditorState): number {
  const plainText = extractPlainText(editorState);
  const words = plainText.trim().split(/\s+/);
  return words.filter(word => word.length > 0).length;
}

// Export types for use in other files
export type {
  LexicalTextNode,
  LexicalElementNode,
  LexicalEditorState,
  StorySubmission,
  StoryApiResponse,
  ApiConfig,
};

export { StoryApiError };
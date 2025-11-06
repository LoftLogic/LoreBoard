import React, { useState } from 'react';
import { LexicalComposer } from '@lexical/react/LexicalComposer';
import { RichTextPlugin } from '@lexical/react/LexicalRichTextPlugin';
import { ContentEditable } from '@lexical/react/LexicalContentEditable';
import { HistoryPlugin } from '@lexical/react/LexicalHistoryPlugin';
import { OnChangePlugin } from '@lexical/react/LexicalOnChangePlugin';
import { LexicalErrorBoundary } from '@lexical/react/LexicalErrorBoundary';
import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext';
import {
  $getSelection,
  $isRangeSelection,
  FORMAT_TEXT_COMMAND,
  $createParagraphNode,
  $createTextNode,
  ElementNode,
  TextNode,
  EditorState,
  LexicalEditor,
} from 'lexical';
import { 
  $setBlocksType 
} from '@lexical/selection';
import { 
  HeadingNode,
  $createHeadingNode,
  HeadingTagType 
} from '@lexical/rich-text';
import { Bold, Italic, Underline, Search } from 'lucide-react';

// Custom heading node for our subtitle style
class SubtitleNode extends HeadingNode {
  static getType() {
    return 'subtitle';
  }

  static clone(node: SubtitleNode) {
    return new SubtitleNode(node.__tag, node.__key);
  }

  createDOM() {
    const element = document.createElement(this.__tag);
    element.className = 'text-sm text-gray-500 font-mono';
    return element;
  }

  static importJSON(serializedNode: any) {
    const node = $createSubtitleNode();
    return node;
  }

  exportJSON() {
    return {
      ...super.exportJSON(),
      type: 'subtitle',
      version: 1,
    };
  }
}

function $createSubtitleNode(): SubtitleNode {
  return new SubtitleNode('h4');
}

// Toolbar component with text formatting controls
function ToolbarPlugin() {
  const [editor] = useLexicalComposerContext();
  const [textType, setTextType] = useState<string>('basic');
  const [isBold, setIsBold] = useState(false);
  const [isItalic, setIsItalic] = useState(false);
  const [isUnderline, setIsUnderline] = useState(false);

  // Update formatting button states based on selection
  const updateToolbar = () => {
    const selection = $getSelection();
    if ($isRangeSelection(selection)) {
      setIsBold(selection.hasFormat('bold'));
      setIsItalic(selection.hasFormat('italic'));
      setIsUnderline(selection.hasFormat('underline'));
    }
  };

  // Register selection change listener
  React.useEffect(() => {
    return editor.registerUpdateListener(({ editorState }) => {
      editorState.read(() => {
        updateToolbar();
      });
    });
  }, [editor]);

  // Handle text type changes
  const handleTextTypeChange = (type: string) => {
    setTextType(type);
    editor.update(() => {
      const selection = $getSelection();
      if ($isRangeSelection(selection)) {
        switch (type) {
          case 'title':
            $setBlocksType(selection, () => $createHeadingNode('h1'));
            break;
          case 'chapter':
            $setBlocksType(selection, () => $createHeadingNode('h2'));
            break;
          case 'subtitle':
            $setBlocksType(selection, () => $createSubtitleNode());
            break;
          case 'basic':
            $setBlocksType(selection, () => $createParagraphNode());
            break;
        }
      }
    });
  };

  // Handle formatting commands
  const formatText = (format: 'bold' | 'italic' | 'underline') => {
    editor.dispatchCommand(FORMAT_TEXT_COMMAND, format);
  };

  return (
    <div className="border-b border-gray-200 bg-white px-4 py-3 flex items-center gap-3 sticky top-0 z-10">
      {/* Text type dropdown */}
      <select
        value={textType}
        onChange={(e) => handleTextTypeChange(e.target.value)}
        className="px-3 py-1.5 border border-gray-300 rounded-md text-sm font-mono focus:outline-none focus:ring-2 focus:ring-loreboard-500 focus:border-transparent"
      >
        <option value="basic">Basic</option>
        <option value="title">Title</option>
        <option value="chapter">Chapter</option>
        <option value="subtitle">Subtitle</option>
      </select>

      {/* Divider */}
      <div className="h-6 w-px bg-gray-300" />

      {/* Formatting buttons */}
      <button
        onClick={() => formatText('bold')}
        className={`p-2 rounded hover:bg-gray-100 transition-colors ${
          isBold ? 'bg-loreboard-100 text-loreboard-700' : 'text-gray-700'
        }`}
        title="Bold"
      >
        <Bold size={18} />
      </button>
      <button
        onClick={() => formatText('italic')}
        className={`p-2 rounded hover:bg-gray-100 transition-colors ${
          isItalic ? 'bg-loreboard-100 text-loreboard-700' : 'text-gray-700'
        }`}
        title="Italic"
      >
        <Italic size={18} />
      </button>
      <button
        onClick={() => formatText('underline')}
        className={`p-2 rounded hover:bg-gray-100 transition-colors ${
          isUnderline ? 'bg-loreboard-100 text-loreboard-700' : 'text-gray-700'
        }`}
        title="Underline"
      >
        <Underline size={18} />
      </button>

      {/* Spacer to push magnifying glass to the right */}
      <div className="flex-grow" />

      {/* Search/Magnifying glass button */}
      <button
        className="p-2 rounded hover:bg-loreboard-50 text-loreboard-600 hover:text-loreboard-700 transition-colors"
        title="Search"
      >
        <Search size={20} />
      </button>
    </div>
  );
}

// Main editor component
export default function StoryEditor() {
  const [editorContent, setEditorContent] = useState<string>('');
  const [isSending, setIsSending] = useState(false);
  const [sendStatus, setSendStatus] = useState<'idle' | 'success' | 'error'>('idle');

  // Initial editor configuration
  const initialConfig = {
    namespace: 'StoryEditor',
    theme: {
      paragraph: 'text-base font-mono mb-4',
      text: {
        bold: 'font-bold',
        italic: 'italic',
        underline: 'underline',
      },
      heading: {
        h1: 'text-4xl font-bold font-mono mb-6',
        h2: 'text-2xl font-semibold font-mono mb-4',
      },
    },
    onError: (error: Error) => {
      console.error(error);
    },
    nodes: [HeadingNode, SubtitleNode],
  };

  // Handle editor state changes
  const onChange = (editorState: EditorState, editor: LexicalEditor) => {
    editorState.read(() => {
      const json = editorState.toJSON();
      setEditorContent(JSON.stringify(json));
    });
  };

  // Handle send button click
  const handleSend = async () => {
    setIsSending(true);
    setSendStatus('idle');

    try {
      // Parse the editor content
      const editorStateJSON = JSON.parse(editorContent);
      
      // You can now use the imported sendStory function instead:
      // import { sendStory } from './storyApi';
      // const result = await sendStory(editorStateJSON, { title: 'My Story' });
      
      // Direct fetch implementation (using storyApi.ts structure)
      const response = await fetch('http://localhost:8000/api/story/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: editorStateJSON,
          timestamp: new Date().toISOString(),
          metadata: {
            title: 'Untitled Story',
            author: 'Anonymous',
          }
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP ${response.status}`);
      }

      const result = await response.json();
      console.log('Story sent successfully:', result);
      setSendStatus('success');
      
      // Reset status after 3 seconds
      setTimeout(() => setSendStatus('idle'), 3000);
    } catch (error) {
      console.error('Error sending story:', error);
      setSendStatus('error');
      
      // Reset status after 3 seconds
      setTimeout(() => setSendStatus('idle'), 3000);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-loreboard-50 to-white">
      <div className="max-w-4xl mx-auto py-8 px-4">
        <div className="bg-white rounded-lg shadow-purple-glow overflow-hidden">
          <LexicalComposer initialConfig={initialConfig}>
            <ToolbarPlugin />
            <div className="relative">
              <RichTextPlugin
                contentEditable={
                  <ContentEditable className="min-h-[500px] px-8 py-6 outline-none font-mono" />
                }
                placeholder={
                  <div className="absolute top-6 left-8 text-gray-400 font-mono pointer-events-none">
                    Begin your story...
                  </div>
                }
                ErrorBoundary={LexicalErrorBoundary}
              />
              <OnChangePlugin onChange={onChange} />
              <HistoryPlugin />
            </div>
          </LexicalComposer>

          {/* Send button */}
          <div className="border-t border-gray-200 px-8 py-4 flex justify-end">
            <button
              onClick={handleSend}
              disabled={isSending || !editorContent}
              className={`px-6 py-2.5 rounded-lg font-medium transition-all ${
                isSending || !editorContent
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : sendStatus === 'success'
                  ? 'bg-green-600 text-white'
                  : sendStatus === 'error'
                  ? 'bg-red-600 text-white'
                  : 'bg-loreboard-600 text-white hover:bg-loreboard-700 shadow-lg hover:shadow-purple-glow'
              }`}
            >
              {isSending ? 'Sending...' : sendStatus === 'success' ? 'Sent!' : sendStatus === 'error' ? 'Error' : 'Send'}
            </button>
          </div>
        </div>

        {/* API Documentation */}
        <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-loreboard-700 mb-4">API Documentation</h2>
          
          <div className="space-y-4 font-mono text-sm">
            <div>
              <h3 className="font-bold text-lg mb-2">Endpoint</h3>
              <code className="bg-gray-100 px-3 py-2 rounded block">POST /api/story</code>
            </div>

            <div>
              <h3 className="font-bold text-lg mb-2">Request Headers</h3>
              <pre className="bg-gray-100 px-3 py-2 rounded overflow-x-auto">
{`Content-Type: application/json`}
              </pre>
            </div>

            <div>
              <h3 className="font-bold text-lg mb-2">Request Body</h3>
              <pre className="bg-gray-100 px-3 py-2 rounded overflow-x-auto">
{`{
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
  "timestamp": "2025-11-06T12:34:56.789Z"
}`}
              </pre>
            </div>

            <div>
              <h3 className="font-bold text-lg mb-2">Content Structure</h3>
              <p className="text-gray-700 mb-2">
                The <code className="bg-gray-100 px-1 py-0.5 rounded">content</code> field contains 
                a Lexical EditorState JSON object with the following structure:
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li><strong>root</strong>: The root node containing all content</li>
                <li><strong>children</strong>: Array of paragraph/heading nodes</li>
                <li>Each node has a <strong>type</strong> (paragraph, heading, subtitle)</li>
                <li>Text nodes have <strong>format</strong> flags (bold=1, italic=2, underline=8)</li>
              </ul>
            </div>

            <div>
              <h3 className="font-bold text-lg mb-2">Expected Response</h3>
              <pre className="bg-gray-100 px-3 py-2 rounded overflow-x-auto">
{`{
  "success": true,
  "storyId": "unique-story-id",
  "message": "Story saved successfully"
}`}
              </pre>
            </div>

            <div>
              <h3 className="font-bold text-lg mb-2">Error Response</h3>
              <pre className="bg-gray-100 px-3 py-2 rounded overflow-x-auto">
{`{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}`}
              </pre>
            </div>

            <div className="border-t pt-4">
              <h3 className="font-bold text-lg mb-2">Backend Implementation Example</h3>
              <pre className="bg-gray-900 text-green-400 px-3 py-2 rounded overflow-x-auto">
{`// Express.js example
app.post('/api/story', async (req, res) => {
  try {
    const { content, timestamp } = req.body;
    
    // Validate content
    if (!content || !content.root) {
      return res.status(400).json({
        success: false,
        error: 'Invalid content structure'
      });
    }
    
    // Save to database
    const storyId = await saveStory(content, timestamp);
    
    res.json({
      success: true,
      storyId,
      message: 'Story saved successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});`}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
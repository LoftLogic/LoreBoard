import React, { useEffect, useRef, useState, useMemo } from 'react';
import ReactQuill, { Quill } from 'react-quill';
import 'react-quill/dist/quill.snow.css';

// Custom Icons Module
const icons = Quill.import('ui/icons');
icons['search'] = '<svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>';
icons['ai-search'] = '<svg viewBox="0 0 24 24" width="18" height="18"><g fill="currentColor"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/><path d="M9.5 6l.87 1.75L12.5 8l-1.63 1.25L11.5 11l-2-1-2 1 .63-1.75L6.5 8l2.13-.25z" fill="#fbbf24"/></g></svg>';

// Create a custom Picker for text types
const Picker = Quill.import('ui/picker');

class TextTypePicker extends Picker {
  constructor(select: HTMLSelectElement, label?: string) {
    super(select);
    this.container.classList.add('ql-textType');
  }
}

// Register the custom picker
Quill.register('modules/textTypePicker', TextTypePicker);

const Editor: React.FC = () => {
  const [content, setContent] = useState('');
  const [selectedFont, setSelectedFont] = useState('');
  const quillRef = useRef<ReactQuill>(null);

  // Custom toolbar configuration with custom buttons
  const modules = useMemo(() => ({
    toolbar: {
      container: [
        [{ 'textType': ['basic', 'chapter', 'title'] }],
        ['bold', 'italic', 'underline'],
        [{ 'font': [] }],
        [{ 'size': ['small', false, 'large', 'huge'] }],
        [{ 'align': [] }],
        ['clean'],
        ['search', 'ai-search'] // Custom buttons
      ],
      handlers: {
        'textType': function(this: any, value: any) {
          const quill = this.quill;
          const range = quill.getSelection();
          if (range) {
            if (value === 'basic') {
              quill.formatLine(range.index, range.length, 'header', false);
              quill.formatText(range.index, range.length, 'size', false);
            } else if (value === 'chapter') {
              quill.formatLine(range.index, range.length, 'header', 1);
              quill.formatText(range.index, range.length, 'size', 'huge');
            } else if (value === 'title') {
              quill.formatLine(range.index, range.length, 'header', 1);
              quill.formatText(range.index, range.length, 'size', 'huge');
              quill.formatLine(range.index, range.length, 'align', 'center');
            }
          }
        },
        'font': function(this: any, value: any) {
          const quill = this.quill;
          quill.format('font', value);
          // Update global font
          setSelectedFont(value || '');
        },
        'search': function(this: any) {
          console.log('Normal search clicked');
          // Add your search logic here
        },
        'ai-search': function(this: any) {
          console.log('AI search clicked');
          // Add your AI search logic here
        }
      }
    }
  }), []);

  const formats = [
    'header', 'size', 'font', 'align',
    'bold', 'italic', 'underline'
  ];

  // Handle content changes - this is the entry point for text processing
  const handleChange = (value: string, delta: any, source: string, editor: any) => {
    setContent(value);
    
    // ENTRY POINT: This is where the user's text gets converted to HTML/Delta format
    // - value: HTML string of the content
    // - delta: Quill Delta object representing the change
    // - source: 'user' or 'api' indicating who made the change
    // - editor: Quill editor instance with methods like getText(), getContents()
    
    console.log('Text changed:', {
      html: value,
      plainText: editor.getText(),
      delta: editor.getContents(),
      lastChange: delta
    });
  };

  // Apply global font to editor
  useEffect(() => {
    const editorElement = document.querySelector('.ql-editor') as HTMLElement;
    if (editorElement && selectedFont) {
      editorElement.style.fontFamily = selectedFont;
    }
  }, [selectedFont, content]);

  // Custom styles for the editor
  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      /* Custom text type styles */
      h1 {
        margin: 1.5em 0 0.5em;
      }
      
      h1[style*="text-align: center"] {
        font-size: 48px !important;
        color: #581c87;
        font-weight: bold;
      }
      
      h1:not([style*="text-align: center"]) {
        font-size: 40px !important;
        color: #3b0764;
        font-weight: bold;
      }
      
      /* Quill editor styling with purple theme */
      .ql-container {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: white;
        border-radius: 0 0 0.75rem 0.75rem;
        min-height: 600px;
      }
      
      .ql-editor {
        min-height: 600px;
        padding: 2rem;
      }
      
      .ql-toolbar {
        background: #faf5ff;
        border: 2px solid #e9d5ff !important;
        border-radius: 0.75rem 0.75rem 0 0;
        border-bottom: 1px solid #e9d5ff !important;
        padding: 0.75rem !important;
      }
      
      .ql-container {
        border: 2px solid #e9d5ff !important;
        border-top: none !important;
      }
      
      .ql-toolbar button:hover {
        background-color: #e9d5ff !important;
      }
      
      .ql-toolbar button.ql-active {
        background-color: #d8b4fe !important;
      }
      
      .ql-toolbar .ql-stroke {
        stroke: #7e22ce !important;
      }
      
      .ql-toolbar .ql-fill {
        fill: #7e22ce !important;
      }
      
      .ql-toolbar .ql-picker {
        color: #7e22ce !important;
      }
      
      /* Custom text type dropdown */
      .ql-textType {
        width: 100px !important;
      }
      
      .ql-textType .ql-picker-label::before {
        content: 'Basic';
      }
      
      .ql-textType .ql-picker-label[data-value="basic"]::before {
        content: 'Basic';
      }
      
      .ql-textType .ql-picker-label[data-value="chapter"]::before {
        content: 'Chapter';
      }
      
      .ql-textType .ql-picker-label[data-value="title"]::before {
        content: 'Title';
      }
      
      .ql-textType .ql-picker-item::before {
        content: 'Basic' !important;
      }
      
      .ql-textType .ql-picker-item[data-value="basic"]::before {
        content: 'Basic' !important;
      }
      
      .ql-textType .ql-picker-item[data-value="chapter"]::before {
        content: 'Chapter' !important;
      }
      
      .ql-textType .ql-picker-item[data-value="title"]::before {
        content: 'Title' !important;
      }
      
      /* Custom search buttons */
      .ql-search, .ql-ai-search {
        width: 35px !important;
        padding: 3px 6px !important;
      }
      
      .ql-search svg, .ql-ai-search svg {
        vertical-align: middle;
      }
      
      .ql-toolbar .ql-search:hover,
      .ql-toolbar .ql-ai-search:hover {
        background-color: #e9d5ff !important;
        border-radius: 3px;
      }
      
      /* Font dropdown customization */
      .ql-font .ql-picker-label[data-value=""]::before {
        content: 'Default Font';
      }
      
      /* Toolbar groups spacing */
      .ql-toolbar .ql-formats {
        margin-right: 15px !important;
      }
      
      .ql-toolbar .ql-formats:last-child {
        margin-right: 0 !important;
      }
    `;
    document.head.appendChild(style);
    
    // Add custom dropdown initialization
    setTimeout(() => {
      const toolbar = document.querySelector('.ql-toolbar');
      if (toolbar) {
        const textTypeSelect = toolbar.querySelector('.ql-textType .ql-picker');
        if (textTypeSelect) {
          textTypeSelect.classList.add('ql-expanded');
          setTimeout(() => {
            textTypeSelect.classList.remove('ql-expanded');
          }, 1);
        }
      }
    }, 100);
    
    return () => {
      document.head.removeChild(style);
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-loreboard-50 to-white">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold text-loreboard-950 mb-8">Creative Writing Editor</h1>
          
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <ReactQuill
              ref={quillRef}
              theme="snow"
              value={content}
              onChange={handleChange}
              modules={modules}
              formats={formats}
              placeholder="Start writing your story..."
            />
          </div>
          
          {/* Entry Point Documentation */}
          <div className="mt-8 p-6 bg-loreboard-100 rounded-xl border-2 border-loreboard-200">
            <h2 className="text-xl font-semibold text-loreboard-950 mb-3">Entry Point Documentation</h2>
            <p className="text-gray-700 mb-2">
              The text entry point is in the <code className="bg-white px-2 py-1 rounded text-loreboard-600">handleChange</code> function.
            </p>
            <p className="text-gray-700 mb-2">
              When users type, the following data is available:
            </p>
            <ul className="list-disc list-inside text-gray-700 space-y-1">
              <li><strong>HTML:</strong> The formatted HTML string of the content</li>
              <li><strong>Plain Text:</strong> Raw text without formatting (via <code className="bg-white px-2 py-1 rounded text-loreboard-600">editor.getText()</code>)</li>
              <li><strong>Delta:</strong> Quill's Delta format for rich content representation (via <code className="bg-white px-2 py-1 rounded text-loreboard-600">editor.getContents()</code>)</li>
              <li><strong>Last Change:</strong> The specific delta of the most recent change</li>
            </ul>
            <p className="text-gray-700 mt-3">
              Check the browser console to see real-time logging of all text changes and their various formats.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Editor;
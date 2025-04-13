import "./styles.scss";

import { Color } from "@tiptap/extension-color";
import ListItem from "@tiptap/extension-list-item";
import TextStyle from "@tiptap/extension-text-style";
import Underline from "@tiptap/extension-underline";
import { useEditor, EditorContent, BubbleMenu } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import React, { useState, useCallback, useEffect } from "react";
import { v4 as uuidv4 } from 'uuid';
import { CommentMark } from "./CommentMark";
import CommentViewComponent from "./CommentViewComponent";
import LeftSidebar from './LeftSidebar';
import RightChatPanel from './RightChatPanel';

const MenuBar = ({ editor }) => {
  if (!editor) {
    return null;
  }

  return (
    <div className="editor-menu">
      <button
        onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
        className={editor.isActive("heading", { level: 1 }) ? "is-active" : ""}
        title="Heading 1"
      >
        H1
      </button>
      <button
        onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
        className={editor.isActive("heading", { level: 2 }) ? "is-active" : ""}
        title="Heading 2"
      >
        H2
      </button>
      <button
        onClick={() => editor.chain().focus().setParagraph().run()}
        className={editor.isActive("paragraph") ? "is-active" : ""}
        title="Body Text"
      >
        ¶
      </button>
      <button
        onClick={() => editor.chain().focus().toggleBold().run()}
        disabled={!editor.can().chain().focus().toggleBold().run()}
        className={editor.isActive("bold") ? "is-active" : ""}
        title="Bold"
      >
        B
      </button>
      <button
        onClick={() => editor.chain().focus().toggleItalic().run()}
        disabled={!editor.can().chain().focus().toggleItalic().run()}
        className={editor.isActive("italic") ? "is-active" : ""}
        title="Italic"
      >
        <em>I</em>
      </button>
      <button
        onClick={() => editor.chain().focus().toggleUnderline().run()}
        disabled={!editor.can().chain().focus().toggleUnderline().run()}
        className={editor.isActive("underline") ? "is-active" : ""}
        title="Underline"
      >
        <u>U</u>
      </button>
    </div>
  );
};

const SelectionMenu = ({ editor }) => {
  const [showCommentInput, setShowCommentInput] = useState(false);
  const [commentText, setCommentText] = useState('');

  if (!editor) {
    return null;
  }

  const addComment = () => {
    if (commentText.trim()) {
      const commentId = uuidv4();
      editor.chain().focus().setMark('comment', {
        id: commentId,
        text: commentText,
        author: 'Current User',
        createdAt: new Date().toISOString(),
        resolved: false,
      }).run();
      setCommentText('');
      setShowCommentInput(false);
    }
  };

  const handleTrackEntity = useCallback(async (entityType) => {
    if (!editor) return;

    const { from, to } = editor.state.selection;
    const selectedText = editor.state.doc.textBetween(from, to);

    if (!selectedText.trim()) {
      console.log("No text selected for tracking.");
      return;
    }

    const apiEntityType = entityType.toLowerCase();
    const apiUrl = `http://localhost:8000/api/entities/${apiEntityType}`;

    const requestBody = {
      name: selectedText,
      selected_text: selectedText,
      position: from
    };

    console.log(`Tracking Entity: Type=${entityType}, Text='${selectedText}', Position=${from}`);
    console.log(`Sending POST request to ${apiUrl} with body:`, requestBody);

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorData.detail || response.statusText}`);
      }

      const createdEntity = await response.json();
      console.log('Successfully created entity:', createdEntity);

    } catch (error) {
      console.error('Error tracking entity:', error);
    }

  }, [editor]);

  return (
    <BubbleMenu className="bubble-menu" editor={editor} tippyOptions={{ duration: 100 }}>
      {!showCommentInput ? (
        <>
          <button
            onClick={() => setShowCommentInput(true)}
            className="bubble-menu-button"
            title="Add Comment"
          >
            💬
          </button>
          <button
            onClick={() => handleTrackEntity('Character')}
            className="bubble-menu-button"
            title="Track Character"
          >
            👤
          </button>
          <button
            onClick={() => handleTrackEntity('Place')}
            className="bubble-menu-button"
            title="Track Place"
          >
            🌍
          </button>
          <button
            onClick={() => handleTrackEntity('Item')}
            className="bubble-menu-button"
            title="Track Item"
          >
            📦
          </button>
        </>
      ) : (
        <div className="bubble-comment-input">
          <textarea
            value={commentText}
            onChange={(e) => setCommentText(e.target.value)}
            placeholder="Add a comment..."
            className="bubble-comment-textarea"
          />
          <div className="bubble-comment-buttons">
            <button onClick={addComment} className="bubble-save-comment">Save</button>
            <button onClick={() => setShowCommentInput(false)} className="bubble-cancel-comment">Cancel</button>
          </div>
        </div>
      )}
    </BubbleMenu>
  );
};

const extensions = [
  Color.configure({ types: [TextStyle.name, ListItem.name] }),
  TextStyle.configure({ types: [ListItem.name] }),
  Underline,
  CommentMark,
  StarterKit.configure({
    bulletList: {
      keepMarks: true,
      keepAttributes: false,
    },
    orderedList: {
      keepMarks: true,
      keepAttributes: false,
    },
  }),
];

// --- Initial Page State ---
const initialPages = [
  {
    id: uuidv4(),
    name: 'Storyboard',
    type: 'file', // Keep type for consistency, though everything is a file now
    content: '<h2>Storyboard Content</h2><p>Initial storyboard content.</p>',
  },
  {
    id: uuidv4(),
    name: 'Chapter 1',
    type: 'file',
    content: '<h2>Chapter 1</h2><p>Start your first chapter here.</p>',
  },
];

// --- Removed recursive helper functions for folders ---

// --- Simplified Add Page function ---
const addPage = (pages, newPage) => {
  return [...pages, newPage];
};

// --- Simplified Rename Page function ---
const renamePage = (pages, pageId, newName) => {
  return pages.map(page => {
    if (page.id === pageId) {
      return { ...page, name: newName };
    }
    return page;
  });
};

// --- Simplified Delete Page function ---
const deletePage = (pages, pageId) => {
  return pages.filter(page => page.id !== pageId);
};

// --- Initial content set from the first default page ---
const initialContent = initialPages[0]?.content || '<p>Select a page from the sidebar.</p>';

export const App = () => {
  const [pages, setPages] = useState(initialPages);
  const [activePageId, setActivePageId] = useState(initialPages[0]?.id || null);
  const [editorContent, setEditorContent] = useState(initialContent);
  const [isChatCollapsed, setIsChatCollapsed] = useState(false); // State for chat collapse

  const editor = useEditor({
    extensions: extensions,
    content: editorContent,
    // Update content when activePageId changes and it's valid
    onUpdate: ({ editor }) => {
        const updatedContent = editor.getHTML();
        setPages(currentPages =>
            currentPages.map(page =>
                page.id === activePageId ? { ...page, content: updatedContent } : page
            )
        );
        setEditorContent(updatedContent); // Keep local editor state sync (optional)
    }
  });

  // Update editor content when active page changes
  useEffect(() => {
    const activePage = pages.find(page => page.id === activePageId);
    const newContent = activePage?.content || '<p>Select a page or create a new one.</p>';
    if (editor && editor.getHTML() !== newContent) { // Avoid unnecessary updates
        // Need to ensure the editor instance is ready before setting content
        // A simple check for editor might suffice, or use editor.isEditable
        editor.commands.setContent(newContent);
    }
    setEditorContent(newContent); // Update local state too
  }, [activePageId, pages, editor]); // Add editor to dependencies

  const handleSelectPage = useCallback((pageId) => { // Renamed handler
    setActivePageId(pageId);
    // Content update is now handled by useEffect
  }, []);

  // --- Removed handleToggleFolder --- 

  const handleAddNewPage = useCallback(() => {
    const newPage = {
      id: uuidv4(),
      name: 'Untitled Page',
      type: 'file',
      content: '<p>Start writing...</p>',
    };
    setPages(prevPages => addPage(prevPages, newPage)); // Use simplified function
    setActivePageId(newPage.id);
    // Content update is now handled by useEffect
  }, []); // Removed editor dependency as useEffect handles content

  // --- Removed handleAddNewFolder --- 

  // --- Rename Handler (Simplified) ---
  const handleRenamePage = useCallback((pageId, newName) => { // Renamed handler
    if (!newName.trim()) return; // Prevent empty names
    setPages(prevPages => renamePage(prevPages, pageId, newName)); // Use simplified function
  }, []);

  // --- Delete Handler (Simplified) ---
  const handleDeletePage = useCallback((pageId) => { // Renamed handler
    console.log(`Attempting to delete page: ${pageId}`);
    let newActivePageId = activePageId;
    const remainingPages = deletePage(pages, pageId); 

    if (activePageId === pageId) {
        // If the active page was deleted, select the first remaining page or null
        newActivePageId = remainingPages.length > 0 ? remainingPages[0].id : null;
        setActivePageId(newActivePageId);
        // Let useEffect handle content update for the new active page
    }
    setPages(remainingPages); // Update the pages state

  }, [activePageId, pages]); // Removed editor dependency

  // Handler to toggle chat collapse state
  const handleToggleChatCollapse = useCallback(() => {
    setIsChatCollapsed(prev => !prev);
  }, []);

  return (
    <div className="app-container">
      <LeftSidebar 
        pages={pages} // Pass pages instead of directoryData
        activePageId={activePageId} // Pass activePageId
        onSelectItem={handleSelectPage} // Pass renamed handler
        // Remove folder-related props: onToggleFolder, onAddNewFolder
        onAddNewPage={handleAddNewPage}
        onRenameItem={handleRenamePage}   // Pass renamed handler
        onDeleteItem={handleDeletePage}   // Pass renamed handler
      />
      <div className="main-content">
        <MenuBar editor={editor} />
        <div className="tiptap-container">
          <EditorContent editor={editor} />
          {editor && <SelectionMenu editor={editor} />}
          {editor && <CommentViewComponent editor={editor} />}
        </div>
      </div>
      <RightChatPanel 
        isCollapsed={isChatCollapsed} 
        onToggleCollapse={handleToggleChatCollapse} 
      />
    </div>
  );
};

export default App;

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

  return (
    <BubbleMenu className="bubble-menu" editor={editor} tippyOptions={{ duration: 100 }}>
      {!showCommentInput ? (
        <button
          onClick={() => setShowCommentInput(true)}
          className="bubble-menu-button"
          title="Add Comment"
        >
          💬
        </button>
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

// --- Initial Directory State ---
const initialDirectoryData = [
  {
    id: uuidv4(),
    name: 'Storyboard',
    type: 'file',
    content: '<h2>Storyboard Content</h2><p>This is the storyboard document.</p>',
  },
  {
    id: uuidv4(),
    name: 'Chapters',
    type: 'folder',
    isOpen: true, // Start open
    children: [
      {
        id: uuidv4(),
        name: 'Chapter 1: The Halter Be...',
        type: 'file',
        content: '<h2>Chapter 1</h2><p>Content for chapter 1.</p>',
      },
      {
        id: uuidv4(),
        name: 'Chapter 2: Brie & Bygones',
        type: 'file',
        content: '<h2>Chapter 2</h2><p>Content for chapter 2.</p>',
      },
      {
        id: uuidv4(),
        name: 'Chapter 3: The Doctor i...',
        type: 'file',
        content: '<h2>Chapter 3</h2><p>Content for chapter 3.</p>',
      },
    ],
  },
];

// --- Helper function to toggle folder state immutably ---
const toggleFolderRecursive = (items, folderId) => {
  return items.map(item => {
    if (item.id === folderId && item.type === 'folder') {
      return { ...item, isOpen: !item.isOpen };
    }
    if (item.type === 'folder' && item.children) {
      return { ...item, children: toggleFolderRecursive(item.children, folderId) };
    }
    return item;
  });
};

// --- Helper function to add item immutably (at root level for now) ---
const addItemToRoot = (items, newItem) => {
  return [...items, newItem];
};

// --- Helper function to rename item immutably ---
const renameItemRecursive = (items, itemId, newName) => {
  return items.map(item => {
    if (item.id === itemId) {
      return { ...item, name: newName };
    }
    if (item.type === 'folder' && item.children) {
      return { ...item, children: renameItemRecursive(item.children, itemId, newName) };
    }
    return item;
  });
};

// --- Helper function to delete item immutably ---
const deleteItemRecursive = (items, itemId) => {
  return items.filter(item => {
    if (item.id === itemId) {
      return false; // Exclude this item
    }
    if (item.type === 'folder' && item.children) {
      item.children = deleteItemRecursive(item.children, itemId);
    }
    return true; // Keep other items
  });
};

// Initial content can be the first file's content or a default
const initialContent = initialDirectoryData.find(item => item.type === 'file')?.content || '<p>Select a file from the sidebar.</p>';

export const App = () => {
  const [directoryData, setDirectoryData] = useState(initialDirectoryData);
  const [activeItemId, setActiveItemId] = useState(initialDirectoryData.find(item => item.type === 'file')?.id || null);
  const [editorContent, setEditorContent] = useState(initialContent);

  const editor = useEditor({
    extensions: extensions,
    content: editorContent,
  });

  const handleSelectItem = useCallback((itemId) => {
    setActiveItemId(itemId);
    let selectedItem = null;
    const findItem = (items) => {
      for (const item of items) {
        if (item.id === itemId) {
          selectedItem = item;
          return true;
        }
        if (item.type === 'folder' && item.children && findItem(item.children)) {
          return true;
        }
      }
      return false;
    };
    findItem(directoryData);

    if (selectedItem && selectedItem.type === 'file') {
      const newContent = selectedItem.content || '<p>This file is empty.</p>';
      if (editor) {
        editor.commands.setContent(newContent);
      }
    }
  }, [directoryData, editor]);

  const handleToggleFolder = useCallback((folderId) => {
    setDirectoryData(prevData => toggleFolderRecursive(prevData, folderId));
  }, []);

  const handleAddNewPage = useCallback(() => {
    const newPage = {
      id: uuidv4(),
      name: 'Untitled Page',
      type: 'file',
      content: '<p>Start writing...</p>',
    };
    setDirectoryData(prevData => addItemToRoot(prevData, newPage));
    setActiveItemId(newPage.id);
    if (editor) {
      editor.commands.setContent(newPage.content);
    }
  }, [editor]);

  const handleAddNewFolder = useCallback(() => {
    const newFolder = {
      id: uuidv4(),
      name: 'New Folder',
      type: 'folder',
      isOpen: true,
      children: [],
    };
    setDirectoryData(prevData => addItemToRoot(prevData, newFolder));
  }, []);

  // --- Rename Handler ---
  const handleRenameItem = useCallback((itemId, newName) => {
    if (!newName.trim()) return; // Prevent empty names
    setDirectoryData(prevData => renameItemRecursive(prevData, itemId, newName));
  }, []);

  // --- Delete Handler ---
  const handleDeleteItem = useCallback((itemId) => {
    // Optional: Add confirmation dialog here
    console.log(`Attempting to delete item: ${itemId}`);
    setDirectoryData(prevData => {
        const newData = deleteItemRecursive(prevData, itemId);
        // If the deleted item was the active one, deactivate/load default
        if (activeItemId === itemId) {
            setActiveItemId(null);
            setEditorContent('<p>Select a file or create a new one.</p>');
            if(editor) editor.commands.setContent('<p>Select a file or create a new one.</p>');
        }
        return newData;
    });

  }, [activeItemId, editor]); // Include activeItemId and editor dependencies

  return (
    <div className="app-container">
      <LeftSidebar 
        directoryData={directoryData}
        activeItemId={activeItemId}
        onSelectItem={handleSelectItem}
        onToggleFolder={handleToggleFolder}
        onAddNewPage={handleAddNewPage}
        onAddNewFolder={handleAddNewFolder}
        onRenameItem={handleRenameItem}   // Pass rename handler
        onDeleteItem={handleDeleteItem}   // Pass delete handler
      />
      <div className="main-content">
        <MenuBar editor={editor} />
        <div className="tiptap-container">
          <EditorContent editor={editor} />
          {editor && <SelectionMenu editor={editor} />}
          {editor && <CommentViewComponent editor={editor} />}
        </div>
      </div>
    </div>
  );
};

export default App;

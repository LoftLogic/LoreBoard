import React, { useState, useEffect, useRef } from 'react';

const CommentViewComponent = ({ editor }) => {
  const [activeComment, setActiveComment] = useState(null);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState('');
  const popupRef = useRef(null);

  const findCommentMarkPos = (commentId) => {
    let commentPos = null;
    if (editor) {
      editor.state.doc.descendants((node, pos) => {
        if (node.marks) {
          node.marks.forEach(mark => {
            if (mark.type.name === 'comment' && mark.attrs.id === commentId) {
              commentPos = { from: pos, to: pos + node.nodeSize, mark };
              return false; // Stop iteration
            }
          });
        }
        return !commentPos; // Continue if not found
      });
    }
    return commentPos;
  };

  const updateCommentAttrs = (commentId, newAttrs) => {
    const posInfo = findCommentMarkPos(commentId);
    if (posInfo && editor) {
      const { from, to, mark } = posInfo;
      const updatedAttrs = { ...mark.attrs, ...newAttrs };
      editor.chain().focus()
        .setTextSelection({ from, to })
        .unsetMark('comment') // Remove old mark
        .setMark('comment', updatedAttrs) // Add new mark with updated attrs
        .run();

      // Update the active comment state if it matches the edited one
      if (activeComment && activeComment.id === commentId) {
        setActiveComment(prev => ({ ...prev, ...newAttrs }));
      }
    }
  };

  const deleteComment = (commentId) => {
    const posInfo = findCommentMarkPos(commentId);
    if (posInfo && editor) {
      const { from, to } = posInfo;
      editor.chain().focus()
        .setTextSelection({ from, to })
        .unsetMark('comment')
        .run();
      setActiveComment(null); // Close the popup
    }
  };

  const handleEdit = () => {
    if (activeComment) {
      updateCommentAttrs(activeComment.id, { text: editText });
      setIsEditing(false);
    }
  };

  const toggleResolve = () => {
    if (activeComment) {
      const newResolvedState = !activeComment.resolved;
      updateCommentAttrs(activeComment.id, { resolved: newResolvedState });
      // Update local state immediately for responsiveness
      setActiveComment(prev => ({ ...prev, resolved: newResolvedState }));
    }
  };

  useEffect(() => {
    if (!editor) return;

    const handleClick = (event) => {
      const target = event.target.closest('.comment'); // Find closest comment span
      if (target) {
        const commentId = target.getAttribute('data-comment-id');
        const commentText = target.getAttribute('data-comment-text');
        const commentAuthor = target.getAttribute('data-comment-author') || 'Anonymous';
        const commentResolved = target.hasAttribute('data-comment-resolved');
        const commentCreatedAt = target.getAttribute('data-comment-created-at');

        if (commentId && commentText) {
          const rect = target.getBoundingClientRect();
          setPosition({
            top: rect.bottom + window.scrollY + 5, // Add some offset
            left: rect.left + window.scrollX
          });
          setActiveComment({ 
            id: commentId, 
            text: commentText, 
            author: commentAuthor,
            resolved: commentResolved,
            createdAt: commentCreatedAt ? new Date(commentCreatedAt) : new Date()
          });
          setEditText(commentText);
          setIsEditing(false); // Close edit mode if opening a new comment
        }
      } else {
        // Click outside a comment span, potentially close popup
        if (popupRef.current && !popupRef.current.contains(event.target)) {
          setActiveComment(null);
          setIsEditing(false);
        }
      }
    };

    const handleUpdate = () => {
        // Potentially refresh comment data if needed, or close if comment removed
        if (activeComment) {
            const posInfo = findCommentMarkPos(activeComment.id);
            if (!posInfo) {
                // The mark associated with the active comment no longer exists
                setActiveComment(null);
                setIsEditing(false);
            } else {
                // Optionally refresh data from mark attributes if external changes are possible
                // setActiveComment(prev => ({ ...prev, ...posInfo.mark.attrs }));
            }
        }
    };

    // Listen for clicks on the editor content area
    const editorDom = editor.view.dom;
    editorDom.addEventListener('click', handleClick);
    editor.on('update', handleUpdate);

    return () => {
      editorDom.removeEventListener('click', handleClick);
      editor.off('update', handleUpdate);
    };
  }, [editor, activeComment]); // Re-run if activeComment changes to check outside clicks

  // Handle clicking outside the popup (redundant with editor click but ensures closure)
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (popupRef.current && !popupRef.current.contains(event.target) && 
          !event.target.closest('.comment')) { // Don't close if clicking on another comment
        setActiveComment(null);
        setIsEditing(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []); // Empty dependency array, runs once

  if (!activeComment) return null;

  const formatDate = (date) => {
    return date.toLocaleString(undefined, {
      dateStyle: 'short',
      timeStyle: 'short'
    });
  };

  return (
    <div
      className={`comment-view-popup ${activeComment.resolved ? 'resolved' : ''}`}
      style={{
        position: 'absolute',
        top: `${position.top}px`,
        left: `${position.left}px`,
        zIndex: 50
      }}
      ref={popupRef}
    >
      <div className="comment-header">
        <span>{activeComment.author}</span>
        <span className="comment-timestamp">{formatDate(activeComment.createdAt)}</span>
      </div>

      {!isEditing ? (
        <div className="comment-view-content">
          {activeComment.text}
        </div>
      ) : (
        <div className="comment-edit-content">
          <textarea
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            className="comment-edit-textarea"
          />
        </div>
      )}

      <div className="comment-actions">
        {isEditing ? (
          <>
            <button onClick={handleEdit} className="comment-action-button save">Save</button>
            <button onClick={() => setIsEditing(false)} className="comment-action-button cancel">Cancel</button>
          </>
        ) : (
          <>
            <button onClick={() => setIsEditing(true)} className="comment-action-button edit" title="Edit">✏️</button>
            <button onClick={toggleResolve} className="comment-action-button resolve" title={activeComment.resolved ? "Unresolve" : "Resolve"}>
              {activeComment.resolved ? '↩️' : '✔️'}
            </button>
            <button onClick={() => deleteComment(activeComment.id)} className="comment-action-button delete" title="Delete">🗑️</button>
          </>
        )}
      </div>
    </div>
  );
};

export default CommentViewComponent; 
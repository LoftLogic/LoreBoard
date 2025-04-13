import React, { useState, useEffect, useRef } from 'react';
import { useCurrentEditor } from '@tiptap/react';

const CommentViewComponent = () => {
  const { editor } = useCurrentEditor();
  const [hoverComment, setHoverComment] = useState(null);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  
  useEffect(() => {
    if (!editor) return;
    
    const handleMouseOver = (event) => {
      const target = event.target;
      if (target.classList.contains('comment')) {
        const commentId = target.getAttribute('data-comment-id');
        const commentText = target.getAttribute('data-comment-text');
        
        if (commentId && commentText) {
          const rect = target.getBoundingClientRect();
          setPosition({ 
            top: rect.bottom + window.scrollY,
            left: rect.left + window.scrollX
          });
          setHoverComment({ id: commentId, text: commentText });
        }
      }
    };
    
    const handleMouseOut = (event) => {
      const relatedTarget = event.relatedTarget;
      // Don't hide the comment popup if moving from the comment to the popup
      if (relatedTarget && relatedTarget.closest('.comment-view-popup')) {
        return;
      }
      
      // Otherwise, hide the popup
      setHoverComment(null);
    };
    
    // Add event listeners to all comment elements
    const addEventListeners = () => {
      const commentElements = editor.view.dom.querySelectorAll('.comment');
      commentElements.forEach(element => {
        element.addEventListener('mouseover', handleMouseOver);
        element.addEventListener('mouseout', handleMouseOut);
      });
    };
    
    // Initial setup
    addEventListeners();
    
    // Update listeners when editor updates
    const handleUpdate = () => {
      // Small delay to ensure DOM is updated
      setTimeout(addEventListeners, 100);
    };
    
    editor.on('update', handleUpdate);
    
    return () => {
      editor.off('update', handleUpdate);
      const commentElements = editor.view.dom.querySelectorAll('.comment');
      commentElements.forEach(element => {
        element.removeEventListener('mouseover', handleMouseOver);
        element.removeEventListener('mouseout', handleMouseOut);
      });
    };
  }, [editor]);
  
  const popupRef = useRef(null);
  
  // Handle clicking outside the popup
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (popupRef.current && !popupRef.current.contains(event.target) && 
          !event.target.classList.contains('comment')) {
        setHoverComment(null);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);
  
  if (!hoverComment) return null;
  
  return (
    <div 
      className="comment-view-popup"
      style={{
        position: 'absolute',
        top: `${position.top}px`,
        left: `${position.left}px`,
        zIndex: 50
      }}
      ref={popupRef}
    >
      <div className="comment-view-content">
        {hoverComment.text}
      </div>
    </div>
  );
};

export default CommentViewComponent; 
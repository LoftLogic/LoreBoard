import React, { useState, useEffect, useRef } from 'react';

const RightChatPanel = ({ isCollapsed, onToggleCollapse }) => {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState([]); // Now stores message objects { sender: 'user'|'ai', text: '...'}
  const [showContextPlaceholder, setShowContextPlaceholder] = useState(false); // State for placeholder visibility
  const messagesEndRef = useRef(null); // Ref for scrolling

  // Function to scroll to the bottom of the messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }

  // Scroll to bottom whenever messages update
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    const text = inputValue.trim();
    if (text) {
      const newUserMessage = { sender: 'user', text: text };
      const aiResponse = { sender: 'ai', text: 'Temporary Response' }; // AI's temporary response

      // Update state with both user message and AI response
      setMessages(prevMessages => [...prevMessages, newUserMessage, aiResponse]);
      setInputValue(''); // Clear input after sending
      setShowContextPlaceholder(false); // Hide placeholder when sending message
      // Placeholder: Trigger actual AI response logic here in the future
    }
  };

  const handleAddContext = () => {
    setShowContextPlaceholder(prev => !prev); // Toggle placeholder visibility
    // Placeholder: Implement actual context selection UI later
  };

  return (
    <div className={`right-chat-panel ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header chat-header">
        {!isCollapsed && <span>AI Chat</span>}
        <button
          onClick={onToggleCollapse}
          className="collapse-button"
          title={isCollapsed ? "Expand Chat" : "Collapse Chat"}
        >
          {isCollapsed ? '«' : '»'}
        </button>
      </div>

      {!isCollapsed && (
        <>
          <div className="chat-messages">
            {messages.map((message, index) => (
              <div key={index} className={`chat-message ${message.sender === 'user' ? 'user-message' : 'ai-message'}`}>
                <p>{message.text}</p>
              </div>
            ))}
            <div ref={messagesEndRef} /> {/* Invisible element to scroll to */}
          </div>
          <div className="chat-input-area">
            <button onClick={handleAddContext} className="add-context-button" title="Add Context">
              +
            </button>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask LoreBoard AI..."
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleSendMessage();
                }
              }}
              onClick={() => setShowContextPlaceholder(false)} // Hide placeholder when clicking input
            />
            <button onClick={handleSendMessage} className="send-message-button" title="Send Message">
              ➤
            </button>
          </div>
          {showContextPlaceholder && (
            <div className="context-placeholder">
              Context options will be added later.
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default RightChatPanel; 
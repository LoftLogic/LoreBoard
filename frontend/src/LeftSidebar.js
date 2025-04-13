import React, { useState, useEffect, useRef } from 'react';

// --- Context Menu Component ---
const ContextMenu = ({ x, y, itemId, onRename, onDelete, onClose }) => {
  const menuRef = useRef(null);

  // Close menu if clicked outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        onClose();
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [onClose]);

  return (
    <div 
      ref={menuRef}
      className="context-menu"
      style={{ top: `${y}px`, left: `${x}px` }}
    >
      <ul>
        <li onClick={() => { onRename(itemId); onClose(); }}>Rename</li>
        <li onClick={() => { onDelete(itemId); onClose(); }}>Delete</li>
      </ul>
    </div>
  );
};

// --- Recursive component to render directory items ---
const DirectoryItem = ({ item, activeItemId, onSelectItem, onToggleFolder, onRenameItem, onDeleteItem, level = 0 }) => {
  const isFolder = item.type === 'folder';
  const isActive = item.id === activeItemId;
  const [isRenaming, setIsRenaming] = useState(false);
  const [renameValue, setRenameValue] = useState(item.name);
  const inputRef = useRef(null); // Ref for the input field
  
  // Context Menu State
  const [contextMenu, setContextMenu] = useState(null);

  const handleItemClick = (event) => {
    // Prevent click from propagating when renaming
    if (isRenaming || (event.target.tagName === 'INPUT')) return; 
    
    if (contextMenu) {
        setContextMenu(null); // Close context menu on left click
    }

    if (isFolder) {
      onToggleFolder(item.id);
    } else {
      onSelectItem(item.id);
    }
  };

  const handleRename = () => {
    if (renameValue.trim() !== item.name) {
      onRenameItem(item.id, renameValue.trim());
    }
    setIsRenaming(false);
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleRename();
    } else if (event.key === 'Escape') {
      setRenameValue(item.name); // Revert changes
      setIsRenaming(false);
    }
  };

  // Focus input when renaming starts
  useEffect(() => {
    if (isRenaming && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select(); // Select text for easy replacement
    }
  }, [isRenaming]);
  
   // --- Context Menu Handlers ---
  const handleContextMenu = (event) => {
    event.preventDefault(); // Prevent native context menu
    setContextMenu({ x: event.clientX, y: event.clientY });
  };

  const closeContextMenu = () => {
    setContextMenu(null);
  };

  const startRename = () => {
    setIsRenaming(true);
    setRenameValue(item.name);
    closeContextMenu(); // Close menu when starting rename
  };

  return (
    <>
      <li 
        className={`directory-item ${isActive ? 'active' : ''} ${isFolder ? 'folder' : 'file'}`}
        style={{ paddingLeft: `${level * 20 + 10}px` }}
        onClick={handleItemClick}
        onContextMenu={handleContextMenu} // Add context menu handler
        title={item.name}
      >
        {/* Folder Arrow */} 
        {isFolder && (
          <span className="folder-arrow">{item.isOpen ? '▼' : '▶'}</span>
        )}
        {/* Icon */} 
        <span className="item-icon">{isFolder ? '📁' : '📄'}</span>
        {/* Name or Input Field */} 
        {isRenaming ? (
          <input
            ref={inputRef}
            type="text"
            className="rename-input"
            value={renameValue}
            onChange={(e) => setRenameValue(e.target.value)}
            onBlur={handleRename} // Save when input loses focus
            onKeyDown={handleKeyDown}
            onClick={(e) => e.stopPropagation()} // Prevent click closing rename
          />
        ) : (
          <span className="item-name">{item.name}</span>
        )}
      </li>
      {/* Render children recursively */} 
      {isFolder && item.isOpen && item.children && (
        <ul className="directory-list nested">
          {item.children.map(child => (
            <DirectoryItem 
              key={child.id} 
              item={child} 
              activeItemId={activeItemId} 
              onSelectItem={onSelectItem}
              onToggleFolder={onToggleFolder}
              onRenameItem={onRenameItem} // Pass down handlers
              onDeleteItem={onDeleteItem}
              level={level + 1}
            />
          ))}
        </ul>
      )}
      {/* Render Context Menu */} 
      {contextMenu && (
        <ContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          itemId={item.id}
          onRename={startRename} // Call startRename
          onDelete={onDeleteItem} // Pass directly
          onClose={closeContextMenu}
        />
      )}
    </>
  );
};

const LeftSidebar = ({ directoryData, activeItemId, onSelectItem, onToggleFolder, onAddNewPage, onAddNewFolder, onRenameItem, onDeleteItem }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <div className={`left-sidebar ${isCollapsed ? 'collapsed' : ''}`}>
       <div className="sidebar-header">
        {!isCollapsed && <span>Tutorial Project</span>} 
        <button onClick={toggleCollapse} className="collapse-button" title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}>
          {isCollapsed ? '»' : '«'}
        </button>
      </div>

      {!isCollapsed && (
        <>
          <div className="sidebar-actions">
            <button className="sidebar-button" onClick={onAddNewPage}>＋ New Page</button>
            <button className="sidebar-button" onClick={onAddNewFolder}>＋ New Folder</button>
          </div>

          <div className="sidebar-content">
            <ul className="directory-list">
              {directoryData.map(item => (
                <DirectoryItem 
                  key={item.id}
                  item={item}
                  activeItemId={activeItemId}
                  onSelectItem={onSelectItem}
                  onToggleFolder={onToggleFolder}
                  onRenameItem={onRenameItem} // Pass down rename
                  onDeleteItem={onDeleteItem} // Pass down delete
                />
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
};

export default LeftSidebar; 
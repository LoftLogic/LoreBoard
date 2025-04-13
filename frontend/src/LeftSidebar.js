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

// --- Simplified component to render page items ---
const PageItem = ({ item, activePageId, onSelectItem, onRenameItem, onDeleteItem }) => {
  const isActive = item.id === activePageId;
  const [isRenaming, setIsRenaming] = useState(false);
  const [renameValue, setRenameValue] = useState(item.name);
  const inputRef = useRef(null);
  const [contextMenu, setContextMenu] = useState(null);

  const handleItemClick = (event) => {
    if (isRenaming || (event.target.tagName === 'INPUT')) return; 
    if (contextMenu) {
        setContextMenu(null);
    }
    onSelectItem(item.id);
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
      setRenameValue(item.name);
      setIsRenaming(false);
    }
  };

  useEffect(() => {
    if (isRenaming && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isRenaming]);
  
  const handleContextMenu = (event) => {
    event.preventDefault();
    setContextMenu({ x: event.clientX, y: event.clientY });
  };

  const closeContextMenu = () => {
    setContextMenu(null);
  };

  const startRename = () => {
    setIsRenaming(true);
    setRenameValue(item.name);
    closeContextMenu();
  };

  return (
    <>
      <li 
        className={`directory-item ${isActive ? 'active' : ''} file`}
        onClick={handleItemClick}
        onContextMenu={handleContextMenu}
        title={item.name}
      >
        <span className="item-icon">📄</span>
        {isRenaming ? (
          <input
            ref={inputRef}
            type="text"
            className="rename-input"
            value={renameValue}
            onChange={(e) => setRenameValue(e.target.value)}
            onBlur={handleRename}
            onKeyDown={handleKeyDown}
            onClick={(e) => e.stopPropagation()}
          />
        ) : (
          <span className="item-name">{item.name}</span>
        )}
      </li>
      {contextMenu && (
        <ContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          itemId={item.id}
          onRename={startRename}
          onDelete={onDeleteItem}
          onClose={closeContextMenu}
        />
      )}
    </>
  );
};

const SidebarItem = ({ item, level = 0, activePageId, onSelectItem, onRenameItem, onDeleteItem, onEntityClick }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [newName, setNewName] = useState(item.name);
  const [itemType, setItemType] = useState(item.type || 'page'); // Assume 'page' if type is missing
  const [selectedEntity, setSelectedEntity] = useState(null); // Use this state

  const handleSelect = () => {
    if (itemType === 'page') { // Only select pages for now
      onSelectItem(item.id);
    } else if (onEntityClick) { // If it's an entity and handler exists, call it
      onEntityClick(item);
    }
  };

  const handleRename = () => {
    if (isEditing && newName.trim() !== item.name) {
      onRenameItem(item.id, newName.trim(), itemType);
    }
    setIsEditing(!isEditing);
  };

  const handleDelete = (e) => {
    e.stopPropagation(); // Prevent selection when clicking delete
    if (window.confirm(`Are you sure you want to delete "${item.name}"?`)) {
      onDeleteItem(item.id, itemType);
    }
  };

  const handleNameChange = (e) => {
    setNewName(e.target.value);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleRename();
    } else if (e.key === 'Escape') {
      setNewName(item.name);
      setIsEditing(false);
    }
  };

  // Determine icon based on type
  let icon = '📄'; // Default page icon
  if (itemType === 'character') icon = '🧑';
  else if (itemType === 'place') icon = '🏞️';
  else if (itemType === 'item') icon = '🗡️';

  const isActive = activePageId === item.id && itemType === 'page';

  const handleEntityClick = (entity) => {
    // We need the full entity details here, not just the summary.
    // For now, we'll fetch them again when clicked.
    // This is inefficient - ideally App.js fetches full details initially
    // or provides a function to fetch details on demand.
    // --- Temporary Fetch (Placeholder for better strategy) ---
    const fetchFullEntityDetails = async (entityId, entityType) => {
      try {
        const response = await fetch(`http://localhost:8000/api/entities/${entityType}/${entityId}`);
        if (!response.ok) throw new Error('Failed to fetch details');
        const fullData = await response.json();
        console.log("Fetched full entity details:", fullData);
        setSelectedEntity({ ...entity, ...fullData }); // Merge summary with full data
        setShowEntityPopup(true);
      } catch (error) {
        console.error("Error fetching full entity details:", error);
        // Fallback: Show popup with potentially limited info from props
        setSelectedEntity(entity);
        setShowEntityPopup(true);
      }
    };
    // --- End Temporary Fetch ---
    
    fetchFullEntityDetails(entity.id, entity.type);
    // Original simpler logic (if props contained full details):
    // setSelectedEntity(entity);
    // setShowEntityPopup(true);
  };

  return (
    <div
      className={`sidebar-item ${isActive ? 'active' : ''} ${isEditing ? 'editing' : ''}`}
      style={{ paddingLeft: `${level * 15 + 10}px` }}
      onClick={handleSelect}
    >
      <span className="sidebar-item-icon">{icon}</span>
      {isEditing ? (
        <input
          type="text"
          value={newName}
          onChange={handleNameChange}
          onBlur={handleRename} // Save on blur
          onKeyDown={handleKeyDown}
          autoFocus
          className="sidebar-item-input"
          onClick={(e) => e.stopPropagation()} // Prevent selection when clicking input
        />
      ) : (
        <span className="sidebar-item-name" onDoubleClick={() => setIsEditing(true)}>
          {item.name}
        </span>
      )}
      {(itemType === 'page') && ( // Only show delete for pages for now
          <button className="sidebar-item-delete" onClick={handleDelete} title="Delete">×</button>
      )}
      {/* Add rename/delete for entities later if needed */}
    </div>
  );
};

const LeftSidebar = ({
  pages,
  characters,
  places,
  items,
  activePageId,
  onSelectItem,
  onAddNewPage,
  onRenameItem,
  onDeleteItem
}) => {
  // Log props on every render
  console.log('LeftSidebar receiving props:', { characters, places, items });

  const [isCollapsed, setIsCollapsed] = useState(false);
  const [showEntityPopup, setShowEntityPopup] = useState(false);
  const [selectedEntity, setSelectedEntity] = useState(null);

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
    if (isCollapsed) {
      setShowEntityPopup(false);
      setSelectedEntity(null);
    }
  };

  const handleEntityClick = (entity) => {
    const fetchFullEntityDetails = async (entityId, entityType) => {
      try {
        const response = await fetch(`http://localhost:8000/api/entities/${entityType}/${entityId}`);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Failed to fetch details: ${errorData.detail || response.statusText}`);
        }
        const fullData = await response.json();
        console.log("Fetched full entity details:", fullData);
        setSelectedEntity({ ...entity, ...fullData });
        setShowEntityPopup(true);
      } catch (error) {
        console.error("Error fetching full entity details:", error);
        setSelectedEntity(entity);
        setShowEntityPopup(true);
      }
    };
    fetchFullEntityDetails(entity.id, entity.type);
  };

  const closeEntityPopup = () => {
    setShowEntityPopup(false);
    setSelectedEntity(null);
  }

  const renderEntityFields = (entity) => {
    if (!entity) return null;

    const fieldsToShow = {};
    switch (entity.type) {
      case 'character':
        fieldsToShow['Physical'] = entity.physical;
        fieldsToShow['Personality'] = entity.personality;
        fieldsToShow['Background'] = entity.background;
        fieldsToShow['Goals'] = entity.goals;
        fieldsToShow['Relationships'] = entity.relationships;
        break;
      case 'place':
        fieldsToShow['Physical Description'] = entity.physical;
        fieldsToShow['Environment'] = entity.environment;
        fieldsToShow['Purpose/Significance'] = entity.purpose;
        fieldsToShow['History'] = entity.history;
        fieldsToShow['Location'] = entity.location;
        break;
      case 'item':
        fieldsToShow['Physical Description'] = entity.physical;
        fieldsToShow['Function/Abilities'] = entity.function;
        fieldsToShow['Origin'] = entity.origin;
        fieldsToShow['Ownership'] = entity.ownership;
        fieldsToShow['Properties'] = entity.properties;
        break;
      default:
        return <p>Unknown entity type.</p>;
    }

    return (
      <div className="entity-fields-container">
        {Object.entries(fieldsToShow).map(([label, value]) => (
          (value !== undefined && value !== null && value !== "") && (
            <div key={label} className="entity-field">
              <span className="field-label">{label}:</span>
              <span className="field-value">{value || '-'}</span>
            </div>
          )
        ))}
      </div>
    );
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
          </div>

          <div className="sidebar-content">
            {/* Pages Section */}
            <div className="sidebar-section">
              <div className="sidebar-section-header">
                <h3>Pages</h3>
              </div>
              {pages.map(page => (
                <SidebarItem
                  key={page.id}
                  item={{...page, type: 'page'}} // Ensure type is page
                  level={0}
                  activePageId={activePageId}
                  onSelectItem={onSelectItem}
                  onRenameItem={(id, newName) => onRenameItem(id, newName, 'page')} // Specify type
                  onDeleteItem={(id) => onDeleteItem(id, 'page')} // Specify type
                />
              ))}
            </div>

            {/* Characters Section */}
            <div className="sidebar-section">
              <div className="sidebar-section-header">
                <h3>Characters</h3>
              </div>
              {characters.map(char => (
                <SidebarItem
                  key={char.id}
                  item={{...char, type: 'character'}} // Assign type
                  level={0}
                  activePageId={activePageId} // Pass down but item won't be active unless selected
                  onSelectItem={() => handleEntityClick(char)} // Use handleEntityClick for selection
                  onRenameItem={(id, newName) => onRenameItem(id, newName, 'character')} // Specify type
                  onDeleteItem={(id) => onDeleteItem(id, 'character')} // Specify type
                />
              ))}
            </div>

            {/* Places Section */}
            <div className="sidebar-section">
              <div className="sidebar-section-header">
                <h3>Places</h3>
              </div>
              {places.map(place => (
                <SidebarItem
                  key={place.id}
                  item={{...place, type: 'place'}} // Assign type
                  level={0}
                  activePageId={activePageId}
                  onSelectItem={() => handleEntityClick(place)} // Use handleEntityClick for selection
                  onRenameItem={(id, newName) => onRenameItem(id, newName, 'place')} // Specify type
                  onDeleteItem={(id) => onDeleteItem(id, 'place')} // Specify type
                />
              ))}
            </div>

            {/* Items Section */}
            <div className="sidebar-section">
              <div className="sidebar-section-header">
                <h3>Items</h3>
              </div>
              {items.map(item => (
                <SidebarItem
                  key={item.id}
                  item={{...item, type: 'item'}} // Assign type
                  level={0}
                  activePageId={activePageId}
                  onSelectItem={() => handleEntityClick(item)} // Use handleEntityClick for selection
                  onRenameItem={(id, newName) => onRenameItem(id, newName, 'item')} // Specify type
                  onDeleteItem={(id) => onDeleteItem(id, 'item')} // Specify type
                />
              ))}
            </div>
          </div>
        </>
      )}

      {/* Entity Detail Popup */}
      {showEntityPopup && !isCollapsed && selectedEntity && (
        <div className="entity-popup-overlay" onClick={closeEntityPopup}>
          <div className="entity-popup-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-popup-button" onClick={closeEntityPopup}>×</button>
            <h2>{selectedEntity.name} ({selectedEntity.type})</h2>
            {renderEntityFields(selectedEntity)}
          </div>
        </div>
      )}
    </div>
  );
};

export default LeftSidebar; 
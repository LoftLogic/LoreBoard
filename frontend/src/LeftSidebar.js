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

const LeftSidebar = ({ pages, activePageId, onSelectItem, onAddNewPage, onRenameItem, onDeleteItem }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [showEntityPopup, setShowEntityPopup] = useState(false);
  const [selectedEntity, setSelectedEntity] = useState(null); // Use this state

  // Sample Entities with more details
  const sampleCharacter = {
    id: 'char1', name: 'Heroic Knight', type: 'character',
    physical: "Tall, broad-shouldered, scar across left eye, wears shining plate armor.",
    personality: "Brave, stoic, honorable, but secretly doubts his own courage.",
    background: "Second son of a minor lord, trained from youth in combat.",
    goals: "Protect the kingdom, uphold his family honor.",
    relationships: "Loyal to the King, mentors a young squire."
  };
  const samplePlace = {
    id: 'place1', name: 'Mystic Forest', type: 'place',
    physical: "Ancient trees with glowing moss, twisting paths, hidden clearings.",
    environment: "Perpetual twilight, air thick with magic, strange animal calls.",
    purpose: "Source of potent herbs, home to elusive magical creatures.",
    history: "Site of an old druidic civilization, rumored to be cursed.",
    location: "Bordering the northern mountains, difficult to navigate."
  };
  const sampleItem = {
    id: 'item1', name: 'Enchanted Sword', type: 'item',
    physical: "Gleaming silver blade, hilt wrapped in worn blue leather, emits a faint hum.",
    function: "Cuts through magical barriers, glows when danger is near.",
    origin: "Forged by ancient elves, lost for centuries.",
    ownership: "Currently wielded by the Heroic Knight.",
    properties: "Unbreakable, enhances wielder's speed."
  };

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
    if (isCollapsed) {
      setShowEntityPopup(false);
      setSelectedEntity(null);
    }
  };

  const handleEntityClick = (entity) => {
    setSelectedEntity(entity);
    setShowEntityPopup(true);
    // console.log("Clicked entity:", entity); // Keep for debugging if needed
  };

  const closeEntityPopup = () => {
    setShowEntityPopup(false);
    setSelectedEntity(null);
  }

  // Helper function to render fields
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
          <div key={label} className="entity-field">
            <span className="field-label">{label}:</span>
            <span className="field-value">{value || '-'}</span> {/* Show '-' if value is empty */}
          </div>
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
            <h4 className="sidebar-section-header">Pages</h4>
            <ul className="directory-list">
              {pages.map(page => (
                <PageItem
                  key={page.id}
                  item={page}
                  activePageId={activePageId}
                  onSelectItem={onSelectItem}
                  onRenameItem={onRenameItem}
                  onDeleteItem={onDeleteItem}
                />
              ))}
            </ul>

            {/* Characters Section */}
            <h4 className="sidebar-section-header">Characters</h4>
            <ul className="directory-list">
              <li className="directory-item entity" onClick={() => handleEntityClick(sampleCharacter)}>
                <span className="item-icon">🧑</span> {/* Example icon */}
                <span className="item-name">{sampleCharacter.name}</span>
              </li>
              {/* Add more characters here */}
            </ul>

            {/* Places Section */}
            <h4 className="sidebar-section-header">Places</h4>
            <ul className="directory-list">
               <li className="directory-item entity" onClick={() => handleEntityClick(samplePlace)}>
                 <span className="item-icon">🏞️</span> {/* Example icon */}
                 <span className="item-name">{samplePlace.name}</span>
               </li>
              {/* Add more places here */}
            </ul>

            {/* Items Section */}
            <h4 className="sidebar-section-header">Items</h4>
            <ul className="directory-list">
              <li className="directory-item entity" onClick={() => handleEntityClick(sampleItem)}>
                <span className="item-icon">🗡️</span> {/* Example icon */}
                <span className="item-name">{sampleItem.name}</span>
              </li>
              {/* Add more items here */}
            </ul>
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
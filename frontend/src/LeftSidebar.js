import React, { useState } from 'react';

const LeftSidebar = () => {
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
            <button className="sidebar-button">＋ New Page</button>
            <button className="sidebar-button">＋ New Folder</button>
            {/* <button className="sidebar-button">↓ Import</button> */}
          </div>

          <div className="sidebar-content">
            {/* Placeholder for directory structure */}
            <ul className="directory-list">
              <li>📄 Introduction</li>
              <li>📁 Tutorial</li>
              <ul className="nested">
                 <li>📄 Chapter 1: The Halter Be...</li>
                 <li>📄 Chapter 2: Brie & Bygones</li>
                 <li>📄 Chapter 3: The Doctor i...</li>
              </ul>
              {/* Add more items as needed */}
            </ul>
          </div>
        </>
      )}
    </div>
  );
};

export default LeftSidebar; 
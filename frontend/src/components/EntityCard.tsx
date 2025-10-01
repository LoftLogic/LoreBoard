import React from 'react';
import { Entity, EntityType } from '../types/index';

interface EntityCardProps {
  entity: Entity;
  onClick?: (entity: Entity) => void;
  onEdit?: (entity: Entity) => void;
  onDelete?: (entity: Entity) => void;
  isSelected?: boolean;
}

/**
 * EntityCard Component
 * 
 * Displays an entity in a card format with rich purple styling.
 * Shows entity name, type, description, and key attributes.
 * 
 * @param entity - The entity data to display
 * @param onClick - Handler for card click
 * @param onEdit - Handler for edit action
 * @param onDelete - Handler for delete action
 * @param isSelected - Whether the card is currently selected
 */
export const EntityCard: React.FC<EntityCardProps> = ({
  entity,
  onClick,
  onEdit,
  onDelete,
  isSelected = false
}) => {
  // Get entity type color
  const getTypeColor = (type: EntityType): string => {
    const colors = {
      [EntityType.CHARACTER]: 'bg-loreboard-500',
      [EntityType.LOCATION]: 'bg-accent-teal',
      [EntityType.ITEM]: 'bg-accent-gold',
      [EntityType.EVENT]: 'bg-loreboard-600',
      [EntityType.CUSTOM]: 'bg-loreboard-400'
    };
    return colors[type] || 'bg-loreboard-400';
  };

  // Get entity type icon
  const getTypeIcon = (type: EntityType): string => {
    const icons = {
      [EntityType.CHARACTER]: '👤',
      [EntityType.LOCATION]: '📍',
      [EntityType.ITEM]: '🎁',
      [EntityType.EVENT]: '📅',
      [EntityType.CUSTOM]: '📝'
    };
    return icons[type] || '📝';
  };

  return (
    <div
      className={`
        bg-gradient-to-br from-loreboard-50 to-white 
        rounded-xl shadow-md p-4 border border-loreboard-200 
        hover:shadow-purple-glow transition-all duration-300 
        cursor-pointer transform hover:-translate-y-1
        ${isSelected ? 'ring-2 ring-loreboard-500' : ''}
      `}
      onClick={() => onClick?.(entity)}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{getTypeIcon(entity.type)}</span>
          <h3 className="text-lg font-semibold text-gray-900 line-clamp-1">
            {entity.name}
          </h3>
        </div>
        
        {/* Actions */}
        <div className="flex gap-1">
          {onEdit && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onEdit(entity);
              }}
              className="text-loreboard-600 hover:bg-loreboard-100 p-1 rounded transition-colors"
              aria-label="Edit entity"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
          )}
          {onDelete && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(entity);
              }}
              className="text-accent-rose hover:bg-red-50 p-1 rounded transition-colors"
              aria-label="Delete entity"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Type Badge */}
      <span className={`
        inline-block px-3 py-1 rounded-full text-xs font-medium text-white mb-2
        ${getTypeColor(entity.type)}
      `}>
        {entity.type}
      </span>

      {/* Description */}
      {entity.description && (
        <p className="text-sm text-gray-600 line-clamp-2 mb-3">
          {entity.description}
        </p>
      )}

      {/* Key Attributes */}
      {entity.attributes && Object.keys(entity.attributes).length > 0 && (
        <div className="space-y-1">
          {Object.entries(entity.attributes).slice(0, 3).map(([key, value]) => (
            <div key={key} className="flex items-center gap-2 text-xs">
              <span className="font-medium text-loreboard-700 capitalize">
                {key}:
              </span>
              <span className="text-gray-600 truncate">
                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
              </span>
            </div>
          ))}
          {Object.keys(entity.attributes).length > 3 && (
            <span className="text-xs text-loreboard-600">
              +{Object.keys(entity.attributes).length - 3} more
            </span>
          )}
        </div>
      )}

      {/* Relationship Count (if available) */}
      {entity.relationships && entity.relationships.length > 0 && (
        <div className="mt-3 pt-3 border-t border-loreboard-100">
          <span className="text-xs text-loreboard-600">
            {entity.relationships.length} relationship{entity.relationships.length !== 1 ? 's' : ''}
          </span>
        </div>
      )}
    </div>
  );
};

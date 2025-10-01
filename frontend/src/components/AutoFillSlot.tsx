import React, { useState, useRef, useEffect } from 'react';
import { AutoFillSlot as AutoFillSlotType } from '../types/index';
import { llmApi } from '@services/api';

interface AutoFillSlotProps {
  slot: AutoFillSlotType;
  onFill: (slotId: string, text: string) => void;
  onCancel: () => void;
}

/**
 * AutoFillSlot Component
 * 
 * Provides an inline interface for auto-completing text slots.
 * Shows AI-generated suggestions in a dropdown with purple theme.
 * 
 * @param slot - The auto-fill slot data
 * @param onFill - Handler when slot is filled
 * @param onCancel - Handler when auto-fill is cancelled
 */
export const AutoFillSlot: React.FC<AutoFillSlotProps> = ({
  slot,
  onFill,
  onCancel
}) => {
  const [suggestions, setSuggestions] = useState<string[]>(slot.suggestions || []);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [customInput, setCustomInput] = useState('');
  const [showCustom, setShowCustom] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Load suggestions if not already loaded
    if (!slot.suggestions || slot.suggestions.length === 0) {
      loadSuggestions();
    }
  }, [slot]);

  useEffect(() => {
    // Focus input when showing custom
    if (showCustom && inputRef.current) {
      inputRef.current.focus();
    }
  }, [showCustom]);

  const loadSuggestions = async () => {
    setIsLoading(true);
    try {
      const newSuggestions = await llmApi.generateAutoFill(slot);
      setSuggestions(newSuggestions);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
      setSuggestions(['[Error loading suggestions]']);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (showCustom) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) => 
          prev < suggestions.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => 
          prev > 0 ? prev - 1 : suggestions.length - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (suggestions[selectedIndex]) {
          onFill(slot.id, suggestions[selectedIndex]);
        }
        break;
      case 'Tab':
        e.preventDefault();
        setShowCustom(true);
        break;
      case 'Escape':
        e.preventDefault();
        onCancel();
        break;
    }
  };

  const handleCustomSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (customInput.trim()) {
      onFill(slot.id, customInput.trim());
    }
  };

  return (
    <div className="inline-block relative">
      {/* Slot indicator */}
      <span className="
        inline-flex items-center px-2 py-1 
        bg-loreboard-100 border-2 border-loreboard-500 
        rounded-lg animate-pulse-soft
      ">
        <span className="text-loreboard-700 font-medium">___</span>
      </span>

      {/* Suggestions dropdown */}
      <div className="
        absolute top-full left-0 mt-2 z-50
        bg-white rounded-xl shadow-2xl border border-loreboard-200
        min-w-[200px] max-w-[400px]
        animate-slide-in
      " onKeyDown={handleKeyDown}>
        
        {/* Loading state */}
        {isLoading && (
          <div className="p-4 text-center">
            <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-loreboard-500"></div>
            <p className="text-sm text-gray-600 mt-2">Generating suggestions...</p>
          </div>
        )}

        {/* Suggestions list */}
        {!isLoading && !showCustom && suggestions.length > 0 && (
          <>
            <div className="p-2">
              <p className="text-xs text-gray-500 mb-2">
                Select a suggestion or press Tab for custom input
              </p>
            </div>
            <ul className="py-1">
              {suggestions.map((suggestion, index) => (
                <li key={index}>
                  <button
                    className={`
                      w-full text-left px-4 py-2 
                      hover:bg-loreboard-50 transition-colors
                      ${selectedIndex === index ? 'bg-loreboard-100 border-l-4 border-loreboard-500' : ''}
                    `}
                    onClick={() => onFill(slot.id, suggestion)}
                    onMouseEnter={() => setSelectedIndex(index)}
                  >
                    <span className="text-gray-900">{suggestion}</span>
                    {selectedIndex === index && (
                      <span className="text-xs text-loreboard-600 ml-2">
                        Press Enter
                      </span>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          </>
        )}

        {/* Custom input */}
        {!isLoading && showCustom && (
          <form onSubmit={handleCustomSubmit} className="p-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Custom text:
            </label>
            <input
              ref={inputRef}
              type="text"
              value={customInput}
              onChange={(e) => setCustomInput(e.target.value)}
              className="
                w-full border-2 border-loreboard-200 
                focus:border-loreboard-500 rounded-lg 
                px-3 py-2 outline-none transition-colors
              "
              placeholder="Type your text..."
            />
            <div className="flex gap-2 mt-3">
              <button
                type="submit"
                className="
                  flex-1 bg-loreboard-500 hover:bg-loreboard-600 
                  text-white px-4 py-2 rounded-lg 
                  transition-colors duration-200 font-medium
                "
              >
                Use
              </button>
              <button
                type="button"
                onClick={() => setShowCustom(false)}
                className="
                  flex-1 border-2 border-loreboard-500 
                  text-loreboard-600 hover:bg-loreboard-50 
                  px-4 py-2 rounded-lg transition-colors duration-200
                "
              >
                Back
              </button>
            </div>
          </form>
        )}

        {/* Keyboard shortcuts */}
        <div className="
          px-4 py-2 bg-loreboard-50 
          border-t border-loreboard-100 text-xs text-gray-600
        ">
          <span className="inline-flex items-center gap-4">
            <span>↑↓ Navigate</span>
            <span>Enter Select</span>
            <span>Tab Custom</span>
            <span>Esc Cancel</span>
          </span>
        </div>
      </div>
    </div>
  );
};

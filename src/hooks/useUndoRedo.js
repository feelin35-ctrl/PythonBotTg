import { useState, useCallback } from 'react';

// Упрощенный хук без функций undo/redo, так как они больше не используются
export const useUndoRedo = (initialState = { nodes: [], edges: [] }) => {
  return {
    history: [initialState],
    historyIndex: 0,
    saveToHistory: () => {},
    undo: () => {},
    redo: () => {},
    canUndo: false,
    canRedo: false,
    currentState: initialState
  };
};

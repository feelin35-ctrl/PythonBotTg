import { useState, useCallback } from 'react';

export const useUndoRedo = (initialState = { nodes: [], edges: [] }) => {
  const [history, setHistory] = useState([initialState]);
  const [historyIndex, setHistoryIndex] = useState(0);

  const saveToHistory = useCallback((newState) => {
    // Ограничиваем размер истории до 50 шагов для оптимизации памяти
    const maxHistorySize = 50;
    const newHistory = [...history.slice(0, historyIndex + 1), newState];
    
    if (newHistory.length > maxHistorySize) {
      // Если история слишком длинная, удаляем самые старые записи
      const excess = newHistory.length - maxHistorySize;
      newHistory.splice(0, excess);
      setHistory(newHistory);
      setHistoryIndex(historyIndex - excess + 1);
    } else {
      setHistory(newHistory);
      setHistoryIndex(historyIndex + 1);
    }
  }, [history, historyIndex]);

  const undo = useCallback(() => {
    if (historyIndex > 0) {
      setHistoryIndex(prev => prev - 1);
      return history[historyIndex - 1];
    }
    return null;
  }, [history, historyIndex]);

  const redo = useCallback(() => {
    if (historyIndex < history.length - 1) {
      setHistoryIndex(prev => prev + 1);
      return history[historyIndex + 1];
    }
    return null;
  }, [history, historyIndex]);

  const canUndo = historyIndex > 0;
  const canRedo = historyIndex < history.length - 1;

  return {
    history,
    historyIndex,
    saveToHistory,
    undo,
    redo,
    canUndo,
    canRedo,
    currentState: history[historyIndex]
  };
};
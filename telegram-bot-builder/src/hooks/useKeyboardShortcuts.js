import { useCallback, useEffect } from 'react';

export const useKeyboardShortcuts = ({
  onDeleteSelected,
  onDeleteAll,
  onUndo,
  onRedo
}) => {
  const handleKeyPress = useCallback((event) => {
    // Delete - удалить выбранные блоки
    if (event.key === 'Delete') {
      event.preventDefault();
      onDeleteSelected?.();
    }

    // Ctrl+D - удалить выбранные блоки
    if (event.ctrlKey && event.key === 'd') {
      event.preventDefault();
      onDeleteSelected?.();
    }

    // Ctrl+Shift+D - удалить все блоки
    if (event.ctrlKey && event.shiftKey && event.key === 'D') {
      event.preventDefault();
      onDeleteAll?.();
    }

    // Ctrl+Z - отмена
    if (event.ctrlKey && event.key === 'z') {
      event.preventDefault();
      onUndo?.();
    }

    // Ctrl+Y - повтор
    if (event.ctrlKey && event.key === 'y') {
      event.preventDefault();
      onRedo?.();
    }
  }, [onDeleteSelected, onDeleteAll, onUndo, onRedo]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [handleKeyPress]);
};
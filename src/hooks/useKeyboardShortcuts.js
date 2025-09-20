import { useCallback, useEffect } from 'react';

export const useKeyboardShortcuts = ({
  onDeleteSelected,
  onDeleteAll
}) => {
  const handleKeyPress = useCallback((event) => {
    // Проверяем, не находится ли фокус ввода в поле ввода
    if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
      return;
    }

    // Delete - удалить выбранные элементы (блоки и связи)
    if (event.key === 'Delete') {
      event.preventDefault();
      onDeleteSelected?.();
    }

    // Ctrl+D - удалить выбранные элементы
    if (event.ctrlKey && event.key === 'd') {
      event.preventDefault();
      onDeleteSelected?.();
    }

    // Ctrl+Shift+D - удалить все блоки
    if (event.ctrlKey && event.shiftKey && event.key === 'D') {
      event.preventDefault();
      onDeleteAll?.();
    }
  }, [onDeleteSelected, onDeleteAll]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [handleKeyPress]);
};
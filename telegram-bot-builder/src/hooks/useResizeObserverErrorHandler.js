import { useEffect } from 'react';

export const useResizeObserverErrorHandler = () => {
  useEffect(() => {
    const originalErrorHandler = window.onerror;
    const originalConsoleError = console.error;

    // Обработчик ошибок window.onerror
    window.onerror = function(message, source, lineno, colno, error) {
      if (typeof message === 'string' && message.includes('ResizeObserver')) {
        return true; // Подавляем ошибку
      }
      if (originalErrorHandler) {
        return originalErrorHandler.apply(this, arguments);
      }
      return false;
    };

    // Обработчик console.error
    console.error = function(...args) {
      if (args[0] && typeof args[0] === 'string' && args[0].includes('ResizeObserver')) {
        return; // Подавляем ошибку
      }
      originalConsoleError.apply(console, args);
    };

    // Восстанавливаем оригинальные обработчики при размонтировании
    return () => {
      window.onerror = originalErrorHandler;
      console.error = originalConsoleError;
    };
  }, []);
};
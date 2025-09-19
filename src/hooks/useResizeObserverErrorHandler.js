import { useEffect } from 'react';

export const useResizeObserverErrorHandler = () => {
  useEffect(() => {
    const originalErrorHandler = window.onerror;
    const originalConsoleError = console.error;

    // Обработчик для addEventListener('error')
    const errorEventHandler = (event) => {
      if (event.message && event.message.includes('ResizeObserver')) {
        event.preventDefault();
        event.stopPropagation();
        return true;
      }
    };

    // Обработчик для unhandledrejection
    const unhandledRejectionHandler = (event) => {
      if (event.reason && event.reason.message && event.reason.message.includes('ResizeObserver')) {
        event.preventDefault();
        return true;
      }
    };

    // Добавляем обработчики событий
    window.addEventListener('error', errorEventHandler, true);
    window.addEventListener('unhandledrejection', unhandledRejectionHandler, true);

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
      window.removeEventListener('error', errorEventHandler, true);
      window.removeEventListener('unhandledrejection', unhandledRejectionHandler, true);
      window.onerror = originalErrorHandler;
      console.error = originalConsoleError;
    };
  }, []);
};
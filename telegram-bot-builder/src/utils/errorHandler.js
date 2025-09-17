// src/utils/errorHandler.js
export const setupErrorHandling = () => {
  // Игнорируем ошибки ResizeObserver
  const ignoreResizeObserverErrors = () => {
    const originalOnError = window.onerror;
    const originalConsoleError = console.error;

    window.onerror = function (message, source, lineno, colno, error) {
      if (typeof message === 'string' && message.toLowerCase().includes('resizeobserver')) {
        return true;
      }
      if (originalOnError) {
        return originalOnError.apply(this, arguments);
      }
      return false;
    };

    console.error = function (...args) {
      if (args[0] && typeof args[0] === 'string' && args[0].toLowerCase().includes('resizeobserver')) {
        return;
      }
      originalConsoleError.apply(console, args);
    };
  };

  ignoreResizeObserverErrors();
};
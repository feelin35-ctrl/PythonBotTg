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
  
  // Добавляем обработчик необработанных ошибок
  window.addEventListener('error', (event) => {
    // Игнорируем ошибки сценариев из внешних источников
    if (event.message.includes('Script error') && !event.filename) {
      return;
    }
    
    // Логируем ошибку в консоль
    console.error('Global error caught:', {
      message: event.message,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      error: event.error
    });
  });
  
  // Добавляем обработчик необработанных отклонений промисов
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
  });
};
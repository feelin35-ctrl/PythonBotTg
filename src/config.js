// Файл конфигурации для разных окружений
const isDevelopment = process.env.NODE_ENV === 'development';

// Базовые URL для разных окружений
const API_BASE_URL = isDevelopment 
  ? 'http://localhost:8001'  // Для локальной разработки
  : process.env.REACT_APP_API_URL || 'http://45.150.9.70:8001'; // Для продакшена по умолчанию используем правильный адрес

export { API_BASE_URL, isDevelopment };
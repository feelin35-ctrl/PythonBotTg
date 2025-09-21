import api from './api'; // Import our configured axios instance

// Утилита для определения правильного API URL в зависимости от окружения
export const getApiBaseUrl = () => {
  // Для разработки используем локальный сервер
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:8001';
  }
  
  // Для продакшена сначала проверяем переменную окружения
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // Если переменная окружения не задана, используем относительный путь
  // Это будет работать с прокси или если бэкенд и фронтенд на одном домене
  return '';
};

// Функция для проверки доступности API
export const checkApiAvailability = async (baseUrl) => {
  try {
    // Use our configured API instance instead of direct fetch
    const response = await api.get('/api/get_bots/');
    return response.status === 200;
  } catch (error) {
    console.error('API availability check failed:', error);
    return false;
  }
};

// Функция для отображения пользовательского сообщения об ошибке
export const handleApiError = (error, operation) => {
  console.error(`API Error during ${operation}:`, error);
  
  let userMessage = '';
  
  if (error.code === 'ECONNABORTED') {
    userMessage = 'Превышено время ожидания подключения к серверу. Пожалуйста, проверьте интернет-соединение или попробуйте позже.';
  } else if (!error.response) {
    userMessage = 'Ошибка сети. Пожалуйста, проверьте интернет-соединение или попробуйте позже.';
  } else {
    userMessage = `Ошибка сервера: ${error.response?.data?.message || error.message}`;
  }
  
  // Показываем сообщение пользователю
  if (window.innerWidth <= 768) {
    alert(userMessage);
  } else {
    console.error(userMessage);
  }
  
  return userMessage;
};
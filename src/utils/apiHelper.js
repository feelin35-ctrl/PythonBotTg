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
    const response = await fetch(`${baseUrl}/api/get_bots/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 5000, // 5 секунд таймаут
    });
    
    return response.ok;
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
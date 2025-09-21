import axios from 'axios';
import { getApiBaseUrl } from './utils/apiHelper';

// Получаем базовый URL для API
const API_BASE_URL = getApiBaseUrl();

// Создаем экземпляр axios с базовой конфигурацией
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000, // Уменьшаем таймаут до 15 секунд
});

// Добавляем отладочную информацию
console.log('Axios instance created with baseURL:', API_BASE_URL);

// Добавляем интерцептор для отладки запросов
api.interceptors.request.use(request => {
  console.log('Starting Request:', request);
  return request;
});

api.interceptors.response.use(response => {
  console.log('Response:', response);
  return response;
}, error => {
  console.error('Response Error:', error);
  
  // Добавляем более понятное сообщение об ошибке
  if (error.code === 'ECONNABORTED') {
    console.error('Request timeout - please check if the backend server is running and accessible');
  } else if (!error.response) {
    console.error('Network error - please check your connection and backend server availability');
  }
  
  return Promise.reject(error);
});

export default api;
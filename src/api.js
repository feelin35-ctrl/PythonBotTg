import axios from 'axios';
import { API_BASE_URL } from './config';

// Создаем экземпляр axios с базовой конфигурацией
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
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
  return Promise.reject(error);
});

export default api;
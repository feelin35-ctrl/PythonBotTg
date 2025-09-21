import axios from 'axios';
import { API_BASE_URL } from './config';

// Создаем экземпляр axios с базовой конфигурацией
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export default api;
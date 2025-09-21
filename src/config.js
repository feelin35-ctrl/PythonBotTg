// Файл конфигурации для разных окружений
import { getApiBaseUrl } from './utils/apiHelper';

const isDevelopment = process.env.NODE_ENV === 'development';
const API_BASE_URL = getApiBaseUrl();

// Добавляем отладочную информацию
console.log('Environment detection:');
console.log('NODE_ENV:', process.env.NODE_ENV);
console.log('isDevelopment:', isDevelopment);
console.log('API_BASE_URL:', API_BASE_URL);

export { API_BASE_URL, isDevelopment };
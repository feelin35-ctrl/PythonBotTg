// Тестовая проверка конфигурации прокси
console.log('Testing proxy configuration...');

// Проверяем переменные окружения
console.log('REACT_APP_API_URL:', process.env.REACT_APP_API_URL);

// Проверяем, определена ли функция прокси
try {
  const fs = require('fs');
  const path = require('path');
  
  const proxyFilePath = path.join(__dirname, 'src', 'setupProxy.js');
  console.log('Proxy file exists:', fs.existsSync(proxyFilePath));
  
  if (fs.existsSync(proxyFilePath)) {
    const proxyContent = fs.readFileSync(proxyFilePath, 'utf8');
    console.log('Proxy file content:');
    console.log(proxyContent);
  }
} catch (error) {
  console.error('Error reading proxy file:', error.message);
}
// Тестовый скрипт для проверки переменных окружения в React
console.log('Testing React environment variables...');

// Проверяем, что переменные окружения определены
console.log('REACT_APP_API_URL:', process.env.REACT_APP_API_URL);

// Проверяем содержимое файлов .env
const fs = require('fs');
const path = require('path');

const envFiles = ['.env', '.env.development', '.env.production'];

envFiles.forEach(file => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    console.log(`\n${file} contents:`);
    const content = fs.readFileSync(filePath, 'utf8');
    console.log(content);
  } else {
    console.log(`\n${file} not found`);
  }
});
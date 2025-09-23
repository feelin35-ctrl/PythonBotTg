import mysql.connector
import os
import hashlib
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Хешируем новый пароль
new_password = "newpassword"
hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

# Подключаемся к базе данных
try:
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'telegram_bot_builder')
    )
    
    cursor = connection.cursor()
    
    # Обновляем пароль для пользователя Feelin
    query = "UPDATE users SET password_hash = %s WHERE username = %s"
    cursor.execute(query, (hashed_password, "Feelin"))
    
    # Сохраняем изменения
    connection.commit()
    
    print(f"Пароль для пользователя Feelin успешно обновлен на: {new_password}")
    
    # Закрываем соединение
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Ошибка обновления пароля: {e}")
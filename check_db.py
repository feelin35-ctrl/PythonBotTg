import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Загружаем переменные окружения из файла .env
load_dotenv()

def check_db_connection():
    try:
        # Получаем параметры подключения из переменных окружения
        host = os.getenv('DB_HOST', 'localhost')
        database = os.getenv('DB_NAME', 'telegram_bot_builder')
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', '')
        port = int(os.getenv('DB_PORT', 3306))
        
        print(f"Попытка подключения к базе данных:")
        print(f"  Хост: {host}")
        print(f"  Порт: {port}")
        print(f"  База данных: {database}")
        print(f"  Пользователь: {user}")
        print(f"  Пароль: {'*' * len(password) if password else 'пустой'}")
        
        # Пытаемся подключиться к базе данных
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        
        if connection.is_connected():
            print("✅ Успешное подключение к базе данных!")
            
            # Получаем информацию о сервере
            db_info = connection.get_server_info()
            print(f"Версия сервера MySQL: {db_info}")
            
            # Проверяем наличие таблиц
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print("Таблицы в базе данных:")
                for table in tables:
                    # Просто выводим элемент напрямую
                    print(f"  - {table[0]}")
            else:
                print("В базе данных нет таблиц")
            
            cursor.close()
            connection.close()
            print("Соединение закрыто")
            
    except Error as e:
        print(f"❌ Ошибка при подключении к базе данных: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    check_db_connection()
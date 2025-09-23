#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных MySQL для Telegram Bot Builder
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

def create_database():
    """Создание базы данных и таблиц"""
    connection = None
    cursor = None
    
    try:
        # Подключение к MySQL серверу (без указания базы данных)
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            port=int(os.getenv('DB_PORT', 3306))
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Создание базы данных
            db_name = os.getenv('DB_NAME', 'telegram_bot_builder')
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cursor.execute(f"USE {db_name}")
            
            print(f"База данных '{db_name}' создана или уже существует")
            
            # Создание таблицы пользователей
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL
            )
            """
            
            cursor.execute(create_users_table)
            print("Таблица 'users' создана или уже существует")
            
            # Создание таблицы токенов пользователей
            create_tokens_table = """
            CREATE TABLE IF NOT EXISTS user_tokens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                bot_id VARCHAR(100) NOT NULL,
                token TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_bot (user_id, bot_id)
            )
            """
            
            cursor.execute(create_tokens_table)
            print("Таблица 'user_tokens' создана или уже существует")
            
            # Создание таблицы владельцев ботов
            create_bot_owners_table = """
            CREATE TABLE IF NOT EXISTS bot_owners (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                bot_id VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_bot (bot_id)
            )
            """
            
            cursor.execute(create_bot_owners_table)
            print("Таблица 'bot_owners' создана или уже существует")
            
            # Создание тестового администратора (опционально)
            admin_username = os.getenv('ADMIN_USERNAME', 'admin')
            admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
            
            # Проверка, существует ли уже администратор
            cursor.execute("SELECT id FROM users WHERE username = %s", (admin_username,))
            if not cursor.fetchone():
                # Хеширование пароля (в реальном приложении используйте библиотеку bcrypt)
                import hashlib
                password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
                
                insert_admin = """
                INSERT INTO users (username, email, password_hash, is_admin) 
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_admin, (admin_username, admin_email, password_hash, True))
                connection.commit()
                print(f"Тестовый администратор '{admin_username}' создан")
            else:
                print(f"Администратор '{admin_username}' уже существует")
            
            print("Инициализация базы данных завершена успешно!")
            return True
            
    except Error as e:
        print(f"Ошибка при работе с MySQL: {e}")
        return False
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("Соединение с MySQL закрыто")

if __name__ == "__main__":
    print("Инициализация базы данных MySQL для Telegram Bot Builder")
    print("=" * 50)
    
    # Проверка наличия необходимых переменных окружения
    required_vars = ['DB_HOST', 'DB_USER', 'DB_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Отсутствуют необходимые переменные окружения: {', '.join(missing_vars)}")
        print("Пожалуйста, создайте файл .env с необходимыми настройками")
        sys.exit(1)
    
    success = create_database()
    if success:
        print("\n✅ База данных готова к использованию!")
        print("Теперь вы можете запустить приложение командой: python main.py")
    else:
        print("\n❌ Ошибка инициализации базы данных")
        sys.exit(1)
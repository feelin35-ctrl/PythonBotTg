#!/usr/bin/env python3
"""
Тестовый скрипт для проверки аутентификации пользователей
"""

import sys
import os

# Добавляем текущую директорию в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.models import UserManager
from core.db import db

def test_user_manager():
    """Тест менеджера пользователей"""
    print("Тестирование менеджера пользователей...")
    
    try:
        # Инициализируем базу данных
        if not db.connect():
            print("Ошибка: Не удалось подключиться к базе данных")
            return False
        
        print("Успешное подключение к базе данных")
        
        if not db.create_tables():
            print("Ошибка: Не удалось создать таблицы")
            return False
        
        print("Таблицы созданы успешно")
        
        # Создаем менеджер пользователей
        manager = UserManager()
        print("Менеджер пользователей создан успешно")
        
        # Тест регистрации пользователя
        username = "testuser"
        email = "test@example.com"
        password = "testpassword"
        
        print(f"Регистрация пользователя {username}...")
        result = manager.register_user(username, email, password)
        if result:
            print("Пользователь успешно зарегистрирован")
        else:
            print("Ошибка регистрации пользователя или пользователь уже существует")
        
        # Тест аутентификации пользователя
        print(f"Аутентификация пользователя {username}...")
        user = manager.authenticate_user(username, password)
        if user:
            print("Пользователь успешно аутентифицирован")
            print(f"Имя пользователя: {user.username}")
            print(f"Email: {user.email}")
            print(f"Администратор: {user.is_admin}")
        else:
            print("Ошибка аутентификации пользователя")
        
        # Тест сохранения токена (используем username вместо id)
        print("Сохранение тестового токена...")
        bot_id = "testbot"
        token = "test_token_12345"
        # Для теста используем фиксированный user_id
        result = manager.save_user_token("1", bot_id, token)
        if result:
            print("Токен успешно сохранен")
        else:
            print("Ошибка сохранения токена")
        
        # Тест получения токена
        print("Получение тестового токена...")
        retrieved_token = manager.get_user_token("1", bot_id)
        if retrieved_token:
            print("Токен успешно получен")
            print(f"Токен: {retrieved_token}")
        else:
            print("Ошибка получения токена")
        
        db.disconnect()
        print("Тест завершен успешно")
        return True
        
    except Exception as e:
        print(f"Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Запуск теста аутентификации...")
    success = test_user_manager()
    if success:
        print("\n✅ Все тесты пройдены успешно!")
    else:
        print("\n❌ Тесты завершены с ошибками")
        sys.exit(1)
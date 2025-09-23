#!/usr/bin/env python3
"""
Отладочный скрипт для проверки создания ботов
"""

import requests
import json

def debug_create_bot():
    """Отладка создания ботов"""
    
    print("=== Отладка создания ботов ===\n")
    
    # Попробуем создать бота с user_id
    print("1. Создание бота с user_id=1:")
    try:
        response = requests.post("http://localhost:8001/api/create_bot/?bot_id=debug_bot_1&user_id=1")
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.json()}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    print()
    
    # Проверим, что бот был создан
    print("2. Проверка списка ботов для пользователя 1:")
    try:
        response = requests.get("http://localhost:8001/api/get_bots/?user_id=1")
        bots = response.json().get("bots", [])
        print(f"   Ботов у пользователя 1: {len(bots)}")
        for bot in bots:
            print(f"     - {bot}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    print()
    
    # Проверим базу данных напрямую
    print("3. Проверка таблицы bot_owners:")
    try:
        import mysql.connector
        import os
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'telegram_bot_builder'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, bot_id FROM bot_owners WHERE bot_id = "debug_bot_1"')
        result = cursor.fetchall()
        print("   Записи в bot_owners для debug_bot_1:")
        if result:
            for row in result:
                user_id, bot_id = row
                print(f"     Пользователь {user_id}: бот {bot_id}")
        else:
            print("     Нет записей")
        conn.close()
    except Exception as e:
        print(f"   Ошибка: {e}")

if __name__ == "__main__":
    debug_create_bot()
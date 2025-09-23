#!/usr/bin/env python3
"""
Скрипт для очистки тестовых ботов из базы данных
"""

import mysql.connector
import os

def cleanup_test_bots():
    """Удаляет тестовые боты из базы данных"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'telegram_bot_builder'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        cursor = conn.cursor()
        cursor.execute('DELETE FROM bot_owners WHERE bot_id IN ("test_bot_1", "test_bot_2")')
        conn.commit()
        print(f"Удалено {cursor.rowcount} записей из bot_owners")
        conn.close()
    except Exception as e:
        print(f"Ошибка при очистке тестовых ботов: {e}")

if __name__ == "__main__":
    cleanup_test_bots()
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.db import db

def check_users():
    """Проверяет список пользователей в базе данных"""
    try:
        # Подключаемся к базе данных
        if not db.connect():
            print("❌ Не удалось подключиться к базе данных")
            return
        
        # Получаем список всех пользователей
        query = "SELECT id, username, email, role FROM users"
        result = db.execute_query(query, ())
        
        if result:
            print("Список пользователей в системе:")
            print("=" * 50)
            for row in result:
                user_id, username, email, role = row
                print(f"ID: {user_id}, Имя: {username}, Email: {email}, Роль: {role}")
        else:
            print("Пользователи не найдены в базе данных")
            
    except Exception as e:
        print(f"❌ Ошибка при получении списка пользователей: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_users()
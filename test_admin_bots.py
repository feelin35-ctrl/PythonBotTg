import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.models import UserManager
from core.db import db

def test_admin_bots():
    """Тестирует возможность супер администратора видеть всех ботов"""
    try:
        # Подключаемся к базе данных
        if not db.connect():
            print("❌ Не удалось подключиться к базе данных")
            return
        
        # Получаем ID супер администратора
        query = "SELECT id FROM users WHERE role = 'super_admin' LIMIT 1"
        result = db.execute_query(query, ())
        
        if not result:
            print("❌ Супер администратор не найден в системе")
            return
            
        admin_id = str(result[0][0])
        print(f"ID супер администратора: {admin_id}")
        
        # Проверяем, какие боты видны супер администратору через UserManager
        user_manager = UserManager()
        admin_bots = user_manager.get_user_bots(admin_id)
        print(f"Боты, видимые супер администратору через get_user_bots: {admin_bots}")
        
        # Проверяем все боты в системе
        query = "SELECT bot_id FROM bot_owners"
        result = db.execute_query(query, ())
        all_bots = [row[0] for row in result] if result else []
        print(f"Все боты в системе: {all_bots}")
        
        # Сравниваем
        if set(admin_bots) == set(all_bots):
            print("✅ Супер администратор видит всех ботов в системе")
        else:
            print("❌ Супер администратор не видит всех ботов")
            print(f"  Пропущенные боты: {set(all_bots) - set(admin_bots)}")
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_admin_bots()
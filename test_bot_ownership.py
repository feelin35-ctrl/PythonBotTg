import os
import json
from core.models import UserManager

# Получаем список всех ботов из файловой системы
BOTS_DIR = "bots"

def get_all_bots_from_files():
    """Получает список всех ботов из файлов"""
    bots = []
    if os.path.exists(BOTS_DIR):
        filenames = os.listdir(BOTS_DIR)
        for filename in filenames:
            if filename.startswith("bot_") and filename.endswith(".json"):
                bot_id = filename.replace("bot_", "").replace(".json", "")
                bots.append(bot_id)
    return bots

def check_bot_ownership():
    """Проверяет владение ботами"""
    # Получаем всех пользователей
    user_manager = UserManager()
    
    # Получаем всех ботов из файлов
    all_bots = get_all_bots_from_files()
    print(f"Все боты в системе: {all_bots}")
    
    # Получаем ботов с владельцами из базы данных
    try:
        # Прямой запрос к базе данных для получения всех записей о владении
        from core.db import db
        query = "SELECT user_id, bot_id FROM bot_owners"
        result = db.execute_query(query, ())
        
        print("\nЗарегистрированные владельцы ботов:")
        bot_owners = {}
        if result:
            for row in result:
                user_id, bot_id = row
                bot_owners[bot_id] = user_id
                print(f"  Бот '{bot_id}' принадлежит пользователю с ID {user_id}")
        else:
            print("  Нет зарегистрированных владельцев")
            
        # Показываем ботов без владельцев
        bots_without_owners = [bot for bot in all_bots if bot not in bot_owners]
        print(f"\nБоты без владельцев: {bots_without_owners}")
        
        # Для каждого пользователя показываем его ботов
        print("\nБоты по пользователям:")
        users_query = "SELECT id, username FROM users"
        users_result = db.execute_query(users_query, ())
        if users_result:
            for user_row in users_result:
                user_id, username = user_row
                user_bots = user_manager.get_user_bots(str(user_id))
                print(f"  Пользователь '{username}' (ID {user_id}): {user_bots}")
        
    except Exception as e:
        print(f"Ошибка при проверке владения ботами: {e}")

if __name__ == "__main__":
    check_bot_ownership()
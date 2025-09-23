import os
import json
from core.models import UserManager
from core.db import db

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

def fix_bot_ownership():
    """Исправляет владение ботами - регистрирует владельца для ботов без владельцев"""
    # Получаем менеджер пользователей
    user_manager = UserManager()
    
    # Получаем всех ботов из файлов
    all_bots = get_all_bots_from_files()
    print(f"Все боты в системе: {all_bots}")
    
    # Получаем ботов с владельцами из базы данных
    try:
        # Прямой запрос к базе данных для получения всех записей о владении
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
        
        # Для ботов без владельцев назначаем владельца (первого пользователя или админа)
        if bots_without_owners:
            # Получаем первого пользователя (обычно это админ)
            users_query = "SELECT id FROM users ORDER BY id LIMIT 1"
            users_result = db.execute_query(users_query, ())
            if users_result:
                default_user_id = str(users_result[0][0])
                print(f"\nНазначаем владельца по умолчанию (ID {default_user_id}) для ботов без владельцев:")
                
                for bot_id in bots_without_owners:
                    try:
                        success = user_manager.register_bot_ownership(default_user_id, bot_id)
                        if success:
                            print(f"  ✓ Бот '{bot_id}' теперь принадлежит пользователю с ID {default_user_id}")
                        else:
                            print(f"  ✗ Не удалось зарегистрировать владельца для бота '{bot_id}'")
                    except Exception as e:
                        print(f"  ✗ Ошибка при регистрации владельца для бота '{bot_id}': {e}")
            else:
                print("  Не найдено пользователей для назначения владельца")
        
        # Проверяем результат
        print("\n=== После исправления ===")
        query = "SELECT user_id, bot_id FROM bot_owners"
        result = db.execute_query(query, ())
        
        print("\nЗарегистрированные владельцы ботов:")
        if result:
            for row in result:
                user_id, bot_id = row
                print(f"  Бот '{bot_id}' принадлежит пользователю с ID {user_id}")
        else:
            print("  Нет зарегистрированных владельцев")
            
    except Exception as e:
        print(f"Ошибка при исправлении владения ботами: {e}")

if __name__ == "__main__":
    fix_bot_ownership()
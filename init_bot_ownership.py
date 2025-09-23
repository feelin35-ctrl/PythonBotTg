#!/usr/bin/env python3
"""
Скрипт для инициализации системы владения ботами.
Этот скрипт должен запускаться при первом запуске приложения или при обновлении системы.
"""

import os
import sys
import logging
from core.models import UserManager
from core.db import db

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_bot_ownership():
    """Инициализирует систему владения ботами для всех существующих ботов"""
    try:
        # Проверяем подключение к базе данных
        if not db.connect():
            logger.error("Не удалось подключиться к базе данных")
            return False
            
        # Создаем таблицы если они не существуют
        if not db.create_tables():
            logger.error("Не удалось создать таблицы в базе данных")
            return False
            
        # Получаем менеджер пользователей
        user_manager = UserManager()
        
        # Получаем всех пользователей
        users_query = "SELECT id, username FROM users ORDER BY id"
        users_result = db.execute_query(users_query, ())
        
        if not users_result:
            logger.warning("Нет пользователей в системе. Создайте хотя бы одного пользователя.")
            return False
            
        # Показываем список пользователей
        logger.info("Существующие пользователи:")
        for user_row in users_result:
            user_id, username = user_row
            logger.info(f"  ID {user_id}: {username}")
            
        # Получаем первого пользователя (обычно это админ) как владельца по умолчанию
        default_user_id = str(users_result[0][0])
        default_username = users_result[0][1]
        logger.info(f"Владелец по умолчанию: {default_username} (ID {default_user_id})")
        
        # Получаем всех ботов из файловой системы
        BOTS_DIR = "bots"
        all_bots = []
        if os.path.exists(BOTS_DIR):
            filenames = os.listdir(BOTS_DIR)
            for filename in filenames:
                if filename.startswith("bot_") and filename.endswith(".json"):
                    bot_id = filename.replace("bot_", "").replace(".json", "")
                    all_bots.append(bot_id)
        
        logger.info(f"Найдено ботов в файловой системе: {len(all_bots)}")
        for bot_id in all_bots:
            logger.info(f"  - {bot_id}")
            
        # Получаем ботов с уже зарегистрированными владельцами
        owners_query = "SELECT bot_id FROM bot_owners"
        owners_result = db.execute_query(owners_query, ())
        owned_bots = set()
        if owners_result:
            owned_bots = set(row[0] for row in owners_result)
            
        logger.info(f"Ботов с зарегистрированными владельцами: {len(owned_bots)}")
        
        # Регистрируем владельцев для ботов без владельцев
        bots_without_owners = [bot for bot in all_bots if bot not in owned_bots]
        logger.info(f"Ботов без владельцев: {len(bots_without_owners)}")
        
        if bots_without_owners:
            logger.info(f"Регистрируем владельца по умолчанию для {len(bots_without_owners)} ботов:")
            for bot_id in bots_without_owners:
                try:
                    success = user_manager.register_bot_ownership(default_user_id, bot_id)
                    if success:
                        logger.info(f"  ✓ Бот '{bot_id}' теперь принадлежит пользователю {default_username} (ID {default_user_id})")
                    else:
                        logger.warning(f"  ✗ Не удалось зарегистрировать владельца для бота '{bot_id}'")
                except Exception as e:
                    logger.error(f"  ✗ Ошибка при регистрации владельца для бота '{bot_id}': {e}")
        else:
            logger.info("Все боты уже имеют зарегистрированных владельцев")
            
        # Проверяем результат
        logger.info("=== Финальная проверка ===")
        final_query = "SELECT u.username, bo.bot_id FROM bot_owners bo JOIN users u ON bo.user_id = u.id ORDER BY u.username, bo.bot_id"
        final_result = db.execute_query(final_query, ())
        
        if final_result:
            current_user = None
            for row in final_result:
                username, bot_id = row
                if username != current_user:
                    current_user = username
                    logger.info(f"Пользователь {username}:")
                logger.info(f"  - {bot_id}")
        else:
            logger.info("Нет зарегистрированных владельцев")
            
        logger.info("Инициализация системы владения ботами завершена успешно!")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации системы владения ботами: {e}")
        return False
    finally:
        # Закрываем соединение с базой данных
        try:
            db.disconnect()
        except:
            pass

if __name__ == "__main__":
    success = initialize_bot_ownership()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Деплоймент бота "test_auto_update" для хостинга
Автоматическое обновление из GitHub репозитория
"""

import os
import sys
import logging
import json
import subprocess
import time
from datetime import datetime, timedelta

# Добавляем текущую директорию в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import statements would go here if we had the actual modules
# from core.scenario_runner import ScenarioRunner
# from core.block_registry import block_registry
import telebot
import threading

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Флаг для отслеживания необходимости перезапуска
need_restart = False
last_update_check = datetime.now()


def check_for_updates():
    """Проверяет наличие обновлений в репозитории GitHub"""
    global need_restart, last_update_check
    
    # Проверяем обновления каждые 60 минут
    if datetime.now() - last_update_check < timedelta(minutes=60):
        return False
    
    last_update_check = datetime.now()
    
    try:
        # Проверяем наличие git
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.info("Git не найден, пропускаем проверку обновлений")
            return False
        
        # Проверяем статус репозитория
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.info("Не Git репозиторий, пропускаем проверку обновлений")
            return False
        
        # Получаем последние изменения
        subprocess.run(['git', 'fetch'], check=True)
        
        # Проверяем, есть ли новые коммиты
        local_hash = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True)
        remote_hash = subprocess.run(['git', 'rev-parse', '@{u}'], capture_output=True, text=True, check=True)
        
        if local_hash.stdout.strip() != remote_hash.stdout.strip():
            logger.info("Найдены обновления, начинаем обновление...")
            
            # Выполняем обновление
            subprocess.run(['git', 'pull'], check=True)
            
            # Устанавливаем зависимости
            if os.path.exists('requirements.txt'):
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
            
            logger.info("Обновление завершено, требуется перезапуск")
            need_restart = True
            return True
        else:
            logger.info("Обновлений не найдено")
            return False
            
    except subprocess.CalledProcessError as ex:
        logger.error(f"Ошибка при проверке обновлений: {ex}")
        return False
    except Exception as ex:
        logger.error(f"Неожиданная ошибка при проверке обновлений: {ex}")
        return False


def run_bot():
    """Запускает бота"""
    global need_restart
    
    while True:
        try:
            # Проверяем обновления перед запуском
            if check_for_updates():
                logger.info("Перезапуск бота после обновления...")
                continue
            
            # Загружаем конфигурацию
            tokens_path = "bot_tokens.json"
            if not os.path.exists(tokens_path):
                logger.error("Файл токенов не найден")
                return
            
            with open(tokens_path, "r", encoding="utf-8") as f:
                tokens = json.load(f)
            
            bot_token = tokens.get("test_auto_update")
            if not bot_token:
                logger.error("Токен бота не найден")
                return
            
            # Создаем бота
            bot = telebot.TeleBot(bot_token)
            bot_info = bot.get_me()
            logger.info(f"✅ Бот запущен: @{bot_info.username}")
            
            @bot.message_handler(commands=['start', 'help'])
            def handle_start(message):
                try:
                    logger.info(f"👤 /start от {message.chat.id} - {message.from_user.username}")
                    bot.send_message(message.chat.id, "Hello! This bot includes auto-update functionality.")
                except Exception as e:
                    logger.error(f"❌ Ошибка в /start: {e}")
            
            @bot.message_handler(commands=['update'])
            def handle_update(message):
                """Handle manual update command"""
                try:
                    logger.info(f"🔄 Ручная проверка обновлений от {message.chat.id}")
                    bot.send_message(message.chat.id, "🔍 Проверяю наличие обновлений...")
                    
                    if check_for_updates():
                        bot.send_message(message.chat.id, "✅ Обновления успешно установлены! Перезапуск бота...")
                        bot.stop_polling()
                        # In a real implementation, you would restart the bot here
                    else:
                        bot.send_message(message.chat.id, "ℹ️ Обновлений не найдено.")
                except Exception as e:
                    logger.error(f"❌ Ошибка при ручной проверке обновлений: {e}")
                    bot.send_message(message.chat.id, f"❌ Ошибка при проверке обновлений: {str(e)}")
            
            logger.info("🤖 Бот запущен и ожидает сообщений...")
            
            # Запускаем polling в отдельном потоке для возможности проверки обновлений
            def polling_thread():
                bot.polling(none_stop=True)
            
            poll_thread = threading.Thread(target=polling_thread)
            poll_thread.daemon = True
            poll_thread.start()
            
            # Проверяем обновления каждые 10 минут в основном потоке
            while poll_thread.is_alive():
                time.sleep(600)  # 10 минут
                if check_for_updates():
                    logger.info("Перезапуск бота после обновления...")
                    bot.stop_polling()
                    break
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска бота: {e}")
            
            # Ждем перед повторной попыткой
            time.sleep(10)
            
        # Если мы дошли до этой точки, значит бот остановился
        break


if __name__ == "__main__":
    run_bot()
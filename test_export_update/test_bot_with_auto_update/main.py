#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deployment of bot "test_auto_update" for hosting
Automatic updates from GitHub repository

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

# Add the current directory to the module search path
# Добавляем текущую директорию в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import statements would go here if we had the actual modules
# from core.scenario_runner import ScenarioRunner
# from core.block_registry import block_registry
import telebot
import threading

# Logging setup
# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flag to track if restart is needed
# Флаг для отслеживания необходимости перезапуска
need_restart = False
last_update_check = datetime.now()


def check_for_updates():
    """Checks for updates in the GitHub repository
    Проверяет наличие обновлений в репозитории GitHub"""
    global need_restart, last_update_check
    
    # Check for updates every 60 minutes
    # Проверяем обновления каждые 60 минут
    if datetime.now() - last_update_check < timedelta(minutes=60):
        return False
    
    last_update_check = datetime.now()
    
    try:
        # Check if git is available
        # Проверяем наличие git
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.info("Git not found, skipping update check\nGit не найден, пропускаем проверку обновлений")
            return False
        
        # Check if this is a git repository
        # Проверяем статус репозитория
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.info("Not a Git repository, skipping update check\nНе Git репозиторий, пропускаем проверку обновлений")
            return False
        
        # Fetch latest changes
        # Получаем последние изменения
        subprocess.run(['git', 'fetch'], check=True)
        
        # Check if there are new commits
        # Проверяем, есть ли новые коммиты
        local_hash = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True)
        remote_hash = subprocess.run(['git', 'rev-parse', '@{u}'], capture_output=True, text=True, check=True)
        
        if local_hash.stdout.strip() != remote_hash.stdout.strip():
            logger.info("Updates found, starting update process\nНайдены обновления, начинаем обновление...")
            
            # Perform update
            # Выполняем обновление
            subprocess.run(['git', 'pull'], check=True)
            
            # Install dependencies
            # Устанавливаем зависимости
            if os.path.exists('requirements.txt'):
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
            
            logger.info("Update completed, restart required\nОбновление завершено, требуется перезапуск")
            need_restart = True
            return True
        else:
            logger.info("No updates found\nОбновлений не найдено")
            return False
            
    except subprocess.CalledProcessError as ex:
        logger.error(f"Error checking for updates: {ex}\nОшибка при проверке обновлений: {ex}")
        return False
    except Exception as ex:
        logger.error(f"Unexpected error checking for updates: {ex}\nНеожиданная ошибка при проверке обновлений: {ex}")
        return False


def run_bot():
    """Starts the bot
    Запускает бота"""
    global need_restart
    
    while True:
        try:
            # Check for updates before starting
            # Проверяем обновления перед запуском
            if check_for_updates():
                logger.info("Restarting bot after update\nПерезапуск бота после обновления...")
                continue
            
            # Load configuration
            # Загружаем конфигурацию
            tokens_path = "bot_tokens.json"
            if not os.path.exists(tokens_path):
                logger.error("Token file not found\nФайл токенов не найден")
                return
            
            with open(tokens_path, "r", encoding="utf-8") as f:
                tokens = json.load(f)
            
            bot_token = tokens.get("test_auto_update")
            if not bot_token:
                logger.error("Bot token not found\nТокен бота не найден")
                return
            
            # Create bot
            # Создаем бота
            bot = telebot.TeleBot(bot_token)
            bot_info = bot.get_me()
            logger.info(f"✅ Bot started: @{bot_info.username}\n✅ Бот запущен: @{bot_info.username}")
            
            @bot.message_handler(commands=['start', 'help'])
            def handle_start(message):
                try:
                    logger.info(f"👤 /start from {message.chat.id} - {message.from_user.username}\n👤 /start от {message.chat.id} - {message.from_user.username}")
                    bot.send_message(message.chat.id, "Hello! This bot includes auto-update functionality.\nПривет! Этот бот включает функцию автоматического обновления.")
                except Exception as e:
                    logger.error(f"❌ Error in /start: {e}\n❌ Ошибка в /start: {e}")
            
            @bot.message_handler(commands=['update'])
            def handle_update(message):
                """Handle manual update command
                Обрабатывает команду ручного обновления"""
                try:
                    logger.info(f"🔄 Manual update check from {message.chat.id}\n🔄 Ручная проверка обновлений от {message.chat.id}")
                    bot.send_message(message.chat.id, "🔍 Checking for updates...\n🔍 Проверяю наличие обновлений...")
                    
                    if check_for_updates():
                        bot.send_message(message.chat.id, "✅ Updates successfully installed! Restarting bot...\n✅ Обновления успешно установлены! Перезапуск бота...")
                        bot.stop_polling()
                        # In a real implementation, you would restart the bot here
                        # В реальной реализации здесь нужно перезапустить бота
                    else:
                        bot.send_message(message.chat.id, "ℹ️ No updates found.\nℹ️ Обновлений не найдено.")
                except Exception as e:
                    logger.error(f"❌ Error during manual update check: {e}\n❌ Ошибка при ручной проверке обновлений: {e}")
                    bot.send_message(message.chat.id, f"❌ Error checking for updates: {str(e)}\n❌ Ошибка при проверке обновлений: {str(e)}")
            
            logger.info("🤖 Bot started and waiting for messages\n🤖 Бот запущен и ожидает сообщений...")
            
            # Run polling in a separate thread to allow update checks
            # Запускаем polling в отдельном потоке для возможности проверки обновлений
            def polling_thread():
                bot.polling(none_stop=True)
            
            poll_thread = threading.Thread(target=polling_thread)
            poll_thread.daemon = True
            poll_thread.start()
            
            # Check for updates every 10 minutes in the main thread
            # Проверяем обновления каждые 10 минут в основном потоке
            while poll_thread.is_alive():
                time.sleep(600)  # 10 minutes
                if check_for_updates():
                    logger.info("Restarting bot after update\nПерезапуск бота после обновления...")
                    bot.stop_polling()
                    break
            
        except Exception as e:
            logger.error(f"❌ Error starting bot: {e}\n❌ Ошибка запуска бота: {e}")
            
            # Wait before retrying
            # Ждем перед повторной попыткой
            time.sleep(10)
            
        # If we reach this point, the bot has stopped
        # Если мы дошли до этой точки, значит бот остановился
        break


if __name__ == "__main__":
    run_bot()
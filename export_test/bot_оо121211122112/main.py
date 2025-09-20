#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Деплоймент бота "оо121211122112" для хостинга
"""

import os
import sys
import logging
import json

# Добавляем текущую директорию в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.scenario_runner import ScenarioRunner
from core.block_registry import block_registry
import telebot
import time
import threading
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_bot():
    """Запускает бота"""
    try:
        # Загружаем конфигурацию
        # Сначала пробуем загрузить из .env файла
        load_dotenv()
        bot_token = os.getenv("BOT_TOKEN")
        
        # Если нет в .env, пробуем загрузить из файла токенов
        if not bot_token:
            tokens_path = "bot_tokens.json"
            if not os.path.exists(tokens_path):
                logger.error("Файл токенов не найден")
                return
            
            with open(tokens_path, "r", encoding="utf-8") as f:
                tokens = json.load(f)
            
            bot_token = tokens.get("оо121211122112")
            if not bot_token:
                logger.error("Токен бота не найден")
                return
        
        # Загружаем сценарий
        scenario_path = f"bots/bot_оо121211122112.json"
        if not os.path.exists(scenario_path):
            logger.error("Файл сценария не найден")
            return
        
        with open(scenario_path, "r", encoding="utf-8") as f:
            scenario_data = json.load(f)
        
        # Создаем исполнитель сценария
        scenario_runner = ScenarioRunner(scenario_data)
        if not scenario_runner.nodes_map:
            logger.error("Нет доступных блоков в сценарии!")
            return
        
        # Создаем бота
        bot = telebot.TeleBot(bot_token)
        bot_info = bot.get_me()
        logger.info(f"✅ Бот запущен: @{bot_info.username}")
        
        @bot.message_handler(commands=['start', 'help'])
        def handle_start(message):
            try:
                logger.info(f"👤 /start от {message.chat.id} - {message.from_user.username}")
                
                # Находим стартовый узел
                start_node = next((node_id for node_id, block in scenario_runner.nodes_map.items()
                                   if hasattr(block, 'type') and block.type == 'start'), None)
                if start_node:
                    # Запускаем цепочку обработки
                    next_node_id = scenario_runner.process_node(bot, message.chat.id, start_node)
                    while next_node_id:
                        # Проверяем тип следующего узла
                        next_block = scenario_runner.nodes_map.get(next_node_id)
                        if next_block and hasattr(next_block, 'type'):
                            # Если это интерактивные блоки, останавливаем автоматическое выполнение
                            if next_block.type in ['button', 'inline_button', 'input', 'menu']:
                                scenario_runner.process_node(bot, message.chat.id, next_node_id)
                                break
                            else:
                                # Продолжаем для обычных блоков
                                scenario_runner.process_node(bot, message.chat.id, next_node_id)
                                next_node_id = scenario_runner.get_next_node_id(next_node_id)
                        else:
                            scenario_runner.process_node(bot, message.chat.id, next_node_id)
                            next_node_id = scenario_runner.get_next_node_id(next_node_id)
                else:
                    bot.send_message(message.chat.id, "🚀 Бот запущен! Напишите что-нибудь.")
            except Exception as e:
                logger.error(f"❌ Ошибка в /start: {e}")
        
        # Добавляем обработчики для остальных типов блоков (кнопки, inline-кнопки и т.д.)
        # ... (остальные обработчики можно добавить при необходимости)
        
        logger.info("🤖 Бот запущен и ожидает сообщений...")
        bot.polling(none_stop=True)
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")


if __name__ == "__main__":
    run_bot()

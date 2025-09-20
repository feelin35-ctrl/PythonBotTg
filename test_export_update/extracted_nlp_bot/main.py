#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый бот с обработкой естественного языка
"""

import os
import sys
import logging
import json
import telebot
import threading
import time

# Добавляем текущую директорию в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
        tokens_path = "bot_tokens.json"
        if not os.path.exists(tokens_path):
            logger.error("Файл токенов не найден")
            return
        
        with open(tokens_path, "r", encoding="utf-8") as f:
            tokens = json.load(f)
        
        bot_token = tokens.get("nlp_test")
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
                bot.send_message(message.chat.id, "Привет! Я бот с возможностью понимания естественного языка. Задай мне вопрос!")
            except Exception as e:
                logger.error(f"❌ Ошибка в /start: {e}")
        
        @bot.message_handler(func=lambda message: True)
        def handle_all_messages(message):
            """Обрабатывает все входящие сообщения"""
            try:
                logger.info(f"💬 Сообщение от {message.chat.id}: {message.text}")
                
                # Простая обработка естественного языка
                user_message = message.text.lower()
                
                # База знаний для простого понимания естественного языка
                knowledge_base = {
                    "привет": ["привет", "здравствуй", "здравствуйте", "hi", "hello"],
                    "пока": ["пока", "до свидания", "прощай", "goodbye", "bye"],
                    "помощь": ["помоги", "помощь", "help", "поддержка", "support"],
                    "время": ["время", "который час", "time", "сколько времени"],
                    "имя": ["как тебя зовут", "твое имя", "what is your name", "имя"],
                    "возраст": ["сколько тебе лет", "твой возраст", "how old are you", "возраст"],
                    "функции": ["что ты умеешь", "твои возможности", "what can you do", "функции"],
                }
                
                responses = {
                    "привет": "Привет! Рад видеть вас! Чем могу помочь?",
                    "пока": "До свидания! Буду рад помочь вам снова!",
                    "помощь": "Я могу ответить на различные вопросы, помочь с информацией и выполнить разные задачи. Просто задайте мне вопрос!",
                    "время": "Извините, у меня нет доступа к текущему времени, но я могу помочь с другими вопросами!",
                    "имя": "Меня зовут ваш виртуальный помощник! Я создан для того, чтобы помогать вам.",
                    "возраст": "Я виртуальный помощник, поэтому у меня нет возраста в привычном понимании!",
                    "функции": "Я могу отвечать на вопросы, предоставлять информацию, помогать с различными задачами и многое другое!",
                    "default": "Спасибо за ваше сообщение! Я постараюсь помочь вам с этим вопросом. Можете уточнить, что именно вам нужно?"
                }
                
                # Поиск соответствия в базе знаний
                response = responses["default"]
                for category, keywords in knowledge_base.items():
                    for keyword in keywords:
                        if keyword in user_message:
                            response = responses[category]
                            break
                    if response != responses["default"]:
                        break
                
                # Отправляем ответ пользователю
                bot.send_message(message.chat.id, response)
                
            except Exception as e:
                logger.error(f"❌ Ошибка обработки сообщения: {e}")
                bot.send_message(message.chat.id, "Извините, произошла ошибка при обработке вашего сообщения.")
        
        logger.info("🤖 Бот запущен и ожидает сообщений...")
        bot.polling(none_stop=True)
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")


if __name__ == "__main__":
    run_bot()
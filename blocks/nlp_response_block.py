from .base_block import BaseBlock
import telebot
from typing import Dict, Any, Optional
import logging
import json
import re

logger = logging.getLogger(__name__)

class NLPResponseBlock(BaseBlock):
    """Блок для обработки естественного языка и формирования ответов на основе контекста"""
    
    # База знаний для простого понимания естественного языка
    KNOWLEDGE_BASE = {
        "привет": ["привет", "здравствуй", "здравствуйте", "hi", "hello"],
        "пока": ["пока", "до свидания", "прощай", "goodbye", "bye"],
        "помощь": ["помоги", "помощь", "help", "поддержка", "support"],
        "время": ["время", "который час", "time", "сколько времени"],
        "имя": ["как тебя зовут", "твое имя", "what is your name", "имя"],
        "возраст": ["сколько тебе лет", "твой возраст", "how old are you", "возраст"],
        "функции": ["что ты умеешь", "твои возможности", "what can you do", "функции"],
    }
    
    RESPONSES = {
        "привет": "Привет! Рад видеть вас! Чем могу помочь?",
        "пока": "До свидания! Буду рад помочь вам снова!",
        "помощь": "Я могу ответить на различные вопросы, помочь с информацией и выполнить разные задачи. Просто задайте мне вопрос!",
        "время": "Извините, у меня нет доступа к текущему времени, но я могу помочь с другими вопросами!",
        "имя": "Меня зовут ваш виртуальный помощник! Я создан для того, чтобы помогать вам.",
        "возраст": "Я виртуальный помощник, поэтому у меня нет возраста в привычном понимании!",
        "функции": "Я могу отвечать на вопросы, предоставлять информацию, помогать с различными задачами и многое другое!",
        "default": "Спасибо за ваше сообщение! Я постараюсь помочь вам с этим вопросом. Можете уточнить, что именно вам нужно?"
    }
    
    @staticmethod
    def get_block_type() -> str:
        return "nlp_response"

    def execute(self, bot: telebot.TeleBot, chat_id: int, **kwargs) -> Optional[str]:
        """Выполняет обработку сообщения пользователя и формирует ответ"""
        try:
            # Получаем текст сообщения пользователя
            user_message = kwargs.get('user_message', '')
            
            if not user_message:
                bot.send_message(chat_id, "Пожалуйста, отправьте текстовое сообщение.")
                return None
            
            # Анализируем сообщение и формируем ответ
            response = self.generate_response(user_message.lower())
            
            # Отправляем ответ пользователю
            bot.send_message(chat_id, response)
            
        except Exception as e:
            logger.error(f"Ошибка в блоке NLP ответа: {e}")
            bot.send_message(chat_id, "Извините, произошла ошибка при обработке вашего сообщения.")
        
        # Возвращаем None, чтобы ScenarioRunner сам нашел следующий узел
        return None

    def generate_response(self, user_message: str) -> str:
        """Генерирует ответ на основе сообщения пользователя"""
        # Проверяем совпадения с ключевыми словами
        for category, keywords in self.KNOWLEDGE_BASE.items():
            for keyword in keywords:
                if keyword in user_message:
                    return self.RESPONSES.get(category, self.RESPONSES["default"])
        
        # Если нет точных совпадений, используем ответ по умолчанию
        return self.RESPONSES["default"]
        
    def extract_entities(self, message: str) -> Dict[str, Any]:
        """Извлекает сущности из сообщения (для расширения функциональности)"""
        entities = {
            "numbers": re.findall(r'\d+', message),
            "emails": re.findall(r'\S+@\S+', message),
            "urls": re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message)
        }
        return entities
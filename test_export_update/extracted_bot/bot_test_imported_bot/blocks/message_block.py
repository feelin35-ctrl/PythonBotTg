from .base_block import BaseBlock
import telebot
from typing import Dict, Any, Optional


class MessageBlock(BaseBlock):

    @staticmethod
    def get_block_type() -> str:
        return "message"

    def execute(self, bot: telebot.TeleBot, chat_id: int, **kwargs) -> Optional[str]:
        message_text = self.node_data.get('data', {}).get('label', '')
        if message_text:
            bot.send_message(chat_id, message_text)

        # Возвращаем None, чтобы ScenarioRunner сам нашел следующий узел
        return None
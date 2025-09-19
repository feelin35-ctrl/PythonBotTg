from .base_block import BaseBlock
import telebot
from typing import Dict, Any, Optional

class EndBlock(BaseBlock):

    @staticmethod
    def get_block_type() -> str:
        return "end"

    def execute(self, bot: telebot.TeleBot, chat_id: int, **kwargs) -> Optional[str]:
        # Конечный блок завершает диалог
        bot.send_message(chat_id, "Спасибо за общение! 👋")
        return None
from .base_block import BaseBlock
import telebot
from typing import Dict, Any, Optional


class StartBlock(BaseBlock):

    @staticmethod
    def get_block_type() -> str:
        return "start"

    def execute(self, bot: telebot.TeleBot, chat_id: int, **kwargs) -> Optional[str]:
        # Стартовый блок просто передает управление дальше
        # ScenarioRunner сам найдет следующий узел
        return None
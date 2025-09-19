from .base_block import BaseBlock
import telebot
from typing import Dict, Any, Optional

class ConditionBlock(BaseBlock):

    @staticmethod
    def get_block_type() -> str:
        return "condition"

    def execute(self, bot: telebot.TeleBot, chat_id: int, **kwargs) -> Optional[str]:
        condition = self.node_data.get('data', {}).get('condition', '')
        if condition:
            bot.send_message(chat_id, f"Условие: {condition}")
        return None

    def get_next_node_id_for_condition(self, condition_result: bool, edges) -> Optional[str]:
        """Получает следующий узел в зависимости от результата условия"""
        handle_id = "yes" if condition_result else "no"
        return self.get_next_node_id(edges, handle_id)
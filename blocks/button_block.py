from .base_block import BaseBlock
import telebot
from typing import Dict, Any, Optional


class ButtonBlock(BaseBlock):

    @staticmethod
    def get_block_type() -> str:
        return "button"

    def execute(self, bot: telebot.TeleBot, chat_id: int, **kwargs) -> Optional[str]:
        buttons = self.node_data.get('data', {}).get('buttons', [])
        if not buttons:
            return None

        # Создаем клавиатуру
        markup = telebot.types.ReplyKeyboardMarkup(
            one_time_keyboard=True,
            resize_keyboard=True
        )

        for button in buttons:
            markup.add(telebot.types.KeyboardButton(button.get('label', '')))

        bot.send_message(chat_id, "Выберите вариант:", reply_markup=markup)

        # Для кнопок следующий узел определяется при нажатии
        return None
from .base_block import BaseBlock
import telebot
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class InlineButtonBlock(BaseBlock):

    @staticmethod
    def get_block_type() -> str:
        return "inline_button"

    def execute(self, bot: telebot.TeleBot, chat_id: int, **kwargs) -> Optional[str]:
        buttons = self.node_data.get('data', {}).get('buttons', [])
        message_text = self.node_data.get('data', {}).get('label', '')

        # Если текст сообщения пустой, используем заглушку
        if not message_text:
            message_text = "Выберите вариант:"
            logger.warning("⚠️ Текст сообщения для inline-кнопок пустой, используется заглушка")

        if not buttons:
            logger.warning("⚠️ Нет кнопок для inline-кнопок")
            bot.send_message(chat_id, message_text)
            return None

        try:
            # Создаем inline-клавиатуру
            markup = telebot.types.InlineKeyboardMarkup()

            for button in buttons:
                button_text = button.get('label', '')
                if not button_text:
                    button_text = "Кнопка"
                    logger.warning("⚠️ Текст кнопки пустой, используется заглушка")

                callback_data = button.get('callbackData', f"btn_{hash(button_text) % 10000}")
                markup.add(telebot.types.InlineKeyboardButton(
                    text=button_text,
                    callback_data=callback_data
                ))

            logger.info(f"📨 Отправляем сообщение с inline-кнопками: {message_text}")
            bot.send_message(chat_id, message_text, reply_markup=markup)

        except Exception as e:
            logger.error(f"❌ Ошибка отправки inline-кнопок: {e}")
            # Fallback: отправляем просто сообщение
            try:
                bot.send_message(chat_id, message_text)
                for button in buttons:
                    button_text = button.get('label', 'Кнопка')
                    bot.send_message(chat_id, f"🔘 {button_text}")
            except Exception as fallback_error:
                logger.error(f"❌ Ошибка fallback: {fallback_error}")

        return None

    def get_next_node_id_for_button(self, callback_data: str, edges) -> Optional[str]:
        """Получает следующий узел для конкретной inline-кнопки"""
        buttons = self.node_data.get('data', {}).get('buttons', [])

        for index, button in enumerate(buttons):
            button_text = button.get('label', 'Кнопка')
            btn_callback = button.get('callbackData', f"btn_{hash(button_text) % 10000}")
            if btn_callback == callback_data:
                return self.get_next_node_id(edges, str(index))

        return None
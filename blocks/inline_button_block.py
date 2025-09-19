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
        hide_keyboard = self.node_data.get('data', {}).get('hideKeyboard', False)
        layout = self.node_data.get('data', {}).get('buttonLayout', 'column')  # 'row' или 'column'
        buttons_per_row = self.node_data.get('data', {}).get('buttonsPerRow', 8)  # Количество кнопок в ряду

        # Если нет кнопок, не отправляем сообщение
        if not buttons:
            logger.warning("⚠️ Нет кнопок для inline-кнопок")
            return None

        # Если текст сообщения пустой, используем пустую строку (Telegram поддерживает это)
        if not message_text or not message_text.strip():
            message_text = ""
            logger.info("ℹ️ Текст сообщения пустой, отправляем только inline-кнопки")

        try:
            if hide_keyboard:
                # Отправляем обычное сообщение с перечислением вариантов
                button_text = f"{message_text}\n\nВарианты:\n"
                for i, button in enumerate(buttons):
                    button_text += f"{i+1}. {button.get('label', '')}\n"
                bot.send_message(chat_id, button_text)
            else:
                # Создаем inline-клавиатуру
                markup = telebot.types.InlineKeyboardMarkup()

                if layout == 'row':
                    # Ограничиваем количество кнопок в ряду от 1 до 8
                    buttons_per_row = max(1, min(8, buttons_per_row))
                    
                    # Размещаем кнопки в ряды по указанному количеству
                    current_row = []
                    for i, button in enumerate(buttons):
                        button_text = button.get('label', '')
                        if not button_text:
                            button_text = "Кнопка"
                            logger.warning("⚠️ Текст кнопки пустой, используется заглушка")

                        callback_data = button.get('callbackData', f"btn_{hash(button_text) % 10000}")
                        current_row.append(telebot.types.InlineKeyboardButton(
                            text=button_text,
                            callback_data=callback_data
                        ))
                        
                        # Добавляем ряд если набралось нужное количество кнопок или это последняя кнопка
                        if len(current_row) == buttons_per_row or i == len(buttons) - 1:
                            markup.row(*current_row)
                            current_row = []
                else:
                    # Размещаем кнопки в столбик (по умолчанию)
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

        # Проверяем, если это числовой callback_data для скрытой клавиатуры
        if callback_data.startswith('btn_') and callback_data[4:].isdigit():
            index = int(callback_data[4:])
            if 0 <= index < len(buttons):
                return self.get_next_node_id(edges, str(index))

        # Обычная проверка по callback_data
        for index, button in enumerate(buttons):
            button_text = button.get('label', 'Кнопка')
            btn_callback = button.get('callbackData', f"btn_{hash(button_text) % 10000}")
            if btn_callback == callback_data:
                return self.get_next_node_id(edges, str(index))

        return None
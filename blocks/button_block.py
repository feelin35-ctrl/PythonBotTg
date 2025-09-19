from .base_block import BaseBlock
import telebot
from typing import Dict, Any, Optional


class ButtonBlock(BaseBlock):

    @staticmethod
    def get_block_type() -> str:
        return "button"

    def execute(self, bot: telebot.TeleBot, chat_id: int, **kwargs) -> Optional[str]:
        buttons = self.node_data.get('data', {}).get('buttons', [])
        hide_keyboard = self.node_data.get('data', {}).get('hideKeyboard', False)
        layout = self.node_data.get('data', {}).get('buttonLayout', 'column')  # 'row' или 'column'
        buttons_per_row = self.node_data.get('data', {}).get('buttonsPerRow', 8)  # Количество кнопок в ряду
        message_text = self.node_data.get('data', {}).get('label', '')  # Текст сообщения с кнопками
        
        if not buttons:
            return None

        # Создаем клавиатуру
        if hide_keyboard:
            # Отправляем сообщение без клавиатуры, но показываем варианты
            button_text = "Варианты ответа:\n"
            for i, button in enumerate(buttons):
                button_text += f"{i+1}. {button.get('label', '')}\n"
            bot.send_message(chat_id, button_text)
        else:
            # Обычная клавиатура
            markup = telebot.types.ReplyKeyboardMarkup(
                one_time_keyboard=True,
                resize_keyboard=True
            )

            if layout == 'row':
                # Ограничиваем количество кнопок в ряду от 1 до 8
                buttons_per_row = max(1, min(8, buttons_per_row))
                
                # Размещаем кнопки в ряды по указанному количеству
                current_row = []
                for i, button in enumerate(buttons):
                    current_row.append(telebot.types.KeyboardButton(button.get('label', '')))
                    
                    # Добавляем ряд если набралось нужное количество кнопок или это последняя кнопка
                    if len(current_row) == buttons_per_row or i == len(buttons) - 1:
                        markup.row(*current_row)  # Используем row() для горизонтального размещения
                        current_row = []
            else:
                # Размещаем кнопки в столбик (по умолчанию)
                for button in buttons:
                    markup.add(telebot.types.KeyboardButton(button.get('label', '')))

            # Отправляем клавиатуру с настраиваемым текстом или невидимым символом
            if not message_text or not message_text.strip():
                message_text = "\u200B"  # Невидимый символ вместо текста
            
            bot.send_message(chat_id, message_text, reply_markup=markup)

        # Для кнопок следующий узел определяется при нажатии
        return None
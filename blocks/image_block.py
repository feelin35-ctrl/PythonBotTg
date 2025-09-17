from .base_block import BaseBlock
import telebot
from typing import Dict, Any, Optional


class ImageBlock(BaseBlock):

    @staticmethod
    def get_block_type() -> str:
        return "image"

    def execute(self, bot: telebot.TeleBot, chat_id: int, **kwargs) -> Optional[str]:
        image_url = self.node_data.get('data', {}).get('url', '')
        if not image_url:
            return None

        # Пытаемся отправить изображение
        try:
            bot.send_photo(chat_id, image_url)
        except Exception as e:
            # Если не удалось, отправляем ссылку
            bot.send_message(chat_id, f"🖼️ Изображение: {image_url}")

        # Возвращаем None, чтобы ScenarioRunner сам нашел следующий узел
        return None
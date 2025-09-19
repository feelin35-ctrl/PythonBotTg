from .base_block import BaseBlock
import telebot
from typing import Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)


class FileBlock(BaseBlock):

    @staticmethod
    def get_block_type() -> str:
        return "file"

    def execute(self, bot: telebot.TeleBot, chat_id: int, **kwargs) -> Optional[str]:
        files = self.node_data.get('data', {}).get('files', [])
        caption = self.node_data.get('data', {}).get('caption', '')
        
        if not files:
            logger.warning("⚠️ Нет файлов для отправки")
            if caption:
                bot.send_message(chat_id, caption)
            return None

        try:
            for file_info in files:
                file_path = file_info.get('path', '').strip()
                file_name = file_info.get('name', '').strip()
                
                if not file_path:
                    logger.warning(f"⚠️ Пустой путь к файлу: {file_info}")
                    continue
                
                # Проверяем существование файла
                if not os.path.exists(file_path):
                    logger.error(f"❌ Файл не найден: {file_path}")
                    bot.send_message(chat_id, f"❌ Файл не найден: {file_name or file_path}")
                    continue
                
                # Определяем тип файла по расширению
                file_extension = os.path.splitext(file_path)[1].lower()
                
                try:
                    with open(file_path, 'rb') as file:
                        if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                            # Отправляем как фото
                            bot.send_photo(
                                chat_id, 
                                file, 
                                caption=caption if len(files) == 1 else f"{caption}\n📷 {file_name}" if caption else f"📷 {file_name}"
                            )
                        elif file_extension in ['.mp4', '.avi', '.mkv', '.mov', '.webm']:
                            # Отправляем как видео
                            bot.send_video(
                                chat_id, 
                                file, 
                                caption=caption if len(files) == 1 else f"{caption}\n🎥 {file_name}" if caption else f"🎥 {file_name}"
                            )
                        elif file_extension in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
                            # Отправляем как аудио
                            bot.send_audio(
                                chat_id, 
                                file, 
                                caption=caption if len(files) == 1 else f"{caption}\n🎵 {file_name}" if caption else f"🎵 {file_name}"
                            )
                        else:
                            # Отправляем как документ
                            bot.send_document(
                                chat_id, 
                                file, 
                                caption=caption if len(files) == 1 else f"{caption}\n📄 {file_name}" if caption else f"📄 {file_name}"
                            )
                        
                        logger.info(f"✅ Файл отправлен: {file_name or file_path}")
                        
                except Exception as file_error:
                    logger.error(f"❌ Ошибка отправки файла {file_path}: {file_error}")
                    bot.send_message(chat_id, f"❌ Ошибка отправки файла: {file_name or file_path}")

        except Exception as e:
            logger.error(f"❌ Ошибка выполнения файлового блока: {e}")
            bot.send_message(chat_id, "❌ Ошибка отправки файлов")

        # Возвращаем None, чтобы ScenarioRunner сам нашел следующий узел
        return None
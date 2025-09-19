from .base_block import BaseBlock
import telebot
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MenuBlock(BaseBlock):

    @staticmethod
    def get_block_type() -> str:
        return "menu"

    def execute(self, bot: telebot.TeleBot, chat_id: int, **kwargs) -> Optional[str]:
        menu_items = self.node_data.get('data', {}).get('menuItems', [])
        menu_title = self.node_data.get('data', {}).get('label', 'Главное меню')
        
        if not menu_items:
            logger.warning("⚠️ Нет пунктов меню")
            bot.send_message(chat_id, menu_title)
            return None

        try:
            # Создаем команды меню для бота
            commands = []
            for item in menu_items:
                command = item.get('command', '').strip()
                description = item.get('description', '').strip()
                
                if command and description:
                    # Убираем / если есть, и добавляем обратно для единообразия
                    if command.startswith('/'):
                        command = command[1:]
                    commands.append(telebot.types.BotCommand(command, description))
            
            # Добавляем команду "Назад" автоматически
            commands.append(telebot.types.BotCommand("назад", "Вернуться на предыдущий шаг"))

            # Устанавливаем меню команд для бота
            if commands:
                bot.set_my_commands(commands)
                logger.info(f"📋 Установлено меню с {len(commands)} командами (включая 'Назад')")
            
            # Отправляем только заголовок меню, без описаний команд
            # Описания уже установлены в меню бота через set_my_commands
            bot.send_message(chat_id, menu_title)

        except Exception as e:
            logger.error(f"❌ Ошибка установки меню: {e}")
            bot.send_message(chat_id, f"{menu_title}\nОшибка установки меню.")

        # Возвращаем None, чтобы ScenarioRunner сам нашел следующий узел
        return None
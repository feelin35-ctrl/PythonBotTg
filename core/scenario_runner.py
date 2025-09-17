from typing import Dict, List, Optional
import telebot
from .block_registry import block_registry
import logging

logger = logging.getLogger(__name__)


class ScenarioRunner:
    """Исполнитель сценариев Telegram бота"""

    def __init__(self, scenario_data: Dict):
        self.scenario_data = scenario_data
        self.nodes_map = self._create_nodes_map()

    def _create_nodes_map(self) -> Dict[str, any]:
        """Создает карту узлов с экземплярами блоков"""
        nodes_map = {}
        for node in self.scenario_data.get('nodes', []):
            try:
                block = block_registry.create_block_instance(node)
                nodes_map[node['id']] = block
            except Exception as e:
                logger.error(f"Ошибка создания блока {node.get('id')}: {e}")
        return nodes_map

    def get_next_node_id(self, current_node_id: str, handle_id: Optional[str] = None) -> Optional[str]:
        """Находит следующий узел на основе связей (работает со словарями)"""
        edges = self.scenario_data.get('edges', [])
        logger.info(f"🔍 Ищем следующий узел для {current_node_id}, handle: {handle_id}")

        for edge in edges:
            if edge.get('source') == current_node_id:
                if handle_id is None or edge.get('sourceHandle') == handle_id:
                    target = edge.get('target')
                    logger.info(f"   ✅ Найдено совпадение: {target}")
                    return target
        logger.info("   ❌ Совпадений не найдено")
        return None

    def process_node(self, bot: telebot.TeleBot, chat_id: int, node_id: str, **kwargs) -> Optional[str]:
        """Обрабатывает указанный узел"""
        block = self.nodes_map.get(node_id)
        if not block:
            logger.error(f"❌ Узел {node_id} не найден")
            return None

        try:
            logger.info(f"🔹 Обрабатываем узел {node_id} типа {block.type}")

            # Выполняем блок
            next_node_id = block.execute(bot, chat_id, **kwargs)

            # Если блок не вернул следующий узел, ищем его по связям
            if next_node_id is None:
                next_node_id = self.get_next_node_id(node_id)

            if next_node_id:
                logger.info(f"➡️ Переходим к узлу {next_node_id}")
                return next_node_id
            else:
                logger.info("⏹️ Конец цепочки")
                return None

        except Exception as e:
            logger.error(f"❌ Ошибка в узле {node_id}: {e}")
            try:
                bot.send_message(chat_id, "Произошла ошибка при обработке запроса 😔")
            except:
                pass
            return None

    def handle_inline_button_press(self, bot: telebot.TeleBot, call, node_id: str, callback_data: str) -> Optional[str]:
        """Обрабатывает нажатие inline-кнопки"""
        block = self.nodes_map.get(node_id)
        if not block or not hasattr(block, 'type') or block.type != 'inline_button':
            return None

        try:
            # Ответим на callback запрос
            bot.answer_callback_query(call.id)

            # Ищем следующий узел для этой кнопки
            next_node_id = block.get_next_node_id_for_button(
                callback_data,
                self.scenario_data.get('edges', [])
            )

            if next_node_id:
                logger.info(f"🔘 Нажата inline-кнопка {callback_data}, переходим к {next_node_id}")
                # Редактируем сообщение чтобы убрать клавиатуру
                try:
                    bot.edit_message_reply_markup(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=None
                    )
                except:
                    pass  # Игнорируем ошибки редактирования

                return self.process_node(bot, call.message.chat.id, next_node_id)
            else:
                bot.send_message(call.message.chat.id, "Спасибо за выбор!")
                return None

        except Exception as e:
            logger.error(f"❌ Ошибка обработки inline-кнопки: {e}")
            return None

    def handle_button_press(self, bot: telebot.TeleBot, chat_id: int, node_id: str, button_index: int) -> Optional[str]:
        """Обрабатывает нажатие кнопки"""
        block = self.nodes_map.get(node_id)
        if not block or not hasattr(block, 'type') or block.type != 'button':
            return None

        try:
            # Ищем следующий узел для этой кнопки
            next_node_id = self.get_next_node_id(node_id, str(button_index))

            if next_node_id:
                logger.info(f"🔘 Нажата кнопка {button_index}, переходим к {next_node_id}")
                return self.process_node(bot, chat_id, next_node_id)
            else:
                bot.send_message(chat_id, "Спасибо за выбор!")
                return None

        except Exception as e:
            logger.error(f"❌ Ошибка обработки кнопки: {e}")
            return None
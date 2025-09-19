from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import telebot
import logging

logger = logging.getLogger(__name__)


class BaseBlock(ABC):
    """Абстрактный базовый класс для всех блоков"""

    def __init__(self, node_data: Dict[str, Any]):
        self.node_data = node_data
        self.type = self.get_block_type()

    @staticmethod
    @abstractmethod
    def get_block_type() -> str:
        """Возвращает тип блока"""
        pass

    @abstractmethod
    def execute(self, bot: telebot.TeleBot, chat_id: int, **kwargs) -> Optional[str]:
        """
        Выполняет логику блока
        Returns: ID следующего узла или None
        """
        pass

    def get_next_node_id(self, edges, handle_id: Optional[str] = None) -> Optional[str]:
        """Находит следующий узел на основе связей"""
        logger.warning(
            "⚠️ Используется устаревший метод get_next_node_id. Используйте ScenarioRunner.get_next_node_id()")
        for edge in edges:
            if edge.get('source') == self.node_data.get('id'):
                if handle_id is None or edge.get('sourceHandle') == handle_id:
                    return edge.get('target')
        return None
from typing import Dict, Type
import logging

logger = logging.getLogger(__name__)


class BlockRegistry:
    """Реестр для управления всеми типами блоков"""

    def __init__(self):
        self._blocks: Dict[str, Type] = {}
        self._register_core_blocks()

    def _register_core_blocks(self):
        """Регистрирует основные блоки вручную"""
        try:
            # Импортируем и регистрируем каждый блок отдельно
            from blocks.message_block import MessageBlock
            from blocks.image_block import ImageBlock
            from blocks.button_block import ButtonBlock
            from blocks.inline_button_block import InlineButtonBlock
            from blocks.start_block import StartBlock
            from blocks.end_block import EndBlock
            from blocks.condition_block import ConditionBlock
            from blocks.menu_block import MenuBlock
            from blocks.file_block import FileBlock

            core_blocks = [
                MessageBlock,
                ImageBlock,
                ButtonBlock,
                InlineButtonBlock,
                StartBlock,
                EndBlock,
                ConditionBlock,
                MenuBlock,
                FileBlock
            ]

            for block_class in core_blocks:
                self.register_block(block_class)

        except ImportError as e:
            logger.error(f"Ошибка импорта блоков: {e}")

    def register_block(self, block_class):
        """Регистрирует новый тип блока"""
        block_type = block_class.get_block_type()
        self._blocks[block_type] = block_class
        logger.info(f"✅ Зарегистрирован блок: {block_type}")

    def get_block(self, block_type: str):
        """Возвращает класс блока по типу"""
        return self._blocks.get(block_type)

    def create_block_instance(self, node_data: Dict):
        """Создает экземпляр блока на основе данных узла"""
        block_type = node_data.get('type')
        if not block_type:
            raise ValueError("Node data must contain 'type'")

        block_class = self.get_block(block_type)
        if not block_class:
            raise ValueError(f"Unknown block type: {block_type}")

        return block_class(node_data)

    def get_available_blocks(self) -> list:
        """Возвращает список доступных типов блоков"""
        return list(self._blocks.keys())


# Глобальный экземпляр реестра
block_registry = BlockRegistry()
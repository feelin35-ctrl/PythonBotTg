from blocks.base_block import BaseBlock
from typing import Dict, List, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)


class KeywordProcessorBlock(BaseBlock):
    """Блок для обработки текстовых сообщений с ключевыми словами"""
    
    def __init__(self, node_data: Dict[str, Any]):
        super().__init__(node_data)
        self.type = "keyword_processor"
        
        # Получаем данные блока
        self.node_data = node_data
        self.data = node_data.get('data', {})
        
        # Получаем список ключевых слов из данных блока
        self.keywords = self.data.get('keywords', [])
        
        # Получаем чувствительность к регистру
        self.case_sensitive = self.data.get('caseSensitive', False)
        
        # Получаем режим сопоставления (точное совпадение или частичное)
        self.match_mode = self.data.get('matchMode', 'exact')  # 'exact' или 'partial'
        
        logger.info(f"Создан блок обработки ключевых слов: {self.keywords}")

    @staticmethod
    def get_block_type() -> str:
        """Возвращает тип блока"""
        return "keyword_processor"

    @classmethod
    def get_node_label(cls) -> str:
        """Возвращает метку узла для отображения в редакторе"""
        return "Обработка по ключевым словам"

    @classmethod
    def get_node_description(cls) -> str:
        """Возвращает описание узла для отображения в редакторе"""
        return "Блок для обработки текстовых сообщений с использованием ключевых слов"

    @classmethod
    def get_node_icon(cls) -> str:
        """Возвращает иконку узла для отображения в редакторе"""
        return "🔍"

    @classmethod
    def get_node_color(cls) -> str:
        """Возвращает цвет узла для отображения в редакторе"""
        return "#FF9800"  # Оранжевый цвет

    @classmethod
    def get_node_fields(cls) -> List[Dict[str, Any]]:
        """Возвращает список полей узла для отображения в редакторе"""
        return [
            {
                "name": "keywords",
                "label": "Ключевые слова",
                "type": "array",
                "description": "Список ключевых слов для поиска в сообщении",
                "default": []
            },
            {
                "name": "caseSensitive",
                "label": "Чувствительность к регистру",
                "type": "boolean",
                "description": "Учитывать ли регистр при поиске ключевых слов",
                "default": False
            },
            {
                "name": "matchMode",
                "label": "Режим сопоставления",
                "type": "select",
                "options": [
                    {"value": "exact", "label": "Точное совпадение"},
                    {"value": "partial", "label": "Частичное совпадение"}
                ],
                "description": "Режим поиска ключевых слов в сообщении",
                "default": "exact"
            }
        ]

    def process(self, bot, chat_id: int, user_message: str = "", **kwargs) -> bool:
        """
        Обрабатывает текстовое сообщение и проверяет наличие ключевых слов
        
        Args:
            bot: Экземпляр бота
            chat_id: ID чата
            user_message: Текст сообщения пользователя
            **kwargs: Дополнительные параметры
            
        Returns:
            bool: True если обработка успешна
        """
        try:
            logger.info(f"Обработка сообщения в блоке keyword_processor: {user_message}")
            
            if not user_message:
                logger.warning("Получено пустое сообщение")
                # Не отправляем сообщение об ошибке, просто возвращаем False
                return False
                
            # Проверяем наличие ключевых слов в сообщении
            matched_keyword = self._check_keywords(user_message)
            
            if matched_keyword:
                logger.info(f"Найдено ключевое слово: {matched_keyword}")
                # Не отправляем сообщение пользователю, просто возвращаем True
                return True
            else:
                logger.info("Ключевые слова не найдены")
                # Не отправляем сообщение, просто возвращаем False
                # Это позволяет другим блокам обрабатывать сообщение
                return False
                
        except Exception as e:
            logger.error(f"Ошибка обработки блока keyword_processor: {e}")
            # Не отправляем сообщение об ошибке пользователю, просто возвращаем False
            return False

    def _check_keywords(self, message: str) -> Optional[str]:
        """
        Проверяет наличие ключевых слов в сообщении
        
        Args:
            message: Текст сообщения
            
        Returns:
            Optional[str]: Найденное ключевое слово или None
        """
        # Подготавливаем сообщение в зависимости от чувствительности к регистру
        search_message = message if self.case_sensitive else message.lower()
        
        # Проверяем каждое ключевое слово
        for keyword in self.keywords:
            if not keyword:  # Пропускаем пустые ключевые слова
                continue
                
            # Подготавливаем ключевое слово в зависимости от чувствительности к регистру
            search_keyword = keyword if self.case_sensitive else keyword.lower()
            
            # Проверяем в зависимости от режима сопоставления
            if self.match_mode == 'exact':
                # Точное совпадение - ключевое слово должно быть отдельным словом
                # Используем регулярное выражение для поиска отдельных слов
                pattern = r'\b' + re.escape(search_keyword) + r'\b'
                if re.search(pattern, search_message):
                    return keyword
            else:
                # Частичное совпадение - ключевое слово может быть частью другого слова
                if search_keyword in search_message:
                    return keyword
                    
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует блок в словарь для сохранения"""
        return {
            "id": self.node_data.get('id'),
            "type": self.type,
            "data": self.data
        }

    def execute(self, bot, chat_id: int, **kwargs) -> Optional[str]:
        """
        Выполняет блок (реализация абстрактного метода)
        
        Args:
            bot: Экземпляр бота
            chat_id: ID чата
            **kwargs: Дополнительные параметры
            
        Returns:
            Optional[str]: ID следующего узла или None
        """
        # Получаем сообщение пользователя из контекста
        user_message = kwargs.get('user_message', '')
        # Выполняем обработку сообщения
        success = self.process(bot, chat_id, user_message, **kwargs)
        
        # Всегда возвращаем None, чтобы ScenarioRunner искал следующий узел по основной связи
        # Это позволяет системе правильно обрабатывать переходы
        return None

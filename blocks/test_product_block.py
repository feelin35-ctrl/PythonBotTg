import unittest
from unittest.mock import Mock, patch
from blocks.product_block import ProductBlock

class TestProductBlock(unittest.TestCase):
    
    def test_product_block_creation(self):
        """Тест создания блока с корректными данными"""
        node_data = {
            "id": "test_product",
            "type": "product_card",
            "data": {
                "photo_url": "https://example.com/photo.jpg",
                "title": "Тестовый товар",
                "description": "Описание тестового товара",
                "price": "1000 руб.",
                "features": [
                    {"key": "Цвет", "value": "Синий"}
                ]
            }
        }
        
        block = ProductBlock(node_data)
        
        # Проверка типа блока
        self.assertEqual(block.get_block_type(), "product_card")
        
        # Проверка создания экземпляра
        self.assertIsInstance(block, ProductBlock)
        
        # Проверка данных
        self.assertEqual(block.photo_url, "https://example.com/photo.jpg")
        self.assertEqual(block.title, "Тестовый товар")
        self.assertEqual(block.description, "Описание тестового товара")
        self.assertEqual(block.price, "1000 руб.")
        self.assertEqual(len(block.features), 1)
        self.assertEqual(block.features[0]["key"], "Цвет")
        self.assertEqual(block.features[0]["value"], "Синий")
    
    def test_product_block_with_minimal_data(self):
        """Тест создания блока с минимальными данными"""
        node_data = {
            "id": "test_product",
            "type": "product_card",
            "data": {}
        }
        
        block = ProductBlock(node_data)
        
        # Проверка типа блока
        self.assertEqual(block.get_block_type(), "product_card")
        
        # Проверка создания экземпляра
        self.assertIsInstance(block, ProductBlock)
        
        # Проверка данных по умолчанию
        self.assertEqual(block.photo_url, "")
        self.assertEqual(block.title, "")
        self.assertEqual(block.description, "")
        self.assertEqual(block.price, "")
        self.assertEqual(block.features, [])
    
    def test_format_product_message_with_all_data(self):
        """Тест форматирования сообщения с полными данными"""
        node_data = {
            "id": "test_product",
            "type": "product_card",
            "data": {
                "title": "Тестовый товар",
                "description": "Описание тестового товара",
                "price": "1000 руб.",
                "features": [
                    {"key": "Цвет", "value": "Синий"},
                    {"key": "Размер", "value": "M"}
                ]
            }
        }
        
        block = ProductBlock(node_data)
        message = block._format_product_message()
        
        # Проверка наличия всех элементов в сообщении
        self.assertIn("*Тестовый товар*", message)
        self.assertIn("Описание тестового товара", message)
        self.assertIn("*Цена:* 1000 руб.", message)
        self.assertIn("*Характеристики:*", message)
        self.assertIn("• Цвет: Синий", message)
        self.assertIn("• Размер: M", message)
    
    def test_format_product_message_with_minimal_data(self):
        """Тест форматирования сообщения с минимальными данными"""
        node_data = {
            "id": "test_product",
            "type": "product_card",
            "data": {}
        }
        
        block = ProductBlock(node_data)
        message = block._format_product_message()
        
        # Проверка сообщения по умолчанию
        self.assertEqual(message, "Карточка товара")
    
    @patch('blocks.product_block.logger')
    def test_execute_with_photo_success(self, mock_logger):
        """Тест выполнения блока с фото (успешная отправка)"""
        node_data = {
            "id": "test_product",
            "type": "product_card",
            "data": {
                "photo_url": "https://example.com/photo.jpg",
                "title": "Тестовый товар",
                "description": "Описание тестового товара",
                "price": "1000 руб.",
                "features": [
                    {"key": "Цвет", "value": "Синий"}
                ]
            }
        }
        
        block = ProductBlock(node_data)
        
        # Создаем моки для бота и chat_id
        mock_bot = Mock()
        chat_id = 12345
        
        # Выполняем блок
        result = block.execute(mock_bot, chat_id)
        
        # Проверяем, что send_photo был вызван с правильными аргументами
        mock_bot.send_photo.assert_called_once_with(
            chat_id=chat_id,
            photo="https://example.com/photo.jpg",
            caption=unittest.mock.ANY,  # caption проверим отдельно
            parse_mode='Markdown'
        )
        
        # Проверяем, что функция возвращает None
        self.assertIsNone(result)
        
        # Проверяем логирование
        mock_logger.info.assert_called()
    
    @patch('blocks.product_block.logger')
    def test_execute_without_photo(self, mock_logger):
        """Тест выполнения блока без фото"""
        node_data = {
            "id": "test_product",
            "type": "product_card",
            "data": {
                "title": "Тестовый товар",
                "description": "Описание тестового товара",
                "price": "1000 руб.",
                "features": [
                    {"key": "Цвет", "value": "Синий"}
                ]
            }
        }
        
        block = ProductBlock(node_data)
        
        # Создаем моки для бота и chat_id
        mock_bot = Mock()
        chat_id = 12345
        
        # Выполняем блок
        result = block.execute(mock_bot, chat_id)
        
        # Проверяем, что send_message был вызван с правильными аргументами
        mock_bot.send_message.assert_called_once_with(
            chat_id=chat_id,
            text=unittest.mock.ANY,  # text проверим отдельно
            parse_mode='Markdown'
        )
        
        # Проверяем, что функция возвращает None
        self.assertIsNone(result)
        
        # Проверяем логирование
        mock_logger.info.assert_called()

if __name__ == '__main__':
    unittest.main()
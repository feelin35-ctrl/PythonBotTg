#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тест для проверки создания блока keyword_processor из данных узла
"""

import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.block_registry import block_registry


def test_block_creation():
    """Тест создания блока keyword_processor"""
    print("Тест создания блока keyword_processor")
    
    # Проверяем, что блок зарегистрирован
    available_blocks = block_registry.get_available_blocks()
    print(f"Доступные блоки: {available_blocks}")
    
    if 'keyword_processor' not in available_blocks:
        print("Блок keyword_processor не зарегистрирован!")
        return
    
    # Создаем тестовые данные узла
    node_data = {
        'id': 'test_node',
        'type': 'keyword_processor',
        'data': {
            'blockType': 'keyword_processor',
            'keywords': ['привет', 'hello', 'тест'],
            'caseSensitive': False,
            'matchMode': 'partial'
        }
    }
    
    # Создаем экземпляр блока
    try:
        block = block_registry.create_block_instance(node_data)
        print(f"Создан блок типа: {block.type}")
        print(f"Ключевые слова: {block.keywords}")
        print(f"Чувствительность к регистру: {block.case_sensitive}")
        print(f"Режим сопоставления: {block.match_mode}")
        
        # Тестируем метод _check_keywords
        test_message = "Привет, это тестовое сообщение"
        result = block._check_keywords(test_message)
        print(f"Проверка сообщения '{test_message}': {result}")
        
    except Exception as e:
        print(f"Ошибка создания блока: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_block_creation()
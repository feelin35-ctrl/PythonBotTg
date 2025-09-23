#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тест для проверки работы блока keyword_processor
"""

import sys
import os
import json

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from blocks.keyword_processor_block import KeywordProcessorBlock


def test_keyword_processor():
    """Тест блока keyword_processor"""
    print("Тест блока keyword_processor")
    
    # Создаем тестовые данные узла
    node_data = {
        'id': 'test_node',
        'type': 'keyword_processor',
        'data': {
            'keywords': ['привет', 'hello', 'тест'],
            'caseSensitive': False,
            'matchMode': 'partial'
        }
    }
    
    # Создаем экземпляр блока
    block = KeywordProcessorBlock(node_data)
    
    print(f"Ключевые слова: {block.keywords}")
    print(f"Чувствительность к регистру: {block.case_sensitive}")
    print(f"Режим сопоставления: {block.match_mode}")
    
    # Тестовые сообщения
    test_messages = [
        "Привет, как дела?",
        "Hello world!",
        "Это тестовое сообщение",
        "Ничего общего",
        "ПРИВЕТ ВСЕМ"
    ]
    
    print("\nРезультаты проверки:")
    for message in test_messages:
        result = block._check_keywords(message)
        print(f"Сообщение: '{message}' -> Найдено: {result}")


if __name__ == "__main__":
    test_keyword_processor()
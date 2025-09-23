#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Полный тест интеграции блока keyword_processor
"""

import sys
import os
import json
from unittest.mock import Mock, MagicMock

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from blocks.keyword_processor_block import KeywordProcessorBlock
from core.block_registry import block_registry
from core.scenario_runner import ScenarioRunner


def test_full_integration():
    """Полный тест интеграции"""
    print("Полный тест интеграции блока keyword_processor")
    
    # Создаем тестовый сценарий
    scenario_data = {
        "nodes": [
            {
                "id": "1",
                "type": "keyword_processor",
                "data": {
                    "blockType": "keyword_processor",
                    "keywords": ["привет", "hello", "тест"],
                    "caseSensitive": False,
                    "matchMode": "partial"
                },
                "position": {"x": 0, "y": 0}
            }
        ],
        "edges": []
    }
    
    # Создаем ScenarioRunner
    scenario_runner = ScenarioRunner(scenario_data)
    
    print(f"Создан ScenarioRunner с {len(scenario_runner.nodes_map)} блоками")
    
    # Проверяем, что блок keyword_processor создан
    if '1' in scenario_runner.nodes_map:
        block = scenario_runner.nodes_map['1']
        print(f"Блок создан: {block.type}")
        print(f"Ключевые слова: {block.keywords}")
        print(f"Чувствительность к регистру: {block.case_sensitive}")
        print(f"Режим сопоставления: {block.match_mode}")
        
        # Создаем mock-объект бота
        mock_bot = Mock()
        
        # Тестируем обработку сообщения
        test_message = "Привет, это тест!"
        print(f"\nТестируем сообщение: '{test_message}'")
        
        # Вызываем метод process напрямую
        success = block.process(mock_bot, 12345, test_message)
        print(f"Результат обработки: {success}")
        
        # Проверяем, что бот отправил сообщение
        if success:
            mock_bot.send_message.assert_called_once()
            call_args = mock_bot.send_message.call_args
            print(f"Отправлено сообщение: {call_args}")
        else:
            print("Сообщение не отправлено")
    else:
        print("Блок keyword_processor не найден!")


if __name__ == "__main__":
    test_full_integration()
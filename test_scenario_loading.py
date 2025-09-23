#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тест для проверки загрузки сценария с блоком keyword_processor
"""

import sys
import os
import json

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import load_scenario


def test_scenario_loading():
    """Тест загрузки сценария"""
    print("Тест загрузки сценария с блоком keyword_processor")
    
    # Создаем тестовый файл сценария
    test_bot_id = "test_keyword_bot"
    test_scenario = {
        "nodes": [
            {
                "id": "1",
                "type": "start",
                "position": {"x": 100, "y": 100},
                "data": {
                    "blockType": "start"
                }
            },
            {
                "id": "2",
                "type": "keyword_processor",
                "position": {"x": 300, "y": 100},
                "data": {
                    "blockType": "keyword_processor",
                    "keywords": ["привет", "hello", "тест"],
                    "caseSensitive": False,
                    "matchMode": "partial"
                }
            }
        ],
        "edges": [
            {
                "id": "e1-2",
                "source": "1",
                "target": "2"
            }
        ]
    }
    
    # Сохраняем тестовый сценарий
    test_file = f"bots/bot_{test_bot_id}.json"
    with open(test_file, "w", encoding="utf-8") as f:
        json.dump(test_scenario, f, ensure_ascii=False, indent=2)
    
    print(f"Создан тестовый файл: {test_file}")
    
    # Загружаем сценарий
    scenario = load_scenario(test_bot_id)
    
    print(f"Загружен сценарий с {len(scenario.nodes)} узлами")
    
    # Проверяем данные узлов
    for node in scenario.nodes:
        print(f"Узел {node.id} (тип: {node.type})")
        if node.data:
            print(f"  blockType: {node.data.blockType}")
            if node.data.blockType == "keyword_processor":
                print(f"  keywords: {node.data.keywords}")
                print(f"  caseSensitive: {node.data.caseSensitive}")
                print(f"  matchMode: {node.data.matchMode}")
    
    # Удаляем тестовый файл
    os.remove(test_file)
    print(f"Удален тестовый файл: {test_file}")


if __name__ == "__main__":
    test_scenario_loading()
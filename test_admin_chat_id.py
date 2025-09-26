import json
import os
import sys

# Добавляем путь к проекту в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import Scenario, Node, Edge

def test_scenario_serialization():
    """Тест для проверки сериализации сценария с admin_chat_id"""
    print("Тест: Проверка сериализации сценария с admin_chat_id")
    
    # Создаем сценарий с admin_chat_id
    scenario = Scenario(
        nodes=[],
        edges=[],
        admin_chat_id="123456789"
    )
    
    # Проверяем model_dump (Pydantic V2)
    dumped = scenario.model_dump()
    print(f"model_dump(): {dumped}")
    
    # Проверяем, что admin_chat_id присутствует
    assert 'admin_chat_id' in dumped, "admin_chat_id должен присутствовать в model_dump()"
    assert dumped['admin_chat_id'] == "123456789", "Значение admin_chat_id должно быть корректным"
    
    print("✅ Тест пройден успешно")
    print()

def test_scenario_with_admin_chat_id_alias():
    """Тест для проверки создания сценария с adminChatId (camelCase)"""
    print("Тест: Проверка создания сценария с adminChatId (camelCase)")
    
    # Создаем сценарий с adminChatId (camelCase)
    scenario_data = {
        "nodes": [],
        "edges": [],
        "adminChatId": "987654321"
    }
    
    scenario = Scenario(**scenario_data)
    
    # Проверяем model_dump (Pydantic V2)
    dumped = scenario.model_dump()
    print(f"model_dump(): {dumped}")
    
    # Проверяем, что admin_chat_id присутствует и имеет правильное значение
    assert 'admin_chat_id' in dumped, "admin_chat_id должен присутствовать в model_dump()"
    assert dumped['admin_chat_id'] == "987654321", "Значение admin_chat_id должно быть корректным"
    
    print("✅ Тест пройден успешно")
    print()

def test_scenario_with_both_formats():
    """Тест для проверки создания сценария с обоими форматами"""
    print("Тест: Проверка создания сценария с обоими форматами")
    
    # Создаем сценарий с обоими форматами
    scenario_data = {
        "nodes": [],
        "edges": [],
        "admin_chat_id": "111111111",
        "adminChatId": "222222222"
    }
    
    scenario = Scenario(**scenario_data)
    
    # Проверяем model_dump (Pydantic V2)
    dumped = scenario.model_dump()
    print(f"model_dump(): {dumped}")
    
    # Проверяем, что admin_chat_id присутствует и имеет правильное значение
    # Приоритет должен быть у adminChatId
    assert 'admin_chat_id' in dumped, "admin_chat_id должен присутствовать в model_dump()"
    assert dumped['admin_chat_id'] == "222222222", "Значение admin_chat_id должно быть равно adminChatId"
    
    print("✅ Тест пройден успешно")
    print()

if __name__ == "__main__":
    print("Запуск тестов для проверки работы с admin_chat_id...")
    print()
    
    test_scenario_serialization()
    test_scenario_with_admin_chat_id_alias()
    test_scenario_with_both_formats()
    
    print("Все тесты пройдены успешно! 🎉")
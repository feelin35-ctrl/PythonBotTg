import json
import os
import sys
from unittest.mock import patch, mock_open

# Добавляем путь к проекту в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Мокаем load_scenario
def mock_load_scenario(bot_id):
    from main import Scenario
    return Scenario(
        nodes=[],
        edges=[],
        admin_chat_id="123456789"
    )

# Тестируем эндпоинт get_scenario
def test_get_scenario_endpoint():
    """Тест для проверки работы эндпоинта get_scenario"""
    print("Тест: Проверка работы эндпоинта get_scenario")
    
    # Мокаем load_scenario
    with patch('main.load_scenario', side_effect=mock_load_scenario):
        from main import get_scenario
        
        # Вызываем эндпоинт
        result = get_scenario("test_bot")
        print(f"Результат: {result}")
        
        # Проверяем, что результат содержит admin_chat_id
        assert 'admin_chat_id' in result, "Результат должен содержать admin_chat_id"
        assert result['admin_chat_id'] == "123456789", "Значение admin_chat_id должно быть корректным"
        
        # Проверяем, что результат содержит adminChatId для совместимости с фронтендом
        assert 'adminChatId' in result, "Результат должен содержать adminChatId для совместимости с фронтендом"
        assert result['adminChatId'] == "123456789", "Значение adminChatId должно совпадать с admin_chat_id"
        
        print("✅ Тест пройден успешно")
        print()

if __name__ == "__main__":
    print("Запуск тестов для проверки эндпоинта get_scenario...")
    print()
    
    test_get_scenario_endpoint()
    
    print("Все тесты пройдены успешно! 🎉")
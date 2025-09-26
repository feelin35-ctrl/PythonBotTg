import json
import os
import sys
from unittest.mock import patch, mock_open, MagicMock

# Добавляем путь к проекту в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Мокаем save_scenario
def mock_save_scenario(bot_id, scenario, user_id=None):
    print(f"Сохранение сценария для бота {bot_id}")
    print(f"Данные сценария: {scenario}")
    print(f"User ID: {user_id}")
    return True

# Мокаем UserManager
class MockUserManager:
    def get_bot_owner(self, bot_id):
        return "test_user_id"

# Тестируем эндпоинт save_scenario_endpoint
def test_save_scenario_endpoint():
    """Тест для проверки работы эндпоинта save_scenario_endpoint"""
    print("Тест: Проверка работы эндпоинта save_scenario_endpoint")
    
    # Мокаем save_scenario и UserManager
    with patch('main.save_scenario', side_effect=mock_save_scenario), \
         patch('main.UserManager', return_value=MockUserManager()):
        
        from main import Scenario, save_scenario_endpoint
        
        # Создаем тестовый сценарий с adminChatId
        scenario_data = {
            "nodes": [],
            "edges": [],
            "adminChatId": "987654321"
        }
        scenario = Scenario(**scenario_data)
        
        # Вызываем эндпоинт
        try:
            result = save_scenario_endpoint("test_bot", scenario, "test_user_id")
            print(f"Результат: {result}")
            
            # Проверяем, что результат успешный
            assert result["status"] == "success", "Статус должен быть success"
            
            print("✅ Тест пройден успешно")
            print()
        except Exception as e:
            print(f"❌ Тест не пройден: {e}")
            print()

if __name__ == "__main__":
    print("Запуск тестов для проверки эндпоинта save_scenario_endpoint...")
    print()
    
    test_save_scenario_endpoint()
    
    print("Тесты завершены!")
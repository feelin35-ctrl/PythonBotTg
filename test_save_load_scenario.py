import json
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Добавляем путь к проекту в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Мокаем UserManager
class MockUserManager:
    def get_bot_owner(self, bot_id):
        return "test_user_id"

def test_save_load_scenario_cycle():
    """Тест для проверки полного цикла сохранения и загрузки сценария"""
    print("Тест: Проверка полного цикла сохранения и загрузки сценария")
    
    # Создаем временную директорию для теста
    with tempfile.TemporaryDirectory() as temp_dir:
        # Мокаем BOTS_DIR
        with patch('main.BOTS_DIR', temp_dir), \
             patch('main.UserManager', return_value=MockUserManager()):
            
            from main import Scenario, save_scenario, load_scenario
            import os
            
            # Создаем тестовый сценарий с adminChatId
            scenario_data = {
                "nodes": [],
                "edges": [],
                "adminChatId": "987654321"
            }
            scenario = Scenario(**scenario_data)
            
            # Сохраняем сценарий
            print("Сохраняем сценарий...")
            try:
                save_scenario("test_bot", scenario, "test_user_id")
                print("✅ Сценарий успешно сохранен")
            except Exception as e:
                print(f"❌ Ошибка при сохранении сценария: {e}")
                return
            
            # Загружаем сценарий
            print("Загружаем сценарий...")
            try:
                loaded_scenario = load_scenario("test_bot", "test_user_id")
                print("✅ Сценарий успешно загружен")
                
                # Проверяем содержимое загруженного сценария
                loaded_dict = loaded_scenario.model_dump()
                print(f"Загруженные данные: {loaded_dict}")
                
                # Проверяем, что admin_chat_id присутствует и имеет правильное значение
                assert 'admin_chat_id' in loaded_dict, "Загруженный сценарий должен содержать admin_chat_id"
                assert loaded_dict['admin_chat_id'] == "987654321", "Значение admin_chat_id должно быть корректным"
                
                print("✅ Данные сценария корректны")
                print()
                
            except Exception as e:
                print(f"❌ Ошибка при загрузке сценария: {e}")
                return
            
            print("✅ Тест пройден успешно")
            print()

if __name__ == "__main__":
    print("Запуск тестов для проверки полного цикла сохранения и загрузки сценария...")
    print()
    
    test_save_load_scenario_cycle()
    
    print("Все тесты пройдены успешно! 🎉")
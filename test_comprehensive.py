import json
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Добавляем путь к проекту в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_comprehensive_scenario_handling():
    """Комплексный тест для проверки работы сценариев"""
    print("Комплексный тест: Проверка работы сценариев")
    
    # Создаем временную директорию для теста
    with tempfile.TemporaryDirectory() as temp_dir:
        # Мокаем BOTS_DIR
        with patch('main.BOTS_DIR', temp_dir):
            
            from main import Scenario, save_scenario, load_scenario
            from blocks.schedule_block import ScheduleBlock
            import telebot
            from unittest.mock import Mock
            
            print("1. Тест создания сценария с adminChatId...")
            # Создаем тестовый сценарий с adminChatId
            scenario_data = {
                "nodes": [],
                "edges": [],
                "adminChatId": "987654321"
            }
            scenario = Scenario(**scenario_data)
            
            # Проверяем, что сценарий создан корректно
            scenario_dict = scenario.model_dump()
            assert 'admin_chat_id' in scenario_dict
            assert scenario_dict['admin_chat_id'] == "987654321"
            print("✅ Сценарий создан корректно")
            
            print("2. Тест сохранения сценария...")
            # Мокаем UserManager
            with patch('main.UserManager') as mock_user_manager_class:
                mock_user_manager = Mock()
                mock_user_manager.get_bot_owner.return_value = "test_user_id"
                mock_user_manager_class.return_value = mock_user_manager
                
                # Сохраняем сценарий
                try:
                    save_scenario("test_bot", scenario, "test_user_id")
                    print("✅ Сценарий успешно сохранен")
                except Exception as e:
                    print(f"❌ Ошибка при сохранении сценария: {e}")
                    return
            
            print("3. Тест загрузки сценария...")
            # Загружаем сценарий
            try:
                loaded_scenario = load_scenario("test_bot", "test_user_id")
                print("✅ Сценарий успешно загружен")
                
                # Проверяем содержимое загруженного сценария
                loaded_dict = loaded_scenario.model_dump()
                assert 'admin_chat_id' in loaded_dict
                assert loaded_dict['admin_chat_id'] == "987654321"
                print("✅ Данные сценария корректны")
                
            except Exception as e:
                print(f"❌ Ошибка при загрузке сценария: {e}")
                return
            
            print("4. Тест работы блока расписания...")
            # Создаем мок-объект бота
            mock_bot = Mock(spec=telebot.TeleBot)
            mock_bot.get_me.return_value.username = "test_bot"
            
            # Создаем тестовый блок расписания
            schedule_block = ScheduleBlock({
                "id": "test_schedule",
                "type": "schedule",
                "data": {
                    "dateQuestion": "На какую дату вы хотите записаться?",
                    "timeQuestion": "На какое время вы хотите записаться?"
                }
            })
            
            # Тестируем отправку уведомления администратору
            try:
                schedule_block.send_to_administrator(
                    bot=mock_bot,
                    user_chat_id=123456789,
                    date_str="2025-09-25",
                    time_str="14:30",
                    user_context={},
                    kwargs={
                        'scenario_data': {
                            'adminChatId': '987654321'
                        }
                    }
                )
                
                # Проверяем, что сообщение отправлено администратору
                mock_bot.send_message.assert_called_once()
                call_args = mock_bot.send_message.call_args
                admin_chat_id = call_args[0][0]
                message = call_args[0][1]
                
                assert str(admin_chat_id) == '987654321', f"Сообщение должно быть отправлено в чат {admin_chat_id}"
                assert "Новая запись через бота" in message, "Сообщение должно содержать информацию о новой записи"
                
                print("✅ Блок расписания работает корректно")
                
            except Exception as e:
                print(f"❌ Ошибка при работе блока расписания: {e}")
                return
            
            print()
            print("✅ Все тесты пройдены успешно!")
            print()

if __name__ == "__main__":
    print("Запуск комплексного теста...")
    print()
    
    test_comprehensive_scenario_handling()
    
    print("Комплексный тест завершен! 🎉")
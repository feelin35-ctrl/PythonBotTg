import sys
import os

# Добавляем путь к блокам в sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'blocks'))

from blocks.schedule_block import ScheduleBlock
import telebot
from unittest.mock import Mock, patch

# Создаем мок-объект бота
mock_bot = Mock(spec=telebot.TeleBot)

# Создаем тестовый блок расписания
schedule_block = ScheduleBlock({
    "id": "test_schedule",
    "type": "schedule",
    "data": {
        "dateQuestion": "На какую дату вы хотите записаться?",
        "timeQuestion": "На какое время вы хотите записаться?"
    }
})

# Тест 1: Отправка уведомления администратору с admin_chat_id в snake_case
print("Тест 1: Отправка уведомления администратору с admin_chat_id в snake_case")
try:
    # Мокаем logger.warning
    with patch('blocks.schedule_block.logger') as mock_logger:
        schedule_block.send_to_administrator(
            bot=mock_bot,
            user_chat_id=123456789,
            date_str="2025-09-25",
            time_str="14:30",
            user_context={},
            kwargs={
                'scenario_data': {
                    'admin_chat_id': '987654321'
                }
            }
        )
        # Проверяем, что сообщение отправлено администратору
        mock_bot.send_message.assert_called_once()
        call_args = mock_bot.send_message.call_args
        admin_chat_id = call_args[0][0]  # Первый аргумент - chat_id
        message = call_args[0][1]  # Второй аргумент - текст сообщения
        
        print(f"Сообщение отправлено в чат: {admin_chat_id}")
        print(f"Текст сообщения: {message}")
        print("✅ Тест 1 пройден успешно")
except Exception as e:
    print(f"❌ Тест 1 не пройден: {e}")
print()

# Сброс моков
mock_bot.reset_mock()

# Тест 2: Отправка уведомления администратору с adminChatId в camelCase
print("Тест 2: Отправка уведомления администратору с adminChatId в camelCase")
try:
    # Мокаем logger.warning
    with patch('blocks.schedule_block.logger') as mock_logger:
        schedule_block.send_to_administrator(
            bot=mock_bot,
            user_chat_id=123456789,
            date_str="2025-09-25",
            time_str="14:30",
            user_context={},
            kwargs={
                'scenario_data': {
                    'adminChatId': '111222333'
                }
            }
        )
        # Проверяем, что сообщение отправлено администратору
        mock_bot.send_message.assert_called_once()
        call_args = mock_bot.send_message.call_args
        admin_chat_id = call_args[0][0]  # Первый аргумент - chat_id
        message = call_args[0][1]  # Второй аргумент - текст сообщения
        
        print(f"Сообщение отправлено в чат: {admin_chat_id}")
        print(f"Текст сообщения: {message}")
        print("✅ Тест 2 пройден успешно")
except Exception as e:
    print(f"❌ Тест 2 не пройден: {e}")
print()

# Сброс моков
mock_bot.reset_mock()

# Тест 3: Отправка уведомления администратору с обоими форматами (adminChatId должен иметь приоритет)
print("Тест 3: Отправка уведомления администратору с обоими форматами")
try:
    # Мокаем logger.warning
    with patch('blocks.schedule_block.logger') as mock_logger:
        schedule_block.send_to_administrator(
            bot=mock_bot,
            user_chat_id=123456789,
            date_str="2025-09-25",
            time_str="14:30",
            user_context={},
            kwargs={
                'scenario_data': {
                    'admin_chat_id': '987654321',
                    'adminChatId': '111222333'
                }
            }
        )
        # Проверяем, что сообщение отправлено администратору
        mock_bot.send_message.assert_called_once()
        call_args = mock_bot.send_message.call_args
        admin_chat_id = call_args[0][0]  # Первый аргумент - chat_id
        message = call_args[0][1]  # Второй аргумент - текст сообщения
        
        print(f"Сообщение отправлено в чат: {admin_chat_id}")
        print(f"Текст сообщения: {message}")
        # Проверяем, что приоритет имеет adminChatId
        if str(admin_chat_id) == '111222333':
            print("✅ Тест 3 пройден успешно (adminChatId имеет приоритет)")
        else:
            print("❌ Тест 3 не пройден (adminChatId должен иметь приоритет)")
except Exception as e:
    print(f"❌ Тест 3 не пройден: {e}")
print()

print("Все тесты блока расписания завершены!")
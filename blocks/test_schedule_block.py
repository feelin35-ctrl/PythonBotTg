import unittest
from unittest.mock import Mock, patch
from blocks.schedule_block import ScheduleBlock

class TestScheduleBlock(unittest.TestCase):
    
    def test_schedule_block_creation(self):
        """Тест создания блока расписания с корректными данными"""
        node_data = {
            "id": "test_schedule",
            "type": "schedule",
            "data": {
                "dateQuestion": "На какую дату вы хотите записаться?",
                "timeQuestion": "На какое время вы хотите записаться?",
                "minDate": "2023-06-01",
                "maxDate": "2023-07-31",
                "timeInterval": 30,
                "workStartTime": "09:00",
                "workEndTime": "18:00",
                "crmIntegration": True,
                "crmEndpoint": "https://api.crm.example.com/slots",
                "unavailableMessage": "Извините, это время уже занято. Пожалуйста, выберите другое.",
                "adminChatId": "123456789"
            }
        }
        
        block = ScheduleBlock(node_data)
        
        # Проверка типа блока
        self.assertEqual(block.get_block_type(), "schedule")
        
        # Проверка создания экземпляра
        self.assertIsInstance(block, ScheduleBlock)
    
    def test_schedule_block_with_minimal_data(self):
        """Тест создания блока расписания с минимальными данными"""
        node_data = {
            "id": "test_schedule",
            "type": "schedule",
            "data": {}
        }
        
        block = ScheduleBlock(node_data)
        
        # Проверка типа блока
        self.assertEqual(block.get_block_type(), "schedule")
        
        # Проверка создания экземпляра
        self.assertIsInstance(block, ScheduleBlock)
    
    @patch('blocks.schedule_block.logger')
    def test_execute_success(self, mock_logger):
        """Тест выполнения блока расписания (успешная отправка вопроса о дате)"""
        node_data = {
            "id": "test_schedule",
            "type": "schedule",
            "data": {
                "dateQuestion": "На какую дату вы хотите записаться?"
            }
        }
        
        block = ScheduleBlock(node_data)
        
        # Создаем моки для бота и chat_id
        mock_bot = Mock()
        chat_id = 12345
        
        # Выполняем блок
        result = block.execute(mock_bot, chat_id)
        
        # Проверяем, что send_message был вызван с правильными аргументами
        mock_bot.send_message.assert_called_once_with(
            chat_id, "На какую дату вы хотите записаться?"
        )
        
        # Проверяем, что функция возвращает None
        self.assertIsNone(result)
        
        # Проверяем логирование
        mock_logger.info.assert_not_called()
    
    @patch('blocks.schedule_block.logger')
    def test_process_date_response_success(self, mock_logger):
        """Тест обработки ответа с датой (успешная обработка)"""
        node_data = {
            "id": "test_schedule",
            "type": "schedule",
            "data": {
                "timeQuestion": "На какое время вы хотите записаться?"
            }
        }
        
        block = ScheduleBlock(node_data)
        
        # Создаем моки для бота и chat_id
        mock_bot = Mock()
        chat_id = 12345
        user_context = {}
        
        # Обрабатываем ответ с датой
        result = block.process_date_response(mock_bot, chat_id, "2023-06-15", user_context=user_context)
        
        # Проверяем, что send_message был вызван с вопросом о времени
        mock_bot.send_message.assert_called_once_with(
            chat_id, "На какое время вы хотите записаться?"
        )
        
        # Проверяем, что дата сохранена в контексте
        self.assertEqual(user_context.get('selected_date'), "2023-06-15")
        
        # Проверяем, что функция возвращает None
        self.assertIsNone(result)
    
    @patch('blocks.schedule_block.logger')
    def test_process_date_response_invalid_format(self, mock_logger):
        """Тест обработки ответа с датой (неправильный формат)"""
        node_data = {
            "id": "test_schedule",
            "type": "schedule",
            "data": {
                "dateQuestion": "На какую дату вы хотите записаться?"
            }
        }
        
        block = ScheduleBlock(node_data)
        
        # Создаем моки для бота и chat_id
        mock_bot = Mock()
        chat_id = 12345
        user_context = {}
        
        # Обрабатываем ответ с неправильной датой
        result = block.process_date_response(mock_bot, chat_id, "неправильная дата", user_context=user_context)
        
        # Проверяем, что send_message был вызван дважды: с ошибкой и с повторным вопросом
        self.assertEqual(mock_bot.send_message.call_count, 2)
        mock_bot.send_message.assert_any_call(
            chat_id, "Неверный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД"
        )
        mock_bot.send_message.assert_any_call(
            chat_id, "На какую дату вы хотите записаться?"
        )
        
        # Проверяем, что функция возвращает None
        self.assertIsNone(result)
    
    @patch('blocks.schedule_block.logger')
    def test_process_time_response_success(self, mock_logger):
        """Тест обработки ответа со временем (успешная обработка)"""
        node_data = {
            "id": "test_schedule",
            "type": "schedule",
            "data": {}
        }
        
        block = ScheduleBlock(node_data)
        
        # Создаем моки для бота и chat_id
        mock_bot = Mock()
        chat_id = 12345
        user_context = {'selected_date': '2023-06-15'}
        
        # Обрабатываем ответ со временем
        result = block.process_time_response(mock_bot, chat_id, "14:30", user_context=user_context)
        
        # Проверяем, что send_message был вызван дважды: с подтверждением и с информацией для администратора
        self.assertEqual(mock_bot.send_message.call_count, 2)
        mock_bot.send_message.assert_any_call(
            chat_id, "Вы записаны на 2023-06-15 в 14:30"
        )
        
        # Проверяем, что функция возвращает None
        self.assertIsNone(result)
    
    @patch('blocks.schedule_block.logger')
    def test_process_time_response_invalid_format(self, mock_logger):
        """Тест обработки ответа со временем (неправильный формат)"""
        node_data = {
            "id": "test_schedule",
            "type": "schedule",
            "data": {
                "timeQuestion": "На какое время вы хотите записаться?"
            }
        }
        
        block = ScheduleBlock(node_data)
        
        # Создаем моки для бота и chat_id
        mock_bot = Mock()
        chat_id = 12345
        user_context = {'schedule_config': {}}
        
        # Обрабатываем ответ с неправильным временем
        result = block.process_time_response(mock_bot, chat_id, "неправильное время", user_context=user_context)
        
        # Проверяем, что send_message был вызван дважды: с ошибкой и с повторным вопросом
        self.assertEqual(mock_bot.send_message.call_count, 2)
        mock_bot.send_message.assert_any_call(
            chat_id, "Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ"
        )
        mock_bot.send_message.assert_any_call(
            chat_id, "На какое время вы хотите записаться?"
        )
        
        # Проверяем, что функция возвращает None
        self.assertIsNone(result)
    
    @patch('blocks.schedule_block.logger')
    @patch('blocks.schedule_block.requests.get')
    def test_process_time_response_with_crm_available(self, mock_requests_get, mock_logger):
        """Тест обработки ответа со временем с интеграцией CRM (доступно)"""
        node_data = {
            "id": "test_schedule",
            "type": "schedule",
            "data": {
                "crmIntegration": True,
                "crmEndpoint": "https://api.crm.example.com/slots"
            }
        }
        
        block = ScheduleBlock(node_data)
        
        # Настраиваем мок для CRM (доступно)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"available": True}
        mock_requests_get.return_value = mock_response
        
        # Создаем моки для бота и chat_id
        mock_bot = Mock()
        chat_id = 12345
        user_context = {
            'selected_date': '2023-06-15',
            'schedule_config': {
                'crm_integration': True,
                'crm_endpoint': 'https://api.crm.example.com/slots'
            }
        }
        
        # Обрабатываем ответ со временем
        result = block.process_time_response(mock_bot, chat_id, "14:30", user_context=user_context)
        
        # Проверяем, что send_message был вызван дважды: с подтверждением и с информацией для администратора
        self.assertEqual(mock_bot.send_message.call_count, 2)
        mock_bot.send_message.assert_any_call(
            chat_id, "Вы записаны на 2023-06-15 в 14:30"
        )
        
        # Проверяем, что функция возвращает None
        self.assertIsNone(result)
    
    @patch('blocks.schedule_block.logger')
    @patch('blocks.schedule_block.requests.get')
    def test_process_time_response_with_crm_unavailable(self, mock_requests_get, mock_logger):
        """Тест обработки ответа со временем с интеграцией CRM (недоступно)"""
        node_data = {
            "id": "test_schedule",
            "type": "schedule",
            "data": {
                "timeQuestion": "На какое время вы хотите записаться?",
                "unavailableMessage": "Извините, это время уже занято. Пожалуйста, выберите другое.",
                "crmIntegration": True,
                "crmEndpoint": "https://api.crm.example.com/slots"
            }
        }
        
        block = ScheduleBlock(node_data)
        
        # Настраиваем мок для CRM (недоступно)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"available": False}
        mock_requests_get.return_value = mock_response
        
        # Создаем моки для бота и chat_id
        mock_bot = Mock()
        chat_id = 12345
        user_context = {
            'selected_date': '2023-06-15',
            'schedule_config': {
                'time_question': 'На какое время вы хотите записаться?',
                'crm_integration': True,
                'crm_endpoint': 'https://api.crm.example.com/slots',
                'unavailable_message': 'Извините, это время уже занято. Пожалуйста, выберите другое.'
            }
        }
        
        # Обрабатываем ответ со временем
        result = block.process_time_response(mock_bot, chat_id, "14:30", user_context=user_context)
        
        # Проверяем, что send_message был вызван дважды: с сообщением о недоступности и с повторным вопросом
        self.assertEqual(mock_bot.send_message.call_count, 2)
        mock_bot.send_message.assert_any_call(
            chat_id, "Извините, это время уже занято. Пожалуйста, выберите другое."
        )
        mock_bot.send_message.assert_any_call(
            chat_id, "На какое время вы хотите записаться?"
        )
        
        # Проверяем, что функция возвращает None
        self.assertIsNone(result)
    
    @patch('blocks.schedule_block.logger')
    def test_send_to_administrator_with_admin_chat_id(self, mock_logger):
        """Тест отправки информации администратору с указанным chat_id"""
        node_data = {
            "id": "test_schedule",
            "type": "schedule",
            "data": {
                "adminChatId": "987654321"
            }
        }
        
        block = ScheduleBlock(node_data)
        
        # Создаем моки для бота
        mock_bot = Mock()
        mock_bot.get_me.return_value.username = "test_bot"
        
        user_chat_id = 12345
        date_str = "2023-06-15"
        time_str = "14:30"
        user_context = {}
        
        # Вызываем метод отправки администратору
        block.send_to_administrator(mock_bot, user_chat_id, date_str, time_str, user_context, {})
        
        # Проверяем, что send_message был вызван с правильным chat_id администратора
        mock_bot.send_message.assert_called_once_with(
            "987654321",
            f"""
🔔 Новая запись через бота @test_bot

📅 Дата: {date_str}
⏰ Время: {time_str}
👤 Пользователь: tg://user?id={user_chat_id}
🔗 Ссылка на пользователя: tg://user?id={user_chat_id}

Пожалуйста, свяжитесь с пользователем для подтверждения записи.
            """.strip()
        )
    
    @patch('blocks.schedule_block.logger')
    def test_send_to_administrator_without_admin_chat_id(self, mock_logger):
        """Тест отправки информации администратору без указанного chat_id (отправка пользователю)"""
        node_data = {
            "id": "test_schedule",
            "type": "schedule",
            "data": {}
        }
        
        block = ScheduleBlock(node_data)
        
        # Создаем моки для бота
        mock_bot = Mock()
        mock_bot.get_me.return_value.username = "test_bot"
        
        user_chat_id = 12345
        date_str = "2023-06-15"
        time_str = "14:30"
        user_context = {}
        
        # Вызываем метод отправки администратору
        block.send_to_administrator(mock_bot, user_chat_id, date_str, time_str, user_context, {})
        
        # Проверяем, что send_message был вызван с chat_id пользователя (демо режим)
        mock_bot.send_message.assert_called_once_with(
            user_chat_id,
            f"""
🔔 Новая запись через бота @test_bot

📅 Дата: {date_str}
⏰ Время: {time_str}
👤 Пользователь: tg://user?id={user_chat_id}
🔗 Ссылка на пользователя: tg://user?id={user_chat_id}

Пожалуйста, свяжитесь с пользователем для подтверждения записи.
            """.strip()
        )

if __name__ == '__main__':
    unittest.main()
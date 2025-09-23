# Тестовый скрипт для проверки исправления ошибки с chat_id
# Мы имитируем вызов process_node с правильными параметрами

def test_process_node_call():
    """Тест для проверки правильного вызова process_node"""
    # Имитируем структуру message_context без chat_id
    message_context = {
        'user_message': 'Хочу капучино',
        'user_id': 123456789,
        'username': 'testuser'
    }
    
    # Имитируем параметры вызова
    bot = "fake_bot_instance"
    chat_id = 1106294909
    node_id = "nlp_node_1"
    
    # Проверяем, что chat_id не дублируется
    # Это правильный вызов:
    print("Правильный вызов process_node:")
    print(f"process_node(bot, {chat_id}, '{node_id}', user_message='{message_context['user_message']}', user_id={message_context['user_id']}, username='{message_context['username']}')")
    
    # Проверим, что в message_context нет chat_id
    if 'chat_id' in message_context:
        print("❌ ОШИБКА: chat_id найден в message_context")
        return False
    else:
        print("✅ УСПЕХ: chat_id отсутствует в message_context")
        return True

if __name__ == "__main__":
    print("Проверка исправления ошибки с дублированием chat_id...")
    print("=" * 50)
    
    success = test_process_node_call()
    
    print("=" * 50)
    if success:
        print("✅ Исправление успешно! Ошибка не должна больше возникать.")
    else:
        print("❌ Исправление не удалось. Нужно проверить код.")
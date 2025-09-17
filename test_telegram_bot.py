import requests
import sys


def test_telegram_bot():
    BASE_URL = "http://127.0.0.1:8001"
    BOT_ID = "test_bot"

    print("🧪 Тестирование Telegram бота")
    print("=" * 50)

    # 1. Получаем текущий токен
    print("1. Получаем токен бота...")
    try:
        response = requests.get(f"{BASE_URL}/get_token/{BOT_ID}/")
        token = response.json().get('token', '')
        print(f"   Токен: {token[:15]}...")
    except:
        print("   ❌ Токен не найден")
        return False

    # 2. Проверяем валидность токена
    print("2. Проверяем валидность токена...")
    if not token or ":" not in token:
        print("   ❌ Неверный формат токена")
        print("   ℹ️  Получите токен у @BotFather: /newbot")
        return False

    # 3. Проверяем доступность Telegram API
    print("3. Проверяем доступность Telegram API...")
    try:
        import telebot
        test_bot = telebot.TeleBot(token)
        bot_info = test_bot.get_me()
        print(f"   ✅ Бот доступен: {bot_info.first_name} (@{bot_info.username})")
    except Exception as e:
        print(f"   ❌ Ошибка доступа: {str(e)}")
        print("   ℹ️  Проверьте токен и интернет-соединение")
        return False

    # 4. Запускаем бота
    print("4. Запускаем бота...")
    try:
        response = requests.post(f"{BASE_URL}/run_bot/{BOT_ID}/", json={"token": token})
        result = response.json()
        print(f"   Результат: {result}")

        if result.get('status') == 'success':
            print("   ✅ Бот успешно запущен!")
            print("\n📋 Инструкция для тестирования:")
            print("1. Найдите бота в Telegram по username")
            print("2. Отправьте команду /start")
            print("3. Проверьте логи в консоли сервера")
            return True
        else:
            print(f"   ❌ Ошибка: {result.get('message')}")
            return False

    except Exception as e:
        print(f"   ❌ Ошибка запуска: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_telegram_bot()
    sys.exit(0 if success else 1)
import requests
import json
import os


def debug_token_system():
    BASE_URL = "http://127.0.0.1:8001"
    TEST_BOT = "debug_bot"
    TEST_TOKEN = "8495785437:AAFR_fwx0AlVTcVanFMwZ7Uf5Z4t3Sk-YdA"

    print("🔍 Диагностика системы токенов")
    print("=" * 50)

    # 1. Проверяем существование файла токенов
    tokens_file = "bot_tokens.json"
    print(f"1. Файл токенов: {tokens_file}")
    print(f"   Существует: {os.path.exists(tokens_file)}")

    if os.path.exists(tokens_file):
        with open(tokens_file, 'r') as f:
            tokens_data = json.load(f)
        print(f"   Содержимое: {tokens_data}")

    # 2. Создаем тестового бота
    print(f"\n2. Создаем бота {TEST_BOT}...")
    try:
        response = requests.post(f"{BASE_URL}/create_bot/?bot_id={TEST_BOT}")
        print(f"   Результат: {response.json()}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return

    # 3. Сохраняем токен
    print(f"\n3. Сохраняем токен для {TEST_BOT}...")
    try:
        token_data = {"token": TEST_TOKEN}
        response = requests.post(f"{BASE_URL}/save_token/{TEST_BOT}/", json=token_data)
        print(f"   Результат: {response.json()}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return

    # 4. Проверяем сохранение
    print(f"\n4. Проверяем сохранение токена...")
    try:
        response = requests.get(f"{BASE_URL}/get_token/{TEST_BOT}/")
        print(f"   Ответ сервера: {response.status_code}")
        print(f"   Данные: {response.json()}")

        token = response.json().get('token')
        if token == TEST_TOKEN:
            print("   ✅ Токен успешно сохранен и получен!")
        else:
            print("   ❌ Токен не совпадает!")

    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

    # 5. Проверяем файл на диске
    print(f"\n5. Проверяем файл токенов после сохранения...")
    if os.path.exists(tokens_file):
        with open(tokens_file, 'r') as f:
            tokens_data = json.load(f)
        print(f"   Токены в файле: {tokens_data}")

        if TEST_BOT in tokens_data:
            print(f"   ✅ Бот {TEST_BOT} найден в файле")
            print(f"   Токен: {tokens_data[TEST_BOT]}")
        else:
            print(f"   ❌ Бот {TEST_BOT} не найден в файле")

    print("\n" + "=" * 50)
    print("Диагностика завершена")


if __name__ == "__main__":
    debug_token_system()
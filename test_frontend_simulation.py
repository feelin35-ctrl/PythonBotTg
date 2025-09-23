import requests
import json

# Тестирование полного флоу создания бота через API
# Используем порт 8002 как в основном приложении

# 1. Логин
login_data = {
    "username": "Feelin",
    "password": "newpassword"
}

print("1. Выполняем вход...")
login_response = requests.post("http://localhost:8002/api/login/", json=login_data)
print(f"Статус входа: {login_response.status_code}")
print(f"Ответ: {login_response.json()}")

if login_response.status_code == 200:
    user_data = login_response.json()["user"]
    user_id = user_data["id"]
    print(f"Успешный вход. User ID: {user_id}")
    
    # 2. Создание бота
    print("\n2. Создаем бота...")
    bot_id = "test_bot_from_frontend"
    params = {
        "bot_id": bot_id,
        "user_id": user_id
    }
    
    create_response = requests.post("http://localhost:8002/api/create_bot/", params=params)
    print(f"Статус создания: {create_response.status_code}")
    print(f"Ответ: {create_response.json()}")
    
    # 3. Получение списка ботов
    print("\n3. Получаем список ботов...")
    bots_params = {"user_id": user_id}
    bots_response = requests.get("http://localhost:8002/api/get_bots/", params=bots_params)
    print(f"Статус получения: {bots_response.status_code}")
    print(f"Список ботов: {bots_response.json()}")
    
    print("\nТест завершен!")
else:
    print("Ошибка входа!")
import requests
import json

# Данные для входа
login_data = {
    "username": "testuser",
    "password": "testpassword"
}

# Отправляем запрос на вход
response = requests.post("http://localhost:8001/api/login/", json=login_data)

# Выводим ответ
print("Login status code:", response.status_code)
print("Login response:", response.json())
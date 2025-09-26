import requests
import json

# URL API для логина
url = "http://localhost:8001/api/login/"

# Данные для входа
payload = {
    "username": "testuser",
    "password": "testpass"
}

# Заголовки
headers = {
    "Content-Type": "application/json"
}

# Выполняем POST запрос
response = requests.post(url, data=json.dumps(payload), headers=headers)

# Выводим результат
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
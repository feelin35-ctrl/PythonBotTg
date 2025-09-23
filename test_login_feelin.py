import requests
import json

# Данные для входа с новым паролем
login_data = {
    "username": "Feelin",
    "password": "newpassword"
}

# Отправляем запрос на вход
response = requests.post("http://localhost:8001/api/login/", json=login_data)

# Выводим ответ
print("Login status code:", response.status_code)
print("Login response:", response.json())
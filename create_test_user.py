import requests
import json

# Данные для регистрации тестового пользователя
register_data = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "testpassword"
}

# Отправляем запрос на регистрацию
response = requests.post("http://localhost:8001/api/register/", json=register_data)

# Выводим ответ
print("Register status code:", response.status_code)
print("Register response:", response.json())

# Если регистрация успешна, пробуем войти
if response.status_code == 200:
    # Данные для входа
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    # Отправляем запрос на вход
    login_response = requests.post("http://localhost:8001/api/login/", json=login_data)
    
    # Выводим ответ
    print("\nLogin status code:", login_response.status_code)
    print("Login response:", login_response.json())
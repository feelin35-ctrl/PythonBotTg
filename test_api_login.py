import requests
import json

# Данные для входа
login_data = {
    "username": "Feelin",
    "password": "newpassword"
}

# Отправляем запрос на вход
try:
    response = requests.post("http://localhost:8001/api/login/", json=login_data)
    
    # Выводим ответ
    print("Status code:", response.status_code)
    print("Response headers:", response.headers)
    print("Response body:", response.text)
    
    # Пытаемся распарсить JSON
    try:
        json_response = response.json()
        print("JSON response:", json_response)
        
        if "user" in json_response:
            print("User data in response:", json_response["user"])
            if "id" in json_response["user"]:
                print("User ID in response:", json_response["user"]["id"])
            else:
                print("No ID in user data")
        else:
            print("No user data in response")
    except Exception as e:
        print("Error parsing JSON:", e)
        
except Exception as e:
    print("Error sending request:", e)
import requests
import logging

# Настройка логирования для отладки
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_proxy():
    print("Testing proxy connection to frontend server...")
    
    # URL фронтенд сервера с прокси
    frontend_url = "http://localhost:3000/api/login/"
    
    # Данные для входа
    login_data = {
        "username": "Feelin",
        "password": "newpassword"
    }
    
    print(f"Making request to: {frontend_url}")
    
    try:
        # Отправляем запрос через прокси фронтенда
        response = requests.post(
            frontend_url,
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: Proxy connection working correctly!")
        else:
            print(f"ERROR: Proxy returned status code {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request failed with exception: {e}")

if __name__ == "__main__":
    test_proxy()
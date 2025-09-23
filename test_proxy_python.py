import requests
import json

def test_proxy():
    # Тестируем прокси через фронтенд сервер
    print("Testing proxy through frontend server...")
    
    url = "http://localhost:3000/api/login/"
    data = {
        "username": "Feelin",
        "password": "newpassword"
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: Proxy connection working correctly!")
        else:
            print(f"ERROR: Proxy returned status code {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: Request failed with exception: {e}")

if __name__ == "__main__":
    test_proxy()
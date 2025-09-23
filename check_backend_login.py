import requests
import json

# Test the backend login endpoint directly
url = "http://localhost:8002/api/login/"
data = {
    "username": "superadmin",
    "password": "SuperAdmin123!"
}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
import requests
import json

# Test the get_bots endpoint directly
url = "http://localhost:8002/api/get_bots/"
params = {
    "user_id": "9"  # superadmin user ID
}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.get(url, params=params, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
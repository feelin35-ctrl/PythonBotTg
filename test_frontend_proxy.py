import requests
import json

# Test the frontend proxy by making a request to the frontend server
# which should proxy it to the backend
url = "http://localhost:3000/api/login/"
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
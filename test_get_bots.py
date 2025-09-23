import requests
import json

# First login to get user info
login_url = "http://localhost:8002/api/login/"
login_data = {
    "username": "superadmin",
    "password": "SuperAdmin123!"
}

headers = {
    "Content-Type": "application/json"
}

try:
    # Login
    login_response = requests.post(login_url, data=json.dumps(login_data), headers=headers)
    if login_response.status_code == 200:
        user_info = login_response.json()["user"]
        user_id = user_info["id"]
        print(f"Logged in user ID: {user_id}")
        
        # Get bots for this user
        bots_url = f"http://localhost:8002/api/get_bots/?user_id={user_id}"
        bots_response = requests.get(bots_url, headers=headers)
        print(f"Bots Status Code: {bots_response.status_code}")
        print(f"Bots Response: {bots_response.text}")
    else:
        print(f"Login failed with status code: {login_response.status_code}")
        print(f"Response: {login_response.text}")
except Exception as e:
    print(f"Error: {e}")
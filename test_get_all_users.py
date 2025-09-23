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
        
        # Get all users (super_admin only)
        users_url = f"http://localhost:8002/api/get_all_users/?user_id={user_id}"
        users_response = requests.get(users_url, headers=headers)
        print(f"Users Status Code: {users_response.status_code}")
        print(f"Users Response: {users_response.text}")
    else:
        print(f"Login failed with status code: {login_response.status_code}")
        print(f"Response: {login_response.text}")
except Exception as e:
    print(f"Error: {e}")
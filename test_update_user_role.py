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
        super_admin_id = user_info["id"]
        print(f"Logged in super admin ID: {super_admin_id}")
        
        # Let's try to update a regular user's role to super_admin
        # We'll use user ID 7 (Feelin35) and change their role to super_admin
        update_url = f"http://localhost:8002/api/update_user_role/"
        params = {
            "user_id": "7",  # Feelin35 user
            "new_role": "super_admin",
            "updated_by_user_id": super_admin_id
        }
        
        update_response = requests.post(update_url, params=params, headers=headers)
        print(f"Update Role Status Code: {update_response.status_code}")
        print(f"Update Role Response: {update_response.text}")
        
        # Verify the change by getting all users again
        users_url = f"http://localhost:8002/api/get_all_users/?user_id={super_admin_id}"
        users_response = requests.get(users_url, headers=headers)
        if users_response.status_code == 200:
            users_data = users_response.json()["users"]
            # Find user with ID 7
            for user in users_data:
                if user["id"] == "7":
                    print(f"User 7 role after update: {user['role']}")
                    break
    else:
        print(f"Login failed with status code: {login_response.status_code}")
        print(f"Response: {login_response.text}")
except Exception as e:
    print(f"Error: {e}")
import requests
import json

# Login as the newly promoted super admin (user ID 7)
login_url = "http://localhost:8002/api/login/"
login_data = {
    "username": "Feelin35",
    "password": "testpassword"  # Using test password
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
        user_role = user_info["role"]
        print(f"Logged in user ID: {user_id}, Role: {user_role}")
        
        # Get all users (should work now as super_admin)
        users_url = f"http://localhost:8002/api/get_all_users/?user_id={user_id}"
        users_response = requests.get(users_url, headers=headers)
        print(f"Users Status Code: {users_response.status_code}")
        if users_response.status_code == 200:
            print("✅ New super admin can access get_all_users endpoint")
            users_data = users_response.json()["users"]
            print(f"Total users visible: {len(users_data)}")
        else:
            print("❌ New super admin cannot access get_all_users endpoint")
            print(f"Response: {users_response.text}")
            
        # Get all bots (should work now as super_admin)
        bots_url = f"http://localhost:8002/api/get_bots/?user_id={user_id}"
        bots_response = requests.get(bots_url, headers=headers)
        print(f"Bots Status Code: {bots_response.status_code}")
        if bots_response.status_code == 200:
            print("✅ New super admin can access get_bots endpoint")
            bots_data = bots_response.json()["bots"]
            print(f"Total bots visible: {len(bots_data)}")
        else:
            print("❌ New super admin cannot access get_bots endpoint")
            print(f"Response: {bots_response.text}")
    else:
        print(f"Login failed with status code: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        # Try with admin password
        print("Trying with 'admin' password...")
        login_data["password"] = "admin"
        login_response = requests.post(login_url, data=json.dumps(login_data), headers=headers)
        if login_response.status_code == 200:
            print("Login successful with 'admin' password")
            user_info = login_response.json()["user"]
            user_id = user_info["id"]
            user_role = user_info["role"]
            print(f"Logged in user ID: {user_id}, Role: {user_role}")
        else:
            print(f"Login also failed with 'admin' password: {login_response.status_code}")
            print(f"Response: {login_response.text}")
except Exception as e:
    print(f"Error: {e}")
import requests
import json
import time

# First, let's login to get a valid user ID
login_data = {
    "username": "Feelin",
    "password": "newpassword"
}

print("Logging in...")
login_response = requests.post("http://localhost:8001/api/login/", json=login_data)
print("Login response:", login_response.json())

if login_response.status_code == 200 and login_response.json().get("status") == "success":
    user_id = login_response.json()["user"]["id"]
    print(f"User ID: {user_id}")
    
    # Now test creating a new bot with user ID
    # Generate a unique bot name with timestamp
    bot_id = f"test_bot_{int(time.time())}"
    
    # Test 1: Create bot with user ID as query parameter
    print(f"\nCreating bot {bot_id} with user_id {user_id}...")
    create_url = f"http://localhost:8001/api/create_bot/?bot_id={bot_id}&user_id={user_id}"
    print(f"URL: {create_url}")
    
    create_response = requests.post(create_url)
    print("Create bot response:", create_response.json())
    
    # Check if bot ownership was registered by checking the bot list
    print("\nChecking bot list for user...")
    bots_url = f"http://localhost:8001/api/get_bots/?user_id={user_id}"
    bots_response = requests.get(bots_url)
    print("Bots response:", bots_response.json())
    
    # Check if our new bot is in the list
    bots_list = bots_response.json().get("bots", [])
    print(f"Bots list: {bots_list}")
    
    # Since the bots list contains bot IDs as strings, we check if our bot_id is in the list
    bot_found = bot_id in bots_list
    print(f"Bot {bot_id} found in user's bot list: {bot_found}")
else:
    print("Login failed")
import requests
import json

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
    
    # Now test creating a bot with user ID
    bot_id = "test_bot_with_user"
    
    # Test 1: Create bot with user ID as query parameter
    print(f"\nCreating bot {bot_id} with user_id {user_id}...")
    create_url = f"http://localhost:8001/api/create_bot/?bot_id={bot_id}&user_id={user_id}"
    print(f"URL: {create_url}")
    
    create_response = requests.post(create_url)
    print("Create bot response:", create_response.json())
    
    # Check if bot ownership was registered
    print("\nChecking bot ownership...")
    try:
        import mysql.connector
        
        # Database connection (update with your actual database credentials)
        conn = mysql.connector.connect(
            host='localhost',
            user='pythonbot',
            password='newpassword',
            database='pythonbot_db'
        )
        
        cursor = conn.cursor()
        query = "SELECT user_id FROM bot_owners WHERE bot_id = %s"
        cursor.execute(query, (bot_id,))
        result = cursor.fetchone()
        
        if result:
            print(f"Bot ownership found: user_id = {result[0]}")
        else:
            print("No bot ownership record found")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error checking database: {e}")
else:
    print("Login failed")
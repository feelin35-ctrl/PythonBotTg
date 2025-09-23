import requests
import json

headers = {
    "Content-Type": "application/json"
}

try:
    # Define login URL
    login_url = "http://localhost:8002/api/login/"
    
    # First, let's create a new regular user
    print("Creating a new regular user...")
    register_url = "http://localhost:8002/api/register/"
    register_data = {
        "username": "new_test_user",
        "email": "new_test_user@example.com",
        "password": "new_test_password"
    }
    
    register_response = requests.post(register_url, data=json.dumps(register_data), headers=headers)
    print(f"Register Status Code: {register_response.status_code}")
    
    if register_response.status_code == 200:
        print("✅ New user registered successfully")
        
        # Login as the new regular user
        login_data = {
            "username": "new_test_user",
            "password": "new_test_password"
        }
        
        login_response = requests.post(login_url, data=json.dumps(login_data), headers=headers)
        if login_response.status_code == 200:
            user_info = login_response.json()["user"]
            user_id = user_info["id"]
            user_role = user_info["role"]
            print(f"Logged in as regular admin - ID: {user_id}, Role: {user_role}")
            
            # Create a bot for this user
            create_bot_url = "http://localhost:8002/api/create_bot/"
            params = {
                "bot_id": "test_bot_by_new_regular_user",
                "user_id": user_id
            }
            
            create_response = requests.post(create_bot_url, params=params, headers=headers)
            print(f"Create Bot Status Code: {create_response.status_code}")
            print(f"Create Bot Response: {create_response.text}")
            
            if create_response.status_code == 200:
                print("✅ Regular admin can create bot")
                
                # Check if the bot is visible to this user
                bots_url = f"http://localhost:8002/api/get_bots/?user_id={user_id}"
                bots_response = requests.get(bots_url, headers=headers)
                if bots_response.status_code == 200:
                    bots_data = bots_response.json()["bots"]
                    if "test_bot_by_new_regular_user" in bots_data:
                        print("✅ Bot is visible to regular admin who created it")
                    else:
                        print("❌ Bot is NOT visible to regular admin who created it")
                else:
                    print("❌ Failed to get bots for regular admin")
            else:
                print("❌ Regular admin cannot create bot")
        else:
            print("❌ Failed to login as new regular admin")
            print(f"Response: {login_response.text}")
    else:
        print("❌ Failed to register new user")
        print(f"Response: {register_response.text}")
        
    # Now test with super admin
    print("\n" + "="*50)
    print("Testing with Super Admin")
    print("="*50)
    
    # Login as super admin
    super_login_data = {
        "username": "superadmin",
        "password": "SuperAdmin123!"
    }
    
    super_login_response = requests.post(login_url, data=json.dumps(super_login_data), headers=headers)
    if super_login_response.status_code == 200:
        super_user_info = super_login_response.json()["user"]
        super_user_id = super_user_info["id"]
        super_user_role = super_user_info["role"]
        print(f"Logged in as super admin - ID: {super_user_id}, Role: {super_user_role}")
        
        # Create a bot for super admin
        create_bot_url = "http://localhost:8002/api/create_bot/"
        params = {
            "bot_id": "test_bot_by_super_admin",
            "user_id": super_user_id
        }
        
        create_response = requests.post(create_bot_url, params=params, headers=headers)
        print(f"Create Bot Status Code: {create_response.status_code}")
        print(f"Create Bot Response: {create_response.text}")
        
        if create_response.status_code == 200:
            print("✅ Super admin can create bot")
            
            # Check if the bot is visible to super admin
            bots_url = f"http://localhost:8002/api/get_bots/?user_id={super_user_id}"
            bots_response = requests.get(bots_url, headers=headers)
            if bots_response.status_code == 200:
                bots_data = bots_response.json()["bots"]
                if "test_bot_by_super_admin" in bots_data:
                    print("✅ Bot is visible to super admin who created it")
                else:
                    print("❌ Bot is NOT visible to super admin who created it")
            else:
                print("❌ Failed to get bots for super admin")
        else:
            print("❌ Super admin cannot create bot")
            
        # Check if super admin can see the new regular user's bot
        bots_url = f"http://localhost:8002/api/get_bots/?user_id={super_user_id}"
        bots_response = requests.get(bots_url, headers=headers)
        if bots_response.status_code == 200:
            bots_data = bots_response.json()["bots"]
            if "test_bot_by_new_regular_user" in bots_data:
                print("✅ Super admin can see regular user's bot")
            else:
                print("❌ Super admin cannot see regular user's bot")
        else:
            print("❌ Failed to get bots for super admin")
    else:
        print("❌ Failed to login as super admin")
        print(f"Response: {super_login_response.text}")
        
except Exception as e:
    print(f"Error: {e}")
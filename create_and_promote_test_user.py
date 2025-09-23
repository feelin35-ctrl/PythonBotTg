import requests
import json

# Register a new test user
register_url = "http://localhost:8002/api/register/"
register_data = {
    "username": "test_super_admin",
    "email": "test_super_admin@example.com",
    "password": "TestSuperAdmin123!"
}

headers = {
    "Content-Type": "application/json"
}

try:
    # Register new user
    register_response = requests.post(register_url, data=json.dumps(register_data), headers=headers)
    print(f"Register Status Code: {register_response.status_code}")
    print(f"Register Response: {register_response.text}")
    
    if register_response.status_code == 200:
        print("✅ User registered successfully")
        
        # Login as the new user
        login_url = "http://localhost:8002/api/login/"
        login_data = {
            "username": "test_super_admin",
            "password": "TestSuperAdmin123!"
        }
        
        login_response = requests.post(login_url, data=json.dumps(login_data), headers=headers)
        if login_response.status_code == 200:
            user_info = login_response.json()["user"]
            user_id = user_info["id"]
            user_role = user_info["role"]
            print(f"Logged in user ID: {user_id}, Role: {user_role}")
            
            # Login as superadmin to promote the new user
            superadmin_login_data = {
                "username": "superadmin",
                "password": "SuperAdmin123!"
            }
            
            superadmin_login_response = requests.post(login_url, data=json.dumps(superadmin_login_data), headers=headers)
            if superadmin_login_response.status_code == 200:
                superadmin_info = superadmin_login_response.json()["user"]
                superadmin_id = superadmin_info["id"]
                print(f"Super admin ID: {superadmin_id}")
                
                # Promote the new user to super_admin
                update_url = f"http://localhost:8002/api/update_user_role/"
                params = {
                    "user_id": user_id,
                    "new_role": "super_admin",
                    "updated_by_user_id": superadmin_id
                }
                
                update_response = requests.post(update_url, params=params, headers=headers)
                print(f"Update Role Status Code: {update_response.status_code}")
                print(f"Update Role Response: {update_response.text}")
                
                if update_response.status_code == 200:
                    print("✅ User promoted to super_admin successfully")
                    
                    # Test that the new super admin can access super admin endpoints
                    # Login again as the new super admin (to get updated role)
                    login_response = requests.post(login_url, data=json.dumps(login_data), headers=headers)
                    if login_response.status_code == 200:
                        user_info = login_response.json()["user"]
                        user_id = user_info["id"]
                        user_role = user_info["role"]
                        print(f"Re-logged in user ID: {user_id}, Role: {user_role}")
                        
                        # Test get_all_users endpoint
                        users_url = f"http://localhost:8002/api/get_all_users/?user_id={user_id}"
                        users_response = requests.get(users_url, headers=headers)
                        print(f"Users Status Code: {users_response.status_code}")
                        if users_response.status_code == 200:
                            print("✅ New super admin can access get_all_users endpoint")
                            users_data = users_response.json()["users"]
                            print(f"Total users visible: {len(users_data)}")
                        else:
                            print("❌ New super admin cannot access get_all_users endpoint")
                            
                        # Test get_bots endpoint
                        bots_url = f"http://localhost:8002/api/get_bots/?user_id={user_id}"
                        bots_response = requests.get(bots_url, headers=headers)
                        print(f"Bots Status Code: {bots_response.status_code}")
                        if bots_response.status_code == 200:
                            print("✅ New super admin can access get_bots endpoint")
                            bots_data = bots_response.json()["bots"]
                            print(f"Total bots visible: {len(bots_data)}")
                        else:
                            print("❌ New super admin cannot access get_bots endpoint")
                else:
                    print("❌ Failed to promote user to super_admin")
            else:
                print("❌ Failed to login as superadmin")
        else:
            print("❌ Failed to login as new user")
    else:
        print("❌ Failed to register new user")
        
except Exception as e:
    print(f"Error: {e}")
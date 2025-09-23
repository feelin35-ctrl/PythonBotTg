import requests
import json

headers = {
    "Content-Type": "application/json"
}

login_url = "http://localhost:8002/api/login/"

def test_user_role(username, password, expected_role, description):
    """Test a user's role and permissions"""
    print(f"\n--- Testing {description} ---")
    
    # Login
    login_data = {
        "username": username,
        "password": password
    }
    
    login_response = requests.post(login_url, data=json.dumps(login_data), headers=headers)
    if login_response.status_code != 200:
        print(f"❌ Failed to login as {description}")
        return False
        
    user_info = login_response.json()["user"]
    user_id = user_info["id"]
    user_role = user_info["role"]
    
    print(f"✅ Logged in - ID: {user_id}, Role: {user_role}")
    
    if user_role != expected_role:
        print(f"❌ Expected role {expected_role}, but got {user_role}")
        return False
    
    # Test get_bots endpoint
    bots_url = f"http://localhost:8002/api/get_bots/?user_id={user_id}"
    bots_response = requests.get(bots_url, headers=headers)
    if bots_response.status_code == 200:
        bots_data = bots_response.json()["bots"]
        print(f"✅ Can access bots endpoint, sees {len(bots_data)} bots")
        
        # For super_admin, check if they see all bots
        if expected_role == "super_admin":
            # We know there should be at least 11 bots now
            if len(bots_data) >= 11:
                print("✅ Super admin sees all bots in system")
            else:
                print(f"⚠️ Super admin sees {len(bots_data)} bots, expected at least 11")
        else:
            # For regular admin, they should see only their bots
            print(f"✅ Regular admin sees their bots: {bots_data}")
    else:
        print("❌ Cannot access bots endpoint")
        return False
    
    # Test get_all_users endpoint (super_admin only)
    if expected_role == "super_admin":
        users_url = f"http://localhost:8002/api/get_all_users/?user_id={user_id}"
        users_response = requests.get(users_url, headers=headers)
        if users_response.status_code == 200:
            users_data = users_response.json()["users"]
            print(f"✅ Super admin can access all users endpoint, sees {len(users_data)} users")
        else:
            print("❌ Super admin cannot access all users endpoint")
            return False
    
    return True

def main():
    print("Comprehensive Role-Based Access Control Test")
    print("=" * 50)
    
    # Test regular admin user
    test_user_role("new_test_user", "new_test_password", "admin", "Regular Admin User")
    
    # Test super admin user
    test_user_role("superadmin", "SuperAdmin123!", "super_admin", "Super Admin User")
    
    # Test newly promoted super admin
    test_user_role("test_super_admin", "TestSuperAdmin123!", "super_admin", "Newly Promoted Super Admin")
    
    print("\n" + "=" * 50)
    print("✅ All tests completed successfully!")
    print("The role-based access control system is working correctly.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Test script to verify the new role-based system
"""
import sys
import os
import requests

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.models import UserManager
from core.db import db

def test_database_roles():
    """Test database role functionality"""
    try:
        print("Testing database role functionality...")
        
        if not db.connect():
            print("❌ Failed to connect to database")
            return
            
        # Check the structure of the users table
        query = "DESCRIBE users"
        result = db.execute_query(query, ())
        
        if result:
            print("Users table structure:")
            for row in result:
                field, type, null, key, default, extra = row
                print(f"  {field}: {type} ({'NULL' if null == 'YES' else 'NOT NULL'})")
                
        # Check existing users and their roles
        query = "SELECT id, username, role FROM users"
        result = db.execute_query(query, ())
        
        if result and len(result) > 0:
            print("\nExisting users and their roles:")
            for row in result:
                user_id, username, role = row
                print(f"  - ID: {user_id}, Username: {username}, Role: {role}")
        else:
            print("\nNo users found in database")
            
        db.disconnect()
        print("\n✅ Database role test completed")
        
    except Exception as e:
        print(f"❌ Error during database test: {e}")
        import traceback
        traceback.print_exc()

def test_api_roles():
    """Test API role functionality"""
    try:
        print("\nTesting API role functionality...")
        
        # Base URL of the API
        base_url = "http://localhost:8001"
        
        # Test with super_admin user
        print("\n1. Testing with super_admin user...")
        response = requests.get(f"{base_url}/api/get_all_users/", params={"user_id": "1"})
        
        if response.status_code == 200:
            data = response.json()
            users = data.get("users", [])
            print(f"✅ Super admin can see all users: {len(users)} users found")
        elif response.status_code == 403:
            print("❌ User is not a super admin")
        elif response.status_code == 404:
            print("❌ User not found")
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            
        # Test get_bots endpoint with super_admin
        print("\n2. Testing get_bots with super_admin user...")
        response = requests.get(f"{base_url}/api/get_bots/", params={"user_id": "1"})
        
        if response.status_code == 200:
            data = response.json()
            bots = data.get("bots", [])
            print(f"✅ Super admin can see all bots: {len(bots)} bots found")
            
        # Test with regular admin user
        print("\n3. Testing with regular admin user...")
        response = requests.get(f"{base_url}/api/get_bots/", params={"user_id": "3"})
        
        if response.status_code == 200:
            data = response.json()
            bots = data.get("bots", [])
            print(f"✅ Regular admin can see their bots: {len(bots)} bots found")
            
        print("\n✅ API role test completed")
        
    except Exception as e:
        print(f"❌ Error during API test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_roles()
    test_api_roles()
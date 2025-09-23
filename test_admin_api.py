#!/usr/bin/env python3
"""
Test script to verify super admin API functionality
"""
import sys
import os
import requests
import json

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_admin_api():
    """Test admin API functionality"""
    try:
        # Base URL of the API
        base_url = "http://localhost:8001"
        
        # Test getting bots as admin user
        print("Testing API with admin user...")
        
        # Admin user ID (from our previous test)
        admin_user_id = "1"
        
        # Make request to get bots endpoint with admin user
        response = requests.get(f"{base_url}/api/get_bots/", params={"user_id": admin_user_id})
        
        if response.status_code == 200:
            data = response.json() if response.content else {}
            bots = data.get("bots", [])
            print(f"✅ Admin user can see all bots: {len(bots)} bots found")
            print(f"Bots: {bots}")
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return
            
        # Test with a regular user (if we have one)
        print("\nTesting API with regular user...")
        regular_user_id = "3"  # From our previous test
        
        response = requests.get(f"{base_url}/api/get_bots/", params={"user_id": regular_user_id})
        
        if response.status_code == 200:
            data = response.json() if response.content else {}
            bots = data.get("bots", [])
            print(f"✅ Regular user can see their bots: {len(bots)} bots found")
            print(f"Bots: {bots}")
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
        # Test with invalid user
        print("\nTesting API with invalid user...")
        response = requests.get(f"{base_url}/api/get_bots/", params={"user_id": "99999"})
        
        if response.status_code == 200:
            data = response.json() if response.content else {}
            bots = data.get("bots", [])
            print(f"✅ Invalid user gets empty list: {len(bots)} bots found")
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            
        # Test without user_id
        print("\nTesting API without user_id...")
        response = requests.get(f"{base_url}/api/get_bots/")
        
        if response.status_code == 200:
            data = response.json() if response.content else {}
            bots = data.get("bots", [])
            print(f"✅ Request without user_id returns empty list: {len(bots)} bots found")
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            
        print("\n✅ All API tests completed successfully")
        
    except Exception as e:
        print(f"❌ Error during API test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_admin_api()
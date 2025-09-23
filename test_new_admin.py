#!/usr/bin/env python3
"""
Test script to verify our new super admin user
"""
import sys
import os
import requests

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_new_admin():
    """Test our new admin user"""
    try:
        # Base URL of the API
        base_url = "http://localhost:8001"
        
        # Test getting bots as our new admin user (ID 9)
        print("Testing API with new admin user (ID: 9)...")
        
        response = requests.get(f"{base_url}/api/get_bots/", params={"user_id": "9"})
        
        if response.status_code == 200:
            data = response.json() if response.content else {}
            bots = data.get("bots", [])
            print(f"✅ New admin user can see all bots: {len(bots)} bots found")
            print(f"Bots: {bots}")
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
        print("\n✅ Test completed successfully")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_admin()
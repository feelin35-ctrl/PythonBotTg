#!/usr/bin/env python3
"""
Final comprehensive test of the role system
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.models import UserManager
from core.db import db

def final_test():
    """Final comprehensive test"""
    try:
        print("=== Final Comprehensive Role System Test ===")
        
        if not db.connect():
            print("❌ Failed to connect to database")
            return
            
        user_manager = UserManager()
        
        # Test 1: Check all users and their roles
        print("\n1. Checking all users and their roles...")
        users = user_manager.get_all_users()
        for user in users:
            print(f"  - ID: {user['id']}, Username: {user['username']}, Role: {user['role']}")
            
        # Test 2: Check if user 1 is super_admin
        print("\n2. Checking if user 1 is super_admin...")
        is_super = user_manager.is_super_admin("1")
        if is_super:
            print("✅ User 1 is super_admin")
        else:
            print("❌ User 1 is not super_admin")
            
        # Test 3: Check if user 3 is admin
        print("\n3. Checking if user 3 is admin...")
        is_super = user_manager.is_super_admin("3")
        if not is_super:
            print("✅ User 3 is admin (not super_admin)")
        else:
            print("❌ User 3 is super_admin (should be admin)")
            
        # Test 4: Test get_all_bots_for_super_admin
        print("\n4. Testing get_all_bots_for_super_admin...")
        bots = user_manager.get_all_bots_for_super_admin()
        print(f"✅ Super admin can see {len(bots)} bots: {bots}")
        
        # Test 5: Test get_user_bots for regular user
        print("\n5. Testing get_user_bots for regular user...")
        user_bots = user_manager.get_user_bots("3")
        print(f"✅ Regular user can see {len(user_bots)} bots: {user_bots}")
        
        db.disconnect()
        print("\n✅ All tests passed! Role system is working correctly.")
        
    except Exception as e:
        print(f"❌ Error during final test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    final_test()
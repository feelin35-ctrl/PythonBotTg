#!/usr/bin/env python3
"""
Test script to verify role update functionality
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.models import UserManager
from core.db import db

def test_role_update():
    """Test role update functionality"""
    try:
        print("Testing role update functionality...")
        
        if not db.connect():
            print("❌ Failed to connect to database")
            return
            
        # Create UserManager instance
        user_manager = UserManager()
        
        # Test updating user role (user ID 3 to super_admin by super_admin user ID 1)
        print("\n1. Testing role update: making user 3 a super_admin...")
        success = user_manager.update_user_role("3", "super_admin", "1")
        
        if success:
            print("✅ Role update successful")
            
            # Verify the update
            query = "SELECT role FROM users WHERE id = 3"
            result = db.execute_query(query, ())
            if result and len(result) > 0:
                role = result[0][0]
                print(f"✅ User 3 now has role: {role}")
            else:
                print("❌ Failed to verify role update")
        else:
            print("❌ Role update failed")
            
        # Test updating user role back to admin
        print("\n2. Testing role update: making user 3 an admin again...")
        success = user_manager.update_user_role("3", "admin", "1")
        
        if success:
            print("✅ Role update successful")
            
            # Verify the update
            query = "SELECT role FROM users WHERE id = 3"
            result = db.execute_query(query, ())
            if result and len(result) > 0:
                role = result[0][0]
                print(f"✅ User 3 now has role: {role}")
            else:
                print("❌ Failed to verify role update")
        else:
            print("❌ Role update failed")
            
        # Test unauthorized role update (user 3 trying to make user 1 admin)
        print("\n3. Testing unauthorized role update...")
        success = user_manager.update_user_role("1", "admin", "3")
        
        if not success:
            print("✅ Unauthorized role update correctly rejected")
        else:
            print("❌ Unauthorized role update was incorrectly allowed")
            
        # Test that super_admin can make another user super_admin
        print("\n4. Testing super_admin making another user super_admin...")
        success = user_manager.update_user_role("3", "super_admin", "1")
        
        if success:
            print("✅ Role update successful")
        else:
            print("❌ Role update failed")
            
        # Reset user 3 back to admin
        user_manager.update_user_role("3", "admin", "1")
            
        db.disconnect()
        print("\n✅ Role update test completed")
        
    except Exception as e:
        print(f"❌ Error during role update test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_role_update()
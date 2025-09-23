#!/usr/bin/env python3
"""
Script to check users and their authentication
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.db import db
from core.models import UserManager

def check_users_auth():
    """Check users and their authentication"""
    try:
        print("Checking users and their authentication...")
        
        if not db.connect():
            print("❌ Failed to connect to database")
            return
            
        # Get all users
        query = "SELECT id, username, email, role FROM users"
        result = db.execute_query(query, ())
        
        if result and len(result) > 0:
            print("Users in the system:")
            for row in result:
                user_id, username, email, role = row
                print(f"  - ID: {user_id}, Username: {username}, Email: {email}, Role: {role}")
        else:
            print("No users found")
            
        db.disconnect()
        
        # Test authentication for super admins
        print("\nTesting authentication for super admin users...")
        user_manager = UserManager()
        
        # Test with default admin user
        print("\n1. Testing default admin user (username: admin)")
        user = user_manager.authenticate_user("admin", "admin")  # Default password might be 'admin'
        if user:
            print("✅ Authentication successful")
            print(f"   User ID: {user.id}, Username: {user.username}, Role: {user.role}")
        else:
            print("❌ Authentication failed with password 'admin'")
            
        # Test with superadmin user
        print("\n2. Testing superadmin user (username: superadmin)")
        user = user_manager.authenticate_user("superadmin", "SuperAdmin123!")  # Password from our demo script
        if user:
            print("✅ Authentication successful")
            print(f"   User ID: {user.id}, Username: {user.username}, Role: {user.role}")
        else:
            print("❌ Authentication failed with password 'SuperAdmin123!'")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def reset_user_password(username, new_password):
    """Reset user password"""
    try:
        print(f"Resetting password for user '{username}'...")
        
        if not db.connect():
            print("❌ Failed to connect to database")
            return False
            
        from core.models import UserManager
        user_manager = UserManager()
        
        # Hash the new password
        hashed_password = user_manager.hash_password(new_password)
        
        # Update the user's password
        query = "UPDATE users SET password_hash = %s WHERE username = %s"
        result = db.execute_update(query, (hashed_password, username))
        
        if result is not None and result > 0:
            print(f"✅ Password for user '{username}' has been reset successfully")
            db.disconnect()
            return True
        else:
            print(f"❌ Failed to reset password for user '{username}'")
            db.disconnect()
            return False
            
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "reset":
        # Reset password for a user
        username = sys.argv[2]
        new_password = sys.argv[3] if len(sys.argv) > 3 else "admin"
        reset_user_password(username, new_password)
    else:
        # Check users and authentication
        check_users_auth()
        
        print("\n" + "="*50)
        print("If authentication is failing, you can reset a user's password:")
        print("Usage: python check_users_auth.py reset <username> [new_password]")
        print("Example: python check_users_auth.py reset admin mynewpassword")
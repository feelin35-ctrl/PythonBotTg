#!/usr/bin/env python3
"""
Script to create a super admin user
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.models import UserManager

def create_admin_user(username, email, password):
    """Create a super admin user"""
    try:
        user_manager = UserManager()
        
        # Register user with admin privileges (super_admin role)
        success = user_manager.register_user(username, email, password, role="super_admin")
        
        if success:
            print(f"✅ Super admin user '{username}' created successfully")
            print(f"Email: {email}")
            print("This user can now see all bots in the system")
            return True
        else:
            print(f"❌ Failed to create super admin user '{username}'")
            print("User may already exist")
            return False
            
    except Exception as e:
        print(f"❌ Error creating super admin user: {e}")
        import traceback
        traceback.print_exc()
        return False

def list_admin_users():
    """List all admin users"""
    try:
        from core.db import db
        
        if not db.connect():
            print("❌ Failed to connect to database")
            return
            
        query = "SELECT id, username, email, role FROM users WHERE role = 'super_admin'"
        result = db.execute_query(query, ())
        
        if result and len(result) > 0:
            print("Current super admin users:")
            for row in result:
                user_id, username, email, role = row
                print(f"  - ID: {user_id}, Username: {username}, Email: {email}, Role: {role}")
        else:
            print("No super admin users found")
            
        db.disconnect()
        
    except Exception as e:
        print(f"❌ Error listing admin users: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_admin_users()
    else:
        print("Create Super Admin User")
        print("=" * 30)
        print("Usage: python create_admin_user.py [list]")
        print("  - Without arguments: Create a new admin user")
        print("  - With 'list' argument: List all admin users")
        print()
        
        if len(sys.argv) > 1:
            print("Invalid argument. Use 'list' to list admin users or no arguments to create one.")
            sys.exit(1)
            
        username = input("Enter username: ").strip()
        email = input("Enter email: ").strip()
        password = input("Enter password: ").strip()
        
        if username and email and password:
            create_admin_user(username, email, password)
        else:
            print("❌ All fields are required")
#!/usr/bin/env python3
"""
Script to register a new user with admin role (default)
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.models import UserManager

def register_user(username, email, password):
    """Register a new user with admin role (default)"""
    try:
        user_manager = UserManager()
        
        # Register user with admin role (default)
        success = user_manager.register_user(username, email, password, role="admin")
        
        if success:
            print(f"✅ User '{username}' registered successfully with admin role")
            print(f"Email: {email}")
            print("This user can create bots and see only their own bots")
            return True
        else:
            print(f"❌ Failed to register user '{username}'")
            print("User may already exist")
            return False
            
    except Exception as e:
        print(f"❌ Error registering user: {e}")
        import traceback
        traceback.print_exc()
        return False

def list_all_users():
    """List all users"""
    try:
        from core.db import db
        
        if not db.connect():
            print("❌ Failed to connect to database")
            return
            
        query = "SELECT id, username, email, role FROM users"
        result = db.execute_query(query, ())
        
        if result and len(result) > 0:
            print("All users:")
            for row in result:
                user_id, username, email, role = row
                print(f"  - ID: {user_id}, Username: {username}, Email: {email}, Role: {role}")
        else:
            print("No users found")
            
        db.disconnect()
        
    except Exception as e:
        print(f"❌ Error listing users: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_all_users()
    else:
        print("Register New User")
        print("=" * 30)
        print("Usage: python register_user.py [list]")
        print("  - Without arguments: Register a new user")
        print("  - With 'list' argument: List all users")
        print()
        
        if len(sys.argv) > 1:
            print("Invalid argument. Use 'list' to list users or no arguments to register a new user.")
            sys.exit(1)
            
        username = input("Enter username: ").strip()
        email = input("Enter email: ").strip()
        password = input("Enter password: ").strip()
        
        if username and email and password:
            register_user(username, email, password)
        else:
            print("❌ All fields are required")
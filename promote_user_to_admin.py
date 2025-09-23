#!/usr/bin/env python3
"""
Script to promote an existing user to super admin
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.db import db

def list_users():
    """List all users"""
    try:
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

def promote_user(user_id):
    """Promote a user to super admin"""
    try:
        if not db.connect():
            print("❌ Failed to connect to database")
            return False
            
        # Check if user exists
        query = "SELECT id, username FROM users WHERE id = %s"
        result = db.execute_query(query, (user_id,))
        
        if not result or len(result) == 0:
            print(f"❌ User with ID {user_id} not found")
            db.disconnect()
            return False
            
        username = result[0][1]
        print(f"Found user: {username}")
        
        # Promote user to super admin
        update_query = "UPDATE users SET role = 'super_admin' WHERE id = %s"
        result = db.execute_update(update_query, (user_id,))
        
        if result is not None and result > 0:
            print(f"✅ User '{username}' (ID: {user_id}) successfully promoted to super admin")
            db.disconnect()
            return True
        else:
            print(f"❌ Failed to promote user '{username}' to super admin")
            db.disconnect()
            return False
            
    except Exception as e:
        print(f"❌ Error promoting user: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            list_users()
        else:
            try:
                user_id = int(sys.argv[1])
                promote_user(user_id)
            except ValueError:
                print("❌ Invalid user ID. Please provide a numeric user ID.")
    else:
        print("Promote User to Super Admin")
        print("=" * 30)
        print("Usage: python promote_user_to_admin.py [user_id|list]")
        print("  - With user_id: Promote the specified user to super admin")
        print("  - With 'list': List all users")
        print()
        print("First, run 'python promote_user_to_admin.py list' to see all users")
        print("Then, run 'python promote_user_to_admin.py [user_id]' to promote a user")
#!/usr/bin/env python3
"""
Script to make a user super admin
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.db import db

def make_super_admin(user_id):
    """Make a user super admin"""
    try:
        print(f"Making user {user_id} a super admin...")
        
        if not db.connect():
            print("❌ Failed to connect to database")
            return False
            
        # Update the user's role
        update_query = "UPDATE users SET role = 'super_admin' WHERE id = %s"
        result = db.execute_update(update_query, (user_id,))
        
        if result is not None and result > 0:
            print(f"✅ User {user_id} is now a super admin")
            db.disconnect()
            return True
        else:
            print(f"❌ Failed to update user {user_id}")
            db.disconnect()
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_super_admin.py <user_id>")
        sys.exit(1)
        
    try:
        user_id = sys.argv[1]
        make_super_admin(user_id)
    except Exception as e:
        print(f"❌ Error: {e}")
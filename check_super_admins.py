#!/usr/bin/env python3
"""
Script to check super admin users
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.db import db

def check_super_admins():
    """Check super admin users"""
    try:
        print("Checking super admin users...")
        
        if not db.connect():
            print("❌ Failed to connect to database")
            return
            
        # Get all super admin users
        query = "SELECT id, username, email, role FROM users WHERE role = 'super_admin'"
        result = db.execute_query(query, ())
        
        if result and len(result) > 0:
            print("Super admin users found:")
            for row in result:
                user_id, username, email, role = row
                print(f"  - ID: {user_id}, Username: {username}, Email: {email}, Role: {role}")
        else:
            print("No super admin users found")
            
        db.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_super_admins()
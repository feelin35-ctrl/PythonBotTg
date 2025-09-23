#!/usr/bin/env python3
"""
Test script to verify super admin functionality
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.models import UserManager
from core.db import db

def test_super_admin():
    """Test super admin functionality"""
    try:
        # Connect to database
        if not db.connect():
            print("❌ Failed to connect to database")
            return
        
        print("✅ Connected to database")
        
        # Check if we have any admin users
        query = "SELECT id, username, email, role FROM users WHERE role = 'super_admin'"
        result = db.execute_query(query, ())
        
        if result and len(result) > 0:
            print(f"✅ Found {len(result)} super admin users:")
            for row in result:
                user_id, username, email, role = row
                print(f"  - ID: {user_id}, Username: {username}, Email: {email}, Role: {role}")
        else:
            print("ℹ️  No super admin users found in the database")
            
        # Check all bots in the system
        query = "SELECT bot_id, user_id FROM bot_owners"
        result = db.execute_query(query, ())
        
        if result and len(result) > 0:
            print(f"\n✅ Found {len(result)} bots in the system:")
            for row in result:
                bot_id, user_id = row
                print(f"  - Bot ID: {bot_id}, Owner ID: {user_id}")
        else:
            print("\nℹ️  No bots found in the system")
            
        db.disconnect()
        print("\n✅ Test completed successfully")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_super_admin()
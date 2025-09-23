#!/usr/bin/env python3
"""
Demo script to create a super admin user programmatically
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.models import UserManager

def main():
    """Main function to create a super admin user"""
    print("Creating Super Admin User Demo")
    print("=" * 40)
    
    # Define admin user details
    username = "superadmin"
    email = "superadmin@example.com"
    password = "SuperAdmin123!"
    
    try:
        # Create UserManager instance
        user_manager = UserManager()
        
        # Register user with super admin privileges
        print(f"Creating super admin user: {username}")
        success = user_manager.register_user(username, email, password, role="super_admin")
        
        if success:
            print("✅ Super admin user created successfully!")
            print(f"Username: {username}")
            print(f"Email: {email}")
            print("This user can see all bots in the system")
            
            # Verify the user was created as super admin
            from core.db import db
            if db.connect():
                query = "SELECT id, username, role FROM users WHERE username = %s"
                result = db.execute_query(query, (username,))
                
                if result and len(result) > 0:
                    user_id, username, role = result[0]
                    print(f"Verification - User ID: {user_id}, Username: {username}, Role: {role}")
                db.disconnect()
        else:
            print("❌ Failed to create super admin user")
            print("User may already exist")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
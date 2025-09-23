#!/usr/bin/env python3
"""
Script to migrate database schema for roles system
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.db import db

def migrate_database():
    """Migrate database schema to support roles"""
    try:
        print("Migrating database schema for roles system...")
        
        if not db.connect():
            print("❌ Failed to connect to database")
            return False
            
        # Check if the 'role' column already exists
        describe_result = db.execute_query("DESCRIBE users", ())
        has_role_column = any(row[0] == 'role' for row in describe_result)
        has_is_admin_column = any(row[0] == 'is_admin' for row in describe_result)
        
        if has_role_column:
            print("✅ Role column already exists")
        else:
            # Add the 'role' column
            print("Adding 'role' column to users table...")
            alter_query = """
            ALTER TABLE users 
            ADD COLUMN role ENUM('super_admin', 'admin') DEFAULT 'admin'
            """
            result = db.execute_update(alter_query, ())
            if result is not None:
                print("✅ Role column added successfully")
            else:
                print("❌ Failed to add role column")
                return False
                
        # If we have is_admin column, migrate data and then drop the column
        if has_is_admin_column:
            print("Migrating data from is_admin to role...")
            # Update existing users: is_admin=1 becomes role='super_admin', is_admin=0 becomes role='admin'
            update_query = """
            UPDATE users 
            SET role = CASE 
                WHEN is_admin = 1 THEN 'super_admin' 
                ELSE 'admin' 
            END
            """
            result = db.execute_update(update_query, ())
            if result is not None:
                print(f"✅ Data migrated for {result} users")
                
                # Drop the old is_admin column
                print("Dropping old is_admin column...")
                drop_query = "ALTER TABLE users DROP COLUMN is_admin"
                result = db.execute_update(drop_query, ())
                if result is not None:
                    print("✅ is_admin column dropped successfully")
                else:
                    print("❌ Failed to drop is_admin column")
            else:
                print("❌ Failed to migrate data")
                
        db.disconnect()
        print("\n✅ Database migration completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error during database migration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    migrate_database()
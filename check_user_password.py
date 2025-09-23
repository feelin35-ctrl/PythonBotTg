import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'tg_bots'),
    'port': int(os.getenv('DB_PORT', 3306))
}

try:
    # Connect to database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Check all users with their roles
    cursor.execute("SELECT id, username, password_hash, role, created_at FROM users ORDER BY created_at")
    users = cursor.fetchall()
    print("All users in database:")
    for user in users:
        user_id, username, password_hash, role, created_at = user
        print(f"  ID: {user_id}, Username: {username}, Role: {role}, Created: {created_at}")
        # For common passwords, show if they match
        common_passwords = ["testpassword", "admin", "password", "123456", "SuperAdmin123!"]
        for pwd in common_passwords:
            # This is just for display, not actual verification
            if pwd == "testpassword" and password_hash == "13d249f2cb4127b40cfa757866850278793f814ded3c587fe5889e889a7a9f6c":
                print(f"    Password: {pwd} (likely)")
                break
            elif pwd == "admin" and password_hash == "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918":
                print(f"    Password: {pwd} (likely)")
                break
        print()
    
    # Close connection
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error connecting to database: {e}")
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
    
    # Check if bot_owners table exists and get data
    cursor.execute("SHOW TABLES LIKE 'bot_owners'")
    result = cursor.fetchone()
    if result:
        print("bot_owners table exists")
        cursor.execute("SELECT * FROM bot_owners")
        bots = cursor.fetchall()
        print(f"Bots in bot_owners table: {bots}")
    else:
        print("bot_owners table does not exist")
    
    # Check users table
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    print(f"Users in database: {users}")
    
    # Close connection
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error connecting to database: {e}")
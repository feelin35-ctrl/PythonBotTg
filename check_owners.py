import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    # Connect to database
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'telegram_bot_builder'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        port=int(os.getenv('DB_PORT', 3306))
    )
    
    cursor = conn.cursor()
    
    # Check bot owners
    cursor.execute('SELECT * FROM bot_owners')
    results = cursor.fetchall()
    
    print('Bot owners:')
    for row in results:
        print(row)
        
    # Check users
    cursor.execute('SELECT id, username FROM users')
    users = cursor.fetchall()
    
    print('\nUsers:')
    for row in users:
        print(row)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
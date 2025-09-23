import mysql.connector
import os

def check_database():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'telegram_bot_builder'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        cursor = conn.cursor()
        
        print("=== Bot Owners Table ===")
        cursor.execute('SELECT * FROM bot_owners')
        result = cursor.fetchall()
        for row in result:
            print(row)
            
        print("\n=== Users Table ===")
        cursor.execute('SELECT * FROM users')
        result = cursor.fetchall()
        for row in result:
            print(row)
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_database()
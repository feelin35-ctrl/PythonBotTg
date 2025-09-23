import os
os.environ['ENCRYPTION_KEY'] = 'E6OEVs6c_KnDECL17YqWKjikmkMBqYyHhxriHQYCqtY='

import mysql.connector
from mysql.connector import Error

# Database connection
connection = None
cursor = None
try:
    connection = mysql.connector.connect(
        host='localhost',
        database='telegram_bot_builder',
        user='root',
        password='',
        port=3306
    )
    
    if connection.is_connected():
        cursor = connection.cursor()
        
        # Get all tokens from the database
        query = "SELECT user_id, bot_id, token FROM user_tokens"
        cursor.execute(query)
        tokens = cursor.fetchall()
        
        print("All tokens in database:")
        for row in tokens:
            user_id, bot_id, encrypted_token = row
            print(f"User ID: {user_id}, Bot ID: {bot_id}")
            # Convert to string if needed
            encrypted_token_str = str(encrypted_token)
            print(f"Encrypted token: {encrypted_token_str[:20]}...")
            
            # Try to decrypt the token
            try:
                from core.security import decrypt_token
                decrypted_token = decrypt_token(encrypted_token_str)
                print(f"Decrypted token: {decrypted_token}")
                is_test = decrypted_token.startswith("123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ") or decrypted_token == "8495785437:AAFR_fwx0AlVTcVanFMwZ7Uf5Z4t3Sk-YdA"
                print(f"Is test token: {is_test}")
            except Exception as e:
                print(f"Error decrypting token: {e}")
            print("---")
            
except Error as e:
    print(f"Error connecting to MySQL: {e}")
finally:
    if connection and connection.is_connected():
        if cursor:
            cursor.close()
        connection.close()
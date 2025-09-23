import sys
import os
import requests
import time

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Use the same database connection pattern as the server
from core.db import db

def get_db_connection():
    """Get a new database connection"""
    # Create a new database instance to avoid connection issues
    from core.db import Database
    new_db = Database()
    if not new_db.connect():
        print("Failed to connect to database")
        return None
    return new_db

def test_deletion_fix():
    # Get a fresh database connection
    test_db = get_db_connection()
    if not test_db:
        return
    
    bot_id = "test_deletion_fix_bot_2"
    user_id = "1"  # Using a valid user ID
    
    # First, create a bot with ownership
    print("Creating test bot...")
    create_url = f"http://localhost:8001/api/create_bot/?bot_id={bot_id}&user_id={user_id}"
    try:
        response = requests.post(create_url)
        print(f"Create bot response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error creating bot: {e}")
        return
    
    # Wait a moment for the database to update
    time.sleep(1)
    
    # Check if the bot ownership was registered in the database
    print("Checking bot ownership in database...")
    query = "SELECT user_id FROM bot_owners WHERE bot_id = %s"
    result = test_db.execute_query(query, (bot_id,))
    print(f"Bot ownership in database: {result}")
    
    if result and len(result) > 0:
        print(f"SUCCESS: Bot ownership created for user {result[0][0]}")
    else:
        print("ERROR: Bot ownership not found in database")
        return
    
    # Close this connection and get a fresh one for checking after deletion
    test_db.disconnect()
    
    # Now test the delete endpoint
    print("Deleting bot...")
    delete_url = f"http://localhost:8001/api/delete_bot/{bot_id}/"
    try:
        response = requests.delete(delete_url)
        print(f"Delete bot response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error deleting bot: {e}")
        return
    
    # Wait a moment for the database to update
    time.sleep(1)
    
    # Get a fresh database connection to check if the bot ownership was deleted
    print("Getting fresh database connection...")
    check_db = get_db_connection()
    if not check_db:
        return
    
    # Check if the bot ownership was deleted from the database
    print("Checking bot ownership after deletion...")
    result_after = check_db.execute_query(query, (bot_id,))
    print(f"Bot ownership after deletion: {result_after}")
    
    check_db.disconnect()
    
    if result_after is None or len(result_after) == 0:
        print("SUCCESS: Bot ownership successfully deleted from database!")
    else:
        print("ERROR: Bot ownership still exists in database!")

if __name__ == "__main__":
    test_deletion_fix()
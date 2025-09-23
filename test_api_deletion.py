import sys
import os
import requests
import time

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Use the same database connection pattern as the server
from core.db import Database

def get_fresh_db_connection():
    """Get a fresh database connection"""
    new_db = Database()
    if not new_db.connect():
        print("Failed to connect to database")
        return None
    # Create tables to ensure they exist
    new_db.create_tables()
    return new_db

def test_api_deletion():
    # Get a fresh database connection
    test_db = get_fresh_db_connection()
    if not test_db:
        return
    
    bot_id = "api_test_bot_2"
    user_id = "1"  # Using a valid user ID
    
    # First, create a bot with ownership
    print("Creating test bot via API...")
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
    
    # Close the connection and get a fresh one
    test_db.disconnect()
    
    # Get user's bot list before deletion
    print("Getting user's bot list before deletion...")
    get_bots_url = f"http://localhost:8001/api/get_bots/?user_id={user_id}"
    try:
        response = requests.get(get_bots_url)
        print(f"Get bots response: {response.status_code} - {response.text}")
        bots_data = response.json()
        print(f"User's bots before deletion: {bots_data}")
    except Exception as e:
        print(f"Error getting bots: {e}")
        return
    
    # Now test the delete endpoint
    print("Deleting bot via API...")
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
    check_db = get_fresh_db_connection()
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
        return
    
    # Get user's bot list after deletion
    print("Getting user's bot list after deletion...")
    try:
        response = requests.get(get_bots_url)
        print(f"Get bots response: {response.status_code} - {response.text}")
        bots_data = response.json()
        print(f"User's bots after deletion: {bots_data}")
        
        # Check if the deleted bot is still in the list
        if bot_id in bots_data.get("bots", []):
            print("ERROR: Deleted bot still appears in user's bot list!")
        else:
            print("SUCCESS: Deleted bot is not in user's bot list!")
    except Exception as e:
        print(f"Error getting bots after deletion: {e}")
        return

if __name__ == "__main__":
    test_api_deletion()
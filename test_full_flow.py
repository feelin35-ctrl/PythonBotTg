import sys
import os
import requests
import time

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.db import db

def test_full_flow():
    # Connect to database
    if not db.connect():
        print("Failed to connect to database")
        return
    
    bot_id = "full_flow_test_bot"
    user_id = "1"  # Using a valid user ID
    
    # First, create a bot with ownership
    print("Creating test bot...")
    create_url = f"http://localhost:8001/api/create_bot/?bot_id={bot_id}&user_id={user_id}"
    response = requests.post(create_url)
    print(f"Create bot response: {response.status_code} - {response.text}")
    
    # Wait a moment for the database to update
    time.sleep(1)
    
    # Check if the bot ownership was registered in the database
    print("Checking bot ownership in database...")
    query = "SELECT user_id FROM bot_owners WHERE bot_id = %s"
    result = db.execute_query(query, (bot_id,))
    print(f"Bot ownership in database: {result}")
    
    if result and len(result) > 0:
        print(f"SUCCESS: Bot ownership created for user {result[0][0]}")
    else:
        print("ERROR: Bot ownership not found in database")
        return
    
    # Now test the delete endpoint
    print("Deleting bot...")
    delete_url = f"http://localhost:8001/api/delete_bot/{bot_id}/"
    response = requests.delete(delete_url)
    print(f"Delete bot response: {response.status_code} - {response.text}")
    
    # Wait a moment for the database to update
    time.sleep(1)
    
    # Check if the bot ownership was deleted from the database
    print("Checking bot ownership after deletion...")
    result_after = db.execute_query(query, (bot_id,))
    print(f"Bot ownership after deletion: {result_after}")
    
    if result_after is None or len(result_after) == 0:
        print("SUCCESS: Bot ownership successfully deleted from database!")
    else:
        print("ERROR: Bot ownership still exists in database!")

if __name__ == "__main__":
    test_full_flow()
import sys
import os
import requests
import time

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.db import db
from core.models import UserManager

def test_bot_deletion_db():
    # Connect to database
    if not db.connect():
        print("Failed to connect to database")
        return
    
    bot_id = "test_db_deletion_bot"
    user_id = "1"  # Using a valid user ID
    
    # First, create a bot with ownership directly in database
    print("Creating test bot ownership in database...")
    user_manager = UserManager()
    result = user_manager.register_bot_ownership(user_id, bot_id)
    print(f"Bot ownership creation result: {result}")
    
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
    
    # Now test the delete_bot_ownership method directly
    print("Deleting bot ownership directly...")
    deletion_result = user_manager.delete_bot_ownership(bot_id)
    print(f"Delete bot ownership result: {deletion_result}")
    
    # Check if the bot ownership was deleted from the database
    print("Checking bot ownership after deletion...")
    result_after = db.execute_query(query, (bot_id,))
    print(f"Bot ownership after deletion: {result_after}")
    
    if result_after is None or len(result_after) == 0:
        print("SUCCESS: Bot ownership successfully deleted from database!")
    else:
        print("ERROR: Bot ownership still exists in database!")
        return
    
    # Now test the get_user_bots method to make sure it doesn't return the deleted bot
    print("Checking get_user_bots method...")
    user_bots = user_manager.get_user_bots(user_id)
    print(f"User bots: {user_bots}")
    
    if bot_id not in user_bots:
        print("SUCCESS: Deleted bot is not in user's bot list!")
    else:
        print("ERROR: Deleted bot still appears in user's bot list!")

if __name__ == "__main__":
    test_bot_deletion_db()
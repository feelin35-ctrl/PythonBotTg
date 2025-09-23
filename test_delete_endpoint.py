import sys
import os
import requests
import json

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_delete_endpoint():
    # Test the delete endpoint
    bot_id = "test_endpoint_bot"
    user_id = "1"  # Using a valid user ID
    
    # First, create a bot with ownership
    print("Creating test bot...")
    create_url = f"http://localhost:8001/api/create_bot/?bot_id={bot_id}&user_id={user_id}"
    response = requests.post(create_url)
    print(f"Create bot response: {response.status_code} - {response.text}")
    
    # Check if the bot ownership was registered
    print("Checking bot ownership...")
    from core.models import UserManager
    user_manager = UserManager()
    owner = user_manager.get_bot_owner(bot_id)
    print(f"Bot owner before deletion: {owner}")
    
    # Now test the delete endpoint
    print("Deleting bot...")
    delete_url = f"http://localhost:8001/api/delete_bot/{bot_id}/"
    response = requests.delete(delete_url)
    print(f"Delete bot response: {response.status_code} - {response.text}")
    
    # Check if the bot ownership was deleted
    print("Checking bot ownership after deletion...")
    owner_after = user_manager.get_bot_owner(bot_id)
    print(f"Bot owner after deletion: {owner_after}")
    
    if owner_after is None:
        print("SUCCESS: Bot ownership successfully deleted from database via endpoint!")
    else:
        print("ERROR: Bot ownership still exists in database after endpoint call!")

if __name__ == "__main__":
    test_delete_endpoint()
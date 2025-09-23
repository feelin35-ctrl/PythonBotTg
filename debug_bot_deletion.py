import sys
import os
import json

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.db import db
from core.models import UserManager

def debug_bot_deletion(bot_id="test_bot_with_user"):
    """Debug function to check bot status and attempt deletion"""
    
    print(f"=== Debugging bot deletion for '{bot_id}' ===")
    
    # 1. Check if bot file exists
    bots_dir = "bots"
    bot_file_path = os.path.join(bots_dir, f"bot_{bot_id}.json")
    print(f"1. Bot file path: {bot_file_path}")
    print(f"   File exists: {os.path.exists(bot_file_path)}")
    
    # 2. Check tokens
    tokens_file = "bot_tokens.json"
    print(f"2. Tokens file: {tokens_file}")
    print(f"   File exists: {os.path.exists(tokens_file)}")
    
    if os.path.exists(tokens_file):
        try:
            with open(tokens_file, 'r') as f:
                tokens = json.load(f)
            print(f"   Bot in tokens: {bot_id in tokens}")
            if bot_id in tokens:
                print(f"   Token preview: {tokens[bot_id][:20]}...")
        except Exception as e:
            print(f"   Error reading tokens: {e}")
    
    # 3. Check database connection
    print("3. Database check:")
    if not db.connect():
        print("   Failed to connect to database")
        return
    
    # 4. Check bot ownership in database
    try:
        query = "SELECT user_id FROM bot_owners WHERE bot_id = %s"
        result = db.execute_query(query, (bot_id,))
        print(f"   Bot ownership in DB: {result}")
        if result and len(result) > 0:
            print(f"   Owner user ID: {result[0][0]}")
    except Exception as e:
        print(f"   Error checking bot ownership: {e}")
    
    # 5. Check all bot owners
    try:
        query = "SELECT bot_id, user_id FROM bot_owners"
        result = db.execute_query(query, ())
        print("   All bot owners in DB:")
        for row in result:
            print(f"     Bot: {row[0]}, User: {row[1]}")
    except Exception as e:
        print(f"   Error getting all bot owners: {e}")
    
    # 6. Try to get user bots for user 8 (based on previous logs)
    try:
        user_manager = UserManager()
        user_bots = user_manager.get_user_bots("8")
        print(f"   User 8 bots (before deletion): {user_bots}")
        print(f"   Target bot in user 8 list (before deletion): {bot_id in user_bots}")
    except Exception as e:
        print(f"   Error getting user bots: {e}")
    
    # 7. Try direct deletion
    print("7. Attempting direct deletion:")
    try:
        user_manager = UserManager()  # Make sure user_manager is defined
        
        # Delete file if exists
        if os.path.exists(bot_file_path):
            os.remove(bot_file_path)
            print("   Bot file deleted")
        else:
            print("   Bot file not found")
            
        # Delete from database
        deletion_result = user_manager.delete_bot_ownership(bot_id)
        print(f"   Database deletion result: {deletion_result}")
        
        # Delete token if exists
        if os.path.exists(tokens_file):
            with open(tokens_file, 'r') as f:
                tokens = json.load(f)
            if bot_id in tokens:
                del tokens[bot_id]
                with open(tokens_file, 'w') as f:
                    json.dump(tokens, f, indent=2)
                print("   Token deleted")
            else:
                print("   Token not found")
        
        print("Direct deletion completed")
        
        # 8. Check if bot is still in user's list after deletion
        print("8. Checking user's bot list after deletion:")
        try:
            user_bots_after = user_manager.get_user_bots("8")
            print(f"   User 8 bots (after deletion): {user_bots_after}")
            print(f"   Target bot in user 8 list (after deletion): {bot_id in user_bots_after}")
        except Exception as e:
            print(f"   Error getting user bots after deletion: {e}")
        
    except Exception as e:
        print(f"   Error during direct deletion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_bot_deletion()
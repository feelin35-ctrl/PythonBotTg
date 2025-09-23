import os
os.environ['ENCRYPTION_KEY'] = 'E6OEVs6c_KnDECL17YqWKjikmkMBqYyHhxriHQYCqtY='

from core.models import UserManager
from core.db import db

# Initialize database connection
if not db.connect():
    print("Failed to connect to database")
    exit(1)

if not db.create_tables():
    print("Failed to create database tables")
    exit(1)

# Get user manager
user_manager = UserManager()

# Check if there's a real token for mainBot
bot_id = "mainBot"
owner_id = user_manager.get_bot_owner(bot_id)

if owner_id:
    print(f"Bot {bot_id} is owned by user {owner_id}")
    token = user_manager.get_user_token(owner_id, bot_id)
    if token:
        print(f"Found token for bot {bot_id}: {token[:10]}...{token[-5:]}")
        # Validate the token format
        if ":" in token and len(token.split(":")[0]) >= 5 and len(token.split(":")[1]) >= 20:
            print("Token appears to be a valid Telegram token format")
        else:
            print("Token does not appear to be a valid Telegram token format")
    else:
        print(f"No token found for bot {bot_id}")
else:
    print(f"Bot {bot_id} has no owner")

# Close database connection
db.disconnect()
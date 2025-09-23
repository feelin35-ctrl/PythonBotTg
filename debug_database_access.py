import os
os.environ['ENCRYPTION_KEY'] = 'E6OEVs6c_KnDECL17YqWKjikmkMBqYyHhxriHQYCqtY='

from core.models import UserManager
from core.db import db

# Initialize database connection
print("Connecting to database...")
if not db.connect():
    print("Failed to connect to database")
    exit(1)

print("Creating tables...")
if not db.create_tables():
    print("Failed to create database tables")
    exit(1)

# Get user manager
print("Getting user manager...")
user_manager = UserManager()

# Check bot owner
bot_id = "mainBot"
print(f"Checking owner for bot {bot_id}...")
owner_id = user_manager.get_bot_owner(bot_id)
print(f"Owner ID: {owner_id}")

if owner_id:
    # Check user token
    print(f"Getting token for user {owner_id} and bot {bot_id}...")
    token = user_manager.get_user_token(owner_id, bot_id)
    print(f"Token: {token}")
    
    if token:
        print("SUCCESS: Retrieved token from database!")
        # Validate the token
        if ":" in token and len(token.split(":")[0]) >= 5 and len(token.split(":")[1]) >= 20:
            print("Token is valid Telegram token format")
        else:
            print("Token is not valid Telegram token format")
    else:
        print("ERROR: No token found in database")
else:
    print("ERROR: No owner found for bot")

# Close database connection
db.disconnect()
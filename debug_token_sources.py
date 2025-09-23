import os
os.environ['ENCRYPTION_KEY'] = 'E6OEVs6c_KnDECL17YqWKjikmkMBqYyHhxriHQYCqtY='

from main import get_bot_token
import json

bot_id = "mainBot"

# Check environment variables
print("Checking environment variables...")
env_token_key = f"BOT_TOKEN_{bot_id.upper()}"
env_token = os.getenv(env_token_key)
print(f"Environment variable {env_token_key}: {env_token}")

env_token_general = os.getenv("BOT_TOKEN")
print(f"General BOT_TOKEN environment variable: {env_token_general}")

# Check database
print("\nChecking database...")
try:
    from core.models import UserManager
    user_manager = UserManager()
    owner_id = user_manager.get_bot_owner(bot_id)
    print(f"Bot owner ID: {owner_id}")
    if owner_id:
        db_token = user_manager.get_user_token(owner_id, bot_id)
        print(f"Token from database: {db_token}")
    else:
        print("Bot has no owner in database")
except Exception as e:
    print(f"Error checking database: {e}")

# Check the final result
print("\nFinal result from get_bot_token:")
final_token = get_bot_token(bot_id)
print(f"Final token: {final_token}")
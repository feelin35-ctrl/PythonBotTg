import os
os.environ['ENCRYPTION_KEY'] = 'E6OEVs6c_KnDECL17YqWKjikmkMBqYyHhxriHQYCqtY='

from main import get_bot_token

# Test retrieving the token for mainBot
bot_id = "mainBot"
token = get_bot_token(bot_id)

if token:
    print(f"Successfully retrieved token for bot {bot_id}: {token[:10]}...{token[-5:]}")
    # Validate the token format
    if ":" in token and len(token.split(":")[0]) >= 5 and len(token.split(":")[1]) >= 20:
        print("Token is valid Telegram token format")
    else:
        print("Token is not valid Telegram token format")
else:
    print(f"Failed to retrieve token for bot {bot_id}")
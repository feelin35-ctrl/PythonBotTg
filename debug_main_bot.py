import os
os.environ['ENCRYPTION_KEY'] = 'E6OEVs6c_KnDECL17YqWKjikmkMBqYyHhxriHQYCqtY='

from main import get_bot_token
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

token = get_bot_token('mainBot')
print(f'Token: {token}')
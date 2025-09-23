import os
os.environ['ENCRYPTION_KEY'] = 'E6OEVs6c_KnDECL17YqWKjikmkMBqYyHhxriHQYCqtY='

from main import get_bot_token

token = get_bot_token('testBot123')
print(f'Token: {token}')
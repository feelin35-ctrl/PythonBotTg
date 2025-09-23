import os
os.environ['ENCRYPTION_KEY'] = 'E6OEVs6c_KnDECL17YqWKjikmkMBqYyHhxriHQYCqtY='

from core.models import UserManager
from core.db import db
from core.security import decrypt_token

db.connect()
result = db.execute_query('SELECT token FROM user_tokens WHERE user_id = %s AND bot_id = %s', ('9', 'testBot123'))
if result:
    token = decrypt_token(result[0][0])
    print(f'Token: {token}')
else:
    print('Token not found')
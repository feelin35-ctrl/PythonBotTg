import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the encryption key from the security module
from core.security import ENCRYPTION_KEY

print(f"Current encryption key: {ENCRYPTION_KEY}")

# Check if it's set in environment variables
env_key = os.getenv("ENCRYPTION_KEY")
print(f"Environment variable ENCRYPTION_KEY: {env_key}")
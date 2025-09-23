# Super Administrator Functionality

This document explains how the super administrator functionality works in the Telegram Bot Constructor system.

## Overview

The super administrator functionality allows specific users to see all chat bots in the system, regardless of ownership. Regular users can only see bots they own.

## Implementation Details

### Database Schema

The system uses a `users` table with an `is_admin` boolean field:
```sql
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
)
```

### API Endpoint

The `/api/get_bots/` endpoint in `main.py` checks if the user is an admin:

```python
@app.get("/api/get_bots/")
def get_bots_endpoint(user_id: Optional[str] = None):
    if user_id == "undefined" or not user_id:
        # Return empty list for invalid user_id
        bots = []
    else:
        # Check if user is super admin
        query = "SELECT is_admin FROM users WHERE id = %s"
        result = db.execute_query(query, (user_id,))
        
        if result and len(result) > 0 and result[0][0]:  # is_admin is True
            # Super admin sees all bots
            query = "SELECT bot_id FROM bot_owners"
            result = db.execute_query(query, ())
            bots = [row[0] for row in result] if result else []
        else:
            # Regular user sees only their bots
            user_manager = UserManager()
            user_bots = user_manager.get_user_bots(user_id)
            bots = user_bots
```

## Usage

### Creating a Super Admin User

1. **Using the create_admin_user.py script:**
   ```bash
   python create_admin_user.py
   ```
   This will prompt you to enter a username, email, and password for the new admin user.

2. **Listing existing admin users:**
   ```bash
   python create_admin_user.py list
   ```

### Promoting an Existing User to Admin

1. **List all users to find the user ID:**
   ```bash
   python promote_user_to_admin.py list
   ```

2. **Promote a user by ID:**
   ```bash
   python promote_user_to_admin.py [user_id]
   ```

### Testing the Functionality

You can test the super admin functionality using the test scripts:

1. **Test database directly:**
   ```bash
   python test_super_admin.py
   ```

2. **Test API endpoints:**
   ```bash
   python test_admin_api.py
   ```

## Verification

As shown in our tests:
- Admin users (like user ID 1) can see all 9 bots in the system
- Regular users (like user ID 3) can only see their own bots (1 bot)
- Invalid users or requests without user_id return empty lists

## Security Considerations

- Only trusted users should be granted admin privileges
- The admin password should be properly secured in production environments
- Consider implementing additional security measures for admin-only operations
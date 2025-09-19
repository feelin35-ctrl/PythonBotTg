# Bot "test_auto_update" for hosting deployment

## Description
This is a fully deployable bot with automatic update functionality from a GitHub repository.

## Project Structure
- `main.py` - Entry point for running the bot
- `bot_tokens.json` - File with bot token
- `bots/bot_test_auto_update.json` - Bot scenario file
- `requirements.txt` - Dependencies to install

## Installation and Startup

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Make sure the `bot_tokens.json` file contains the correct token
4. Run the bot:
   ```bash
   python main.py
   ```

## Automatic Updates from GitHub

The bot supports automatic updates from a GitHub repository. To enable this feature:

1. Create a repository on GitHub for your bot
2. Initialize a Git repository in the bot folder:
   ```bash
   git init
   git remote add origin <your_repository_URL>
   git add .
   git commit -m "Initial commit"
   git push -u origin main
   ```

3. Make sure Git is installed on the server

4. The bot will automatically check for updates every 60 minutes

5. When updates are available, the bot will:
   - Execute `git pull` to get the latest changes
   - Install new dependencies from requirements.txt (if any)
   - Restart to apply changes

## Manual Update Check

You can manually check for updates by sending the `/update` command to the bot.

## Hosting Deployment

### Heroku
1. Create an application on Heroku
2. Add Python buildpack
3. Deploy the project
4. Set environment variable for the token (if needed)

### PythonAnywhere
1. Upload all files via web interface or git
2. Install dependencies via console
3. Run main.py as a web application

### Other Hostings
The bot uses standard long polling, so it's suitable for most hosting providers.

## Support
If you have problems with deployment, refer to the bot constructor documentation.
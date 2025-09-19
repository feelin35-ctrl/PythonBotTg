from .base_block import BaseBlock
import telebot
from typing import Dict, Any, Optional
import subprocess
import sys
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AutoUpdateBlock(BaseBlock):
    
    # Class variables to track update status
    last_update_check = None
    update_interval = timedelta(hours=1)  # Check for updates every hour
    
    @staticmethod
    def get_block_type() -> str:
        return "auto_update"

    def execute(self, bot: telebot.TeleBot, chat_id: int, **kwargs) -> Optional[str]:
        """Execute the auto-update functionality"""
        try:
            # Send a message to the user that we're checking for updates
            bot.send_message(chat_id, "🔍 Проверяю наличие обновлений...")
            
            # Check for updates
            update_result = self.check_for_updates()
            
            if update_result["updated"]:
                # If updates were applied, notify the user
                bot.send_message(
                    chat_id, 
                    f"✅ Обновления успешно установлены!\n"
                    f"Обновлено файлов: {update_result['files_updated']}\n"
                    f"Последний коммит: {update_result['last_commit']}"
                )
                # Optionally restart the bot
                # This would require additional implementation in the main application
            elif update_result["error"]:
                # If there was an error during update check
                bot.send_message(
                    chat_id, 
                    f"❌ Ошибка при проверке обновлений:\n{update_result['error']}"
                )
            else:
                # If no updates were found
                bot.send_message(chat_id, "ℹ️ Обновлений не найдено. Бот работает в актуальной версии.")
                
        except Exception as e:
            logger.error(f"Error in auto update block: {e}")
            bot.send_message(chat_id, f"❌ Произошла ошибка при проверке обновлений: {str(e)}")
        
        # Return None to let ScenarioRunner find the next node
        return None

    def check_for_updates(self) -> Dict[str, Any]:
        """Check for updates from Git repository"""
        result = {
            "updated": False,
            "files_updated": 0,
            "last_commit": "",
            "error": None
        }
        
        try:
            # Check if enough time has passed since last check
            if (self.last_update_check and 
                datetime.now() - self.last_update_check < self.update_interval):
                return result
            
            # Update last check time
            self.last_update_check = datetime.now()
            
            # Check if git is available
            git_version = subprocess.run(
                ['git', '--version'], 
                capture_output=True, 
                text=True
            )
            
            if git_version.returncode != 0:
                result["error"] = "Git не установлен на сервере"
                return result
            
            # Check if this is a git repository
            git_status = subprocess.run(
                ['git', 'status', '--porcelain'], 
                capture_output=True, 
                text=True
            )
            
            if git_status.returncode != 0:
                result["error"] = "Это не Git репозиторий"
                return result
            
            # Fetch latest changes
            fetch_result = subprocess.run(
                ['git', 'fetch'], 
                capture_output=True, 
                text=True
            )
            
            if fetch_result.returncode != 0:
                result["error"] = f"Ошибка при получении изменений: {fetch_result.stderr}"
                return result
            
            # Check if there are new commits
            local_hash = subprocess.run(
                ['git', 'rev-parse', 'HEAD'], 
                capture_output=True, 
                text=True
            )
            
            remote_hash = subprocess.run(
                ['git', 'rev-parse', '@{u}'], 
                capture_output=True, 
                text=True
            )
            
            if local_hash.returncode != 0 or remote_hash.returncode != 0:
                result["error"] = "Ошибка при проверке хешей коммитов"
                return result
            
            # If hashes are different, there are updates
            if local_hash.stdout.strip() != remote_hash.stdout.strip():
                # Get info about the last commit before updating
                last_commit = subprocess.run(
                    ['git', 'log', '--oneline', '-1'], 
                    capture_output=True, 
                    text=True
                )
                
                if last_commit.returncode == 0:
                    result["last_commit"] = last_commit.stdout.strip()
                
                # Pull the updates
                pull_result = subprocess.run(
                    ['git', 'pull'], 
                    capture_output=True, 
                    text=True
                )
                
                if pull_result.returncode != 0:
                    result["error"] = f"Ошибка при загрузке обновлений: {pull_result.stderr}"
                    return result
                
                # Count updated files (simplified approach)
                status_result = subprocess.run(
                    ['git', 'status', '--porcelain'], 
                    capture_output=True, 
                    text=True
                )
                
                if status_result.returncode == 0:
                    # Count lines in status output as a rough estimate
                    result["files_updated"] = len(status_result.stdout.strip().split('\n')) if status_result.stdout.strip() else 0
                
                # Install/update dependencies if requirements.txt changed
                if os.path.exists('requirements.txt'):
                    pip_result = subprocess.run(
                        [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                        capture_output=True, 
                        text=True
                    )
                    
                    if pip_result.returncode != 0:
                        logger.warning(f"Warning during dependency installation: {pip_result.stderr}")
                
                result["updated"] = True
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error during update check: {e}")
        
        return result
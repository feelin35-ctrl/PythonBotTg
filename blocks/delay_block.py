from .base_block import BaseBlock
import telebot
from typing import Dict, Any, Optional
import time


class DelayBlock(BaseBlock):

    @staticmethod
    def get_block_type() -> str:
        return "delay"

    def execute(self, bot: telebot.TeleBot, chat_id: int, **kwargs) -> Optional[str]:
        # Get delay values from node data
        data = self.node_data.get('data', {})
        hours = data.get('hours', 0)
        minutes = data.get('minutes', 0)
        seconds = data.get('seconds', 0)
        
        # Calculate total delay in seconds
        total_delay = hours * 3600 + minutes * 60 + seconds
        
        # Add a message to inform user about the delay (optional)
        if total_delay > 0:
            delay_message = f"Ожидание {hours} ч {minutes} мин {seconds} сек..."
            try:
                bot.send_message(chat_id, delay_message)
            except Exception as e:
                # If we can't send the message, we still continue with the delay
                pass
            
            # Execute the delay
            time.sleep(total_delay)
        
        # Return None to let ScenarioRunner find the next node
        return None
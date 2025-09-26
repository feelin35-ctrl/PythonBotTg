from .base_block import BaseBlock
import telebot
from typing import Dict, Any, Optional
import datetime
import requests
import logging

logger = logging.getLogger(__name__)


class ScheduleBlock(BaseBlock):

    @staticmethod
    def get_block_type() -> str:
        return "schedule"

    def execute(self, bot: telebot.TeleBot, chat_id: int, **kwargs) -> Optional[str]:
        # Get configuration parameters
        data = self.node_data.get('data', {})
        date_question = data.get('dateQuestion', 'На какую дату вы хотите записаться?')
        time_question = data.get('timeQuestion', 'На какое время вы хотите записаться?')
        min_date = data.get('minDate')
        max_date = data.get('maxDate')
        time_interval = data.get('timeInterval', 30)
        work_start_time = data.get('workStartTime', '09:00')
        work_end_time = data.get('workEndTime', '18:00')
        crm_integration = data.get('crmIntegration', False)
        crm_endpoint = data.get('crmEndpoint', '')
        unavailable_message = data.get('unavailableMessage', 'Извините, это время уже занято. Пожалуйста, выберите другое.')
        
        # Store configuration in user context for later use
        user_context = kwargs.get('user_context', {})
        user_context['schedule_config'] = {
            'time_question': time_question,
            'time_interval': time_interval,
            'work_start_time': work_start_time,
            'work_end_time': work_end_time,
            'crm_integration': crm_integration,
            'crm_endpoint': crm_endpoint,
            'unavailable_message': unavailable_message
        }
        
        # Send date question to user
        bot.send_message(chat_id, date_question)
        
        # We'll handle the response in the scenario runner
        # For now, we just return None to indicate we're waiting for user input
        return None

    def process_date_response(self, bot: telebot.TeleBot, chat_id: int, date_str: str, **kwargs) -> Optional[str]:
        """Process user's date response"""
        # Get data and user context
        data = self.node_data.get('data', {})
        user_context = kwargs.get('user_context', {})
        
        try:
            # Try to parse the date in various formats
            selected_date = None
            
            # Try standard format first (YYYY-MM-DD)
            try:
                selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
            
            # If that fails, try other common formats
            if selected_date is None:
                # Try DD.MM.YYYY format
                try:
                    selected_date = datetime.datetime.strptime(date_str, '%d.%m.%Y').date()
                except ValueError:
                    pass
            
            # If that fails, try DD Month format (e.g., "28 сентября")
            if selected_date is None:
                try:
                    # Russian month names mapping
                    months_ru = {
                        'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
                        'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
                        'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
                    }
                    
                    # Split the input
                    parts = date_str.strip().split()
                    if len(parts) == 2:
                        day = int(parts[0])
                        month_name = parts[1].lower()
                        
                        if month_name in months_ru:
                            month = months_ru[month_name]
                            year = datetime.datetime.now().year
                            
                            # If the date is in the past, use next year
                            today = datetime.datetime.now().date()
                            selected_date = datetime.date(year, month, day)
                            if selected_date < today:
                                selected_date = datetime.date(year + 1, month, day)
                except (ValueError, IndexError):
                    pass
            
            # If we still couldn't parse the date, ask user to try again
            if selected_date is None:
                bot.send_message(chat_id, "Неверный формат даты. Пожалуйста, введите дату в формате:\n"
                                 "• ГГГГ-ММ-ДД (например, 2025-09-28)\n"
                                 "• ДД.ММ.ГГГГ (например, 28.09.2025)\n"
                                 "• ДД месяц (например, 28 сентября)")
                # Ask for date again
                date_question = data.get('dateQuestion', 'На какую дату вы хотите записаться?')
                bot.send_message(chat_id, date_question)
                return None
            
            # Check if date is within allowed range
            min_date_str = data.get('minDate')
            max_date_str = data.get('maxDate')
            
            if min_date_str:
                try:
                    min_date = datetime.datetime.strptime(min_date_str, '%Y-%m-%d').date()
                    if selected_date < min_date:
                        bot.send_message(chat_id, f"Выбранная дата должна быть не ранее {min_date.strftime('%d.%m.%Y')}")
                        # Ask for date again
                        date_question = data.get('dateQuestion', 'На какую дату вы хотите записаться?')
                        bot.send_message(chat_id, date_question)
                        return None
                except ValueError:
                    pass  # Invalid minDate format, ignore
            
            if max_date_str:
                try:
                    max_date = datetime.datetime.strptime(max_date_str, '%Y-%m-%d').date()
                    if selected_date > max_date:
                        bot.send_message(chat_id, f"Выбранная дата должна быть не позднее {max_date.strftime('%d.%m.%Y')}")
                        # Ask for date again
                        date_question = data.get('dateQuestion', 'На какую дату вы хотите записаться?')
                        bot.send_message(chat_id, date_question)
                        return None
                except ValueError:
                    pass  # Invalid maxDate format, ignore
            
            # Store selected date in user context in YYYY-MM-DD format
            user_context['selected_date'] = selected_date.strftime('%Y-%m-%d')
            
            # Check CRM availability if enabled
            crm_integration = data.get('crmIntegration', False)
            if crm_integration:
                crm_endpoint = data.get('crmEndpoint', '')
                if crm_endpoint:
                    available = self.check_crm_date_availability(crm_endpoint, selected_date.strftime('%Y-%m-%d'))
                    if not available:
                        bot.send_message(chat_id, "Выбранная дата недоступна. Пожалуйста, выберите другую дату.")
                        # Ask for date again
                        date_question = data.get('dateQuestion', 'На какую дату вы хотите записаться?')
                        bot.send_message(chat_id, date_question)
                        return None
            
            # Ask for time
            config = user_context.get('schedule_config', {})
            time_question = config.get('time_question', 'На какое время вы хотите записаться?')
            bot.send_message(chat_id, time_question)
            
            return None
        except Exception as e:
            logger.error(f"Error processing date response: {e}")
            bot.send_message(chat_id, "Неверный формат даты. Пожалуйста, введите дату в формате:\n"
                             "• ГГГГ-ММ-ДД (например, 2025-09-28)\n"
                             "• ДД.ММ.ГГГГ (например, 28.09.2025)\n"
                             "• ДД месяц (например, 28 сентября)")
            # Ask for date again
            date_question = data.get('dateQuestion', 'На какую дату вы хотите записаться?')
            bot.send_message(chat_id, date_question)
            return None

    def process_time_response(self, bot: telebot.TeleBot, chat_id: int, time_str: str, **kwargs) -> Optional[str]:
        """Process user's time response"""
        # Get user context
        user_context = kwargs.get('user_context', {})
        config = user_context.get('schedule_config', {})
        
        try:
            # Try to parse the time in various formats
            parsed_time = None
            
            # Try standard format first (HH:MM)
            try:
                parsed_time = datetime.datetime.strptime(time_str, '%H:%M').time()
            except ValueError:
                pass
            
            # If that fails, try HH.MM format
            if parsed_time is None:
                try:
                    parsed_time = datetime.datetime.strptime(time_str, '%H.%M').time()
                except ValueError:
                    pass
            
            # If that fails, try H:MM format
            if parsed_time is None:
                try:
                    parsed_time = datetime.datetime.strptime(time_str, '%H:%M').time()
                except ValueError:
                    pass
            
            # If that fails, try H MM format (e.g., "9 30")
            if parsed_time is None:
                try:
                    parts = time_str.strip().split()
                    if len(parts) == 2:
                        hour = int(parts[0])
                        minute = int(parts[1])
                        parsed_time = datetime.time(hour, minute)
                except (ValueError, IndexError):
                    pass
            
            # If we still couldn't parse the time, ask user to try again
            if parsed_time is None:
                bot.send_message(chat_id, "Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ (например, 14:30) или ЧЧ.ММ (например, 14.30)")
                # Ask for time again
                time_question = config.get('time_question', 'На какое время вы хотите записаться?')
                bot.send_message(chat_id, time_question)
                return None
            
            # Format time as HH:MM
            formatted_time = parsed_time.strftime('%H:%M')
            
            selected_date = user_context.get('selected_date')
            
            # Check CRM availability if enabled
            crm_integration = config.get('crm_integration', False)
            if crm_integration:
                crm_endpoint = config.get('crm_endpoint', '')
                if crm_endpoint and selected_date:
                    available = self.check_crm_time_availability(crm_endpoint, selected_date, formatted_time)
                    if not available:
                        unavailable_message = config.get('unavailable_message', 'Извините, это время уже занято. Пожалуйста, выберите другое.')
                        bot.send_message(chat_id, unavailable_message)
                        # Ask for time again
                        time_question = config.get('time_question', 'На какое время вы хотите записаться?')
                        bot.send_message(chat_id, time_question)
                        return None
            
            # If we reach here, the date and time are valid
            # Send confirmation to user
            if selected_date:
                # Format date for display
                try:
                    date_obj = datetime.datetime.strptime(selected_date, '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%d.%m.%Y')
                except ValueError:
                    formatted_date = selected_date
                
                confirmation = f"Вы записаны на {formatted_date} в {formatted_time}"
                bot.send_message(chat_id, confirmation)
            
            # Send information to bot administrator
            self.send_to_administrator(bot, chat_id, selected_date, formatted_time, user_context, kwargs)
            
            # Return next node ID (None means we're done with this interaction)
            return None
        except Exception as e:
            logger.error(f"Error processing time response: {e}")
            bot.send_message(chat_id, "Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ (например, 14:30) или ЧЧ.ММ (например, 14.30)")
            # Ask for time again
            time_question = config.get('time_question', 'На какое время вы хотите записаться?')
            bot.send_message(chat_id, time_question)
            return None

    def send_to_administrator(self, bot: telebot.TeleBot, user_chat_id: int, date_str: str, time_str: str, user_context: dict, kwargs: dict):
        """Send scheduling information to bot administrator"""
        try:
            # Get admin chat ID from scenario data if available
            scenario_data = kwargs.get('scenario_data', {})
            
            # Check for 'adminChatId' first (frontend format), then 'admin_chat_id' (backend format)
            admin_chat_id = scenario_data.get('adminChatId') or scenario_data.get('admin_chat_id')
            
            # If no admin chat ID in scenario, try to get it from node data
            if not admin_chat_id:
                data = self.node_data.get('data', {})
                # Check for 'adminChatId' first (frontend format), then 'admin_chat_id' (backend format)
                admin_chat_id = data.get('adminChatId') or data.get('admin_chat_id')
            
            # If still no admin chat ID, log a warning and send to user for demo purposes
            if not admin_chat_id:
                logger.warning("Admin chat ID not configured. Sending notification to user instead.")
                admin_chat_id = user_chat_id
            
            # Get bot information to include in the message
            bot_info = bot.get_me()
            bot_username = bot_info.username if bot_info.username else "Неизвестный бот"
            
            # Create message for administrator
            admin_message = f"""
🔔 Новая запись через бота @{bot_username}

📅 Дата: {date_str}
⏰ Время: {time_str}
👤 Пользователь: tg://user?id={user_chat_id}
🔗 Ссылка на пользователя: tg://user?id={user_chat_id}

Пожалуйста, свяжитесь с пользователем для подтверждения записи.
            """.strip()
            
            # Send message to administrator
            bot.send_message(admin_chat_id, admin_message)
            
            logger.info(f"Sent scheduling information to administrator {admin_chat_id} for user {user_chat_id}")
        except Exception as e:
            logger.error(f"Error sending information to administrator: {e}")

    def check_crm_date_availability(self, crm_endpoint: str, date_str: str) -> bool:
        """Check date availability with CRM"""
        try:
            response = requests.get(f"{crm_endpoint}?date={date_str}")
            if response.status_code == 200:
                data = response.json()
                return data.get('available', True)
            return True  # Default to available if CRM is unreachable
        except Exception as e:
            logger.error(f"Error checking CRM date availability: {e}")
            return True  # Default to available if CRM is unreachable

    def check_crm_time_availability(self, crm_endpoint: str, date_str: str, time_str: str) -> bool:
        """Check time availability with CRM"""
        try:
            response = requests.get(f"{crm_endpoint}?date={date_str}&time={time_str}")
            if response.status_code == 200:
                data = response.json()
                return data.get('available', True)
            return True  # Default to available if CRM is unreachable
        except Exception as e:
            logger.error(f"Error checking CRM time availability: {e}")
            return True  # Default to available if CRM is unreachable
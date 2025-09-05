import asyncio
import logging
from datetime import datetime, time
from typing import Optional, Dict, Any
import pytz

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings, DEFAULT_NOTIFICATION_TIME
from database import DatabaseManager, User, init_db
from weather_api import weather_api
from localization import localization, get_user_language, _
from city_timezone_mapper import format_local_time

logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)

class BotStates(StatesGroup):
    LANGUAGE_SELECT = State()
    MAIN_MENU = State()
    WAITING_CITY = State()
    SELECTING_CITY = State()
    WAITING_TIME = State()
    IN_SETTINGS = State()
    VIEWING_WEATHER = State()

bot = Bot(token=settings.telegram_bot_token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class WeatherBot:
    def __init__(self):
        self.bot = bot
        self.dp = dp
        self.user_last_action = {}  # Track last action time per user
        self.user_action_types = {}  # Track action types per user
        
        # Smart throttling - different intervals for different actions
        self.throttle_config = {
            'navigation': 0.3,      # Quick navigation (menus, back buttons)
            'weather': 1.0,         # Weather requests (API calls)
            'settings': 0.5,        # Settings changes
            'default': 0.5          # Default for other actions
        }
    
    async def is_throttled(self, user_id: int, action_type: str = 'default') -> bool:
        now = datetime.now().timestamp()
        last_action = self.user_last_action.get(user_id, 0)
        throttle_time = self.throttle_config.get(action_type, self.throttle_config['default'])
        
        if now - last_action < throttle_time:
            return True
        
        self.user_last_action[user_id] = now
        self.user_action_types[user_id] = action_type
        return False
        
    async def create_inline_keyboard(self, buttons: list) -> InlineKeyboardMarkup:
        keyboard = []
        for row in buttons:
            keyboard_row = []
            for text, callback_data in row:
                keyboard_row.append(InlineKeyboardButton(text=text, callback_data=callback_data))
            keyboard.append(keyboard_row)
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    async def get_main_menu_keyboard(self, user: User, language: str) -> InlineKeyboardMarkup:
        city_text = _(
            "my_city" if user.city else "my_city_not_set", 
            language, 
            city=user.city or ""
        )
        
        time_text = _("notification_time", language, time=str(user.notification_time)[:5])
        
        notifications_text = _(
            "notifications_on" if user.notifications_enabled else "notifications_off", 
            language
        )
        
        buttons = [
            [(city_text, "select_city")],
            [(time_text, "select_time"), (notifications_text, "toggle_notifications")],
            [(_("weather_now", language), "weather_now"), (_("settings", language), "settings")]
        ]
        
        return await self.create_inline_keyboard(buttons)
    
    async def get_city_selection_keyboard(self, language: str) -> InlineKeyboardMarkup:
        buttons = localization.get_popular_cities(language)
        buttons.append([(_("enter_city", language), "enter_custom_city")])
        buttons.append([(_("back_to_menu", language), "main_menu")])
        
        return await self.create_inline_keyboard(buttons)
    
    async def get_time_selection_keyboard(self, language: str) -> InlineKeyboardMarkup:
        buttons = localization.get_time_slots(language)
        buttons.append([(_("custom_time", language), "enter_custom_time")])
        buttons.append([(_("back_to_menu", language), "main_menu")])
        
        return await self.create_inline_keyboard(buttons)
    
    async def get_settings_keyboard(self, user: User, language: str) -> InlineKeyboardMarkup:
        notifications_status = "Вкл" if user.notifications_enabled else "Выкл" if language == "ru" else "On" if user.notifications_enabled else "Off"
        
        buttons = [
            [(_("change_city", language), "select_city")],
            [(_("change_time", language), "select_time")],
            [(_("toggle_notifications", language, status=notifications_status), "toggle_notifications")],
            [(_("language", language), "select_language")],
            [(_("my_status", language), "my_status"), (_("help", language), "help")],
            [(_("back_to_menu", language), "main_menu")]
        ]
        
        return await self.create_inline_keyboard(buttons)
    
    async def get_weather_keyboard(self, language: str) -> InlineKeyboardMarkup:
        buttons = [
            [(_("hourly_forecast", language), "hourly_forecast"), (_("daily_forecast", language), "daily_forecast")],
            [(_("refresh", language), "weather_now"), (_("settings", language), "settings")],
            [(_("back_to_menu", language), "main_menu")]
        ]
        
        return await self.create_inline_keyboard(buttons)
    
    async def format_weather_message(self, weather_data: Dict, city: str, language: str, city_lat: float = None, city_lon: float = None) -> str:
        if city_lat is not None and city_lon is not None:
            today_date, current_time = format_local_time(city_lat, city_lon)
        else:
            utc_now = datetime.now(pytz.UTC)
            today_date = utc_now.strftime("%d.%m.%Y")
            current_time = utc_now.strftime("%H:%M")
        
        clothing_advice = weather_api.get_clothing_recommendation(weather_data, language)
        
        if language == "ru":
            weather_title = f"🌤 Погода в {city} на {today_date} в {current_time}"
        elif language == "uk":
            weather_title = f"🌤 Погода в {city} на {today_date} о {current_time}"
        else:
            weather_title = f"🌤 Weather in {city} for {today_date} at {current_time}"
        
        message = weather_title + "\n\n"
        message += _("current_temp", language, 
                    temp=weather_data["current_temperature"], 
                    feels_like=weather_data["feels_like"]) + "\n"
        message += _("today_range", language, 
                    min=weather_data["min_temperature"], 
                    max=weather_data["max_temperature"]) + "\n"
        message += f"☁️ {weather_data['description']}\n"
        message += _("humidity", language, humidity=weather_data["humidity"]) + "\n"
        message += _("wind", language, speed=weather_data["wind_speed"]) + "\n"
        message += _("rain_prob", language, prob=weather_data["rain_probability"]) + "\n\n"
        message += _("recommendation", language, advice=clothing_advice) + "\n\n"
        message += _("have_great_day", language)
        
        return message

    async def cmd_start(self, message: Message, state: FSMContext):
        user_id = message.from_user.id
        
        # Log user action
        await DatabaseManager.log_action(user_id, "start_command")
        
        # Check if user exists
        user = await DatabaseManager.get_user(user_id)
        
        if not user:
            # New user - show language selection
            keyboard = await self.create_inline_keyboard(localization.get_language_keyboard())
            await message.answer(
                _("welcome_choose_language"),
                reply_markup=keyboard
            )
            await state.set_state(BotStates.LANGUAGE_SELECT)
        else:
            # Existing user - show main menu
            language = user.language
            keyboard = await self.get_main_menu_keyboard(user, language)
            await message.answer(
                _("welcome_message", language),
                reply_markup=keyboard
            )
            await state.set_state(BotStates.MAIN_MENU)
    
    # Callback handlers
    async def handle_language_selection(self, callback: CallbackQuery, state: FSMContext):
        user_id = callback.from_user.id
        
        # Apply throttling for settings
        if await self.is_throttled(user_id, 'settings'):
            await callback.answer()
            return
        
        language = callback.data.split("_")[1]
        
        timezone_map = {
            "ru": "Europe/Kiev",
            "uk": "Europe/Kiev",
            "en": "Europe/London"
        }
        timezone = timezone_map.get(language, "Europe/London")
        
        user = await DatabaseManager.create_or_update_user(user_id, language=language, timezone=timezone)
        
        await DatabaseManager.log_action(user_id, "language_selected", {"language": language})
        
        keyboard = await self.get_main_menu_keyboard(user, language)
        await callback.message.edit_text(
            _("welcome_message", language),
            reply_markup=keyboard
        )
        await callback.answer(_("language_changed", language))
        await state.set_state(BotStates.MAIN_MENU)
    
    async def handle_main_menu(self, callback: CallbackQuery, state: FSMContext):
        user_id = callback.from_user.id
        
        # Apply throttling for navigation
        if await self.is_throttled(user_id, 'navigation'):
            await callback.answer()
            return
        
        user = await DatabaseManager.get_user(user_id)
        
        if not user:
            language = callback.from_user.language_code or "en"
            user = await DatabaseManager.create_or_update_user(user_id, language=language)
        
        language = user.language
        
        keyboard = await self.get_main_menu_keyboard(user, language)
        await callback.message.edit_text(
            _("main_menu", language),
            reply_markup=keyboard
        )
        await callback.answer()
        await state.set_state(BotStates.MAIN_MENU)
    
    async def handle_city_selection(self, callback: CallbackQuery, state: FSMContext):
        """Handle city selection menu"""
        user_id = callback.from_user.id
        
        # Apply throttling for navigation
        if await self.is_throttled(user_id, 'navigation'):
            await callback.answer()
            return
        
        user = await DatabaseManager.get_user(user_id)
        
        # If user doesn't exist, create with default language
        if not user:
            language = callback.from_user.language_code or "en"
            user = await DatabaseManager.create_or_update_user(user_id, language=language)
        
        language = user.language
        
        if callback.data == "select_city":
            keyboard = await self.get_city_selection_keyboard(language)
            await callback.message.edit_text(
                _("select_city", language),
                reply_markup=keyboard
            )
            await callback.answer()
        elif callback.data == "enter_custom_city":
            await callback.message.edit_text(_("enter_city_name", language))
            await callback.answer()
            await state.set_state(BotStates.WAITING_CITY)
        elif callback.data.startswith("city_"):
            city_name = callback.data[5:]  # Remove "city_" prefix
            await self.set_user_city(callback, city_name, language, state)
    
    async def handle_time_selection(self, callback: CallbackQuery, state: FSMContext):
        """Handle time selection menu"""
        user_id = callback.from_user.id
        
        # Apply throttling for navigation
        if await self.is_throttled(user_id, 'navigation'):
            await callback.answer()
            return
        
        user = await DatabaseManager.get_user(user_id)
        
        # If user doesn't exist, create with default language
        if not user:
            language = callback.from_user.language_code or "en"
            user = await DatabaseManager.create_or_update_user(user_id, language=language)
        
        language = user.language
        
        if callback.data == "select_time":
            keyboard = await self.get_time_selection_keyboard(language)
            city_name = user.city or "your city"
            await callback.message.edit_text(
                _("select_time", language, city=city_name),
                reply_markup=keyboard
            )
            await callback.answer()
        elif callback.data == "enter_custom_time":
            city_name = user.city or "your city"
            await callback.message.edit_text(_("enter_time", language, city=city_name))
            await callback.answer()
            await state.set_state(BotStates.WAITING_TIME)
        elif callback.data.startswith("time_"):
            time_str = callback.data[5:]  # Remove "time_" prefix
            await self.set_user_time(callback, time_str, language, state)
    
    async def handle_settings(self, callback: CallbackQuery, state: FSMContext):
        """Handle settings menu"""
        user_id = callback.from_user.id
        
        # Apply throttling for navigation
        if await self.is_throttled(user_id, 'navigation'):
            await callback.answer()
            return
        
        user = await DatabaseManager.get_user(user_id)
        
        # If user doesn't exist, create with default language
        if not user:
            language = callback.from_user.language_code or "en"
            user = await DatabaseManager.create_or_update_user(user_id, language=language)
        
        language = user.language
        
        if callback.data == "settings":
            keyboard = await self.get_settings_keyboard(user, language)
            await callback.message.edit_text(
                _("settings_menu", language),
                reply_markup=keyboard
            )
            await callback.answer()
            await state.set_state(BotStates.IN_SETTINGS)
        elif callback.data == "select_language":
            keyboard = await self.create_inline_keyboard(localization.get_language_keyboard())
            await callback.message.edit_text(
                _("welcome_choose_language", language),
                reply_markup=keyboard
            )
            await callback.answer()
        elif callback.data == "my_status":
            await self.show_user_status(callback, user, language)
        elif callback.data == "help":
            await self.show_help(callback, language)
    
    async def handle_notifications_toggle(self, callback: CallbackQuery, state: FSMContext):
        """Handle notifications toggle"""
        user_id = callback.from_user.id
        
        # Apply throttling for settings
        if await self.is_throttled(user_id, 'settings'):
            await callback.answer()
            return
        
        user = await DatabaseManager.get_user(user_id)
        
        # If user doesn't exist, create with default language
        if not user:
            language = callback.from_user.language_code or "en"
            user = await DatabaseManager.create_or_update_user(user_id, language=language)
        
        language = user.language
        
        # Toggle notifications
        new_status = not user.notifications_enabled
        await DatabaseManager.create_or_update_user(user_id, notifications_enabled=new_status)
        
        # Log action
        await DatabaseManager.log_action(user_id, "notifications_toggled", {"enabled": new_status})
        
        # Update user object
        user.notifications_enabled = new_status
        
        # Show updated main menu
        keyboard = await self.get_main_menu_keyboard(user, language)
        await callback.message.edit_text(
            _("main_menu", language),
            reply_markup=keyboard
        )
        
        status_message = _("notifications_enabled" if new_status else "notifications_disabled", language)
        await callback.answer(status_message)
        await state.set_state(BotStates.MAIN_MENU)
    
    async def handle_weather_now(self, callback: CallbackQuery, state: FSMContext):
        """Handle weather now request"""
        user_id = callback.from_user.id
        
        # Apply throttling for weather requests
        if await self.is_throttled(user_id, 'weather'):
            await callback.answer()
            return
        
        user = await DatabaseManager.get_user(user_id)
        
        # If user doesn't exist, create with default language
        if not user:
            language = callback.from_user.language_code or "en"
            user = await DatabaseManager.create_or_update_user(user_id, language=language)
        
        language = user.language
        
        if not user.city or not user.city_lat or not user.city_lon:
            await callback.answer(_("setup_required", language))
            return
        
        # Show loading message
        if language == "ru":
            loading_text = "🌤 Получаю прогноз погоды..."
        elif language == "uk":
            loading_text = "🌤 Отримую прогноз погоди..."
        else:
            loading_text = "🌤 Getting weather forecast..."
        
        await callback.message.edit_text(loading_text)
        await callback.answer()
        
        try:
            # Get weather data
            weather_data = await weather_api.get_weather_forecast(
                float(user.city_lat), 
                float(user.city_lon), 
                language
            )
            
            if weather_data:
                # Use city coordinates for local time
                message = await self.format_weather_message(
                    weather_data, 
                    user.city, 
                    language, 
                    float(user.city_lat), 
                    float(user.city_lon)
                )
                keyboard = await self.get_weather_keyboard(language)
                
                await callback.message.edit_text(message, reply_markup=keyboard)
                await DatabaseManager.log_action(user_id, "weather_requested")
            else:
                await callback.message.edit_text(_("weather_error", language))
        except Exception as e:
            logger.error(f"Error getting weather for user {user_id}: {e}")
            await callback.message.edit_text(_("weather_error", language))
        
        await state.set_state(BotStates.VIEWING_WEATHER)
    
    async def set_user_city(self, callback: CallbackQuery, city_name: str, language: str, state: FSMContext):
        """Set user's city"""
        user_id = callback.from_user.id
        
        # Get city coordinates
        coordinates = await weather_api.get_city_coordinates(city_name)
        
        if coordinates:
            lat, lon, display_name = coordinates
            city_display = city_name if city_name in display_name else display_name.split(',')[0]
            
            # Update user
            await DatabaseManager.create_or_update_user(
                user_id, 
                city=city_display,
                city_lat=lat,
                city_lon=lon
            )
            
            # Log action
            await DatabaseManager.log_action(user_id, "city_set", {"city": city_display})
            
            # Get updated user and show main menu
            user = await DatabaseManager.get_user(user_id)
            keyboard = await self.get_main_menu_keyboard(user, language)
            
            await callback.message.edit_text(
                _("main_menu", language),
                reply_markup=keyboard
            )
            await callback.answer(_("city_set", language, city=city_display))
            await state.set_state(BotStates.MAIN_MENU)
        else:
            await callback.answer(_("city_not_found", language))
    
    async def set_user_time(self, callback: CallbackQuery, time_str: str, language: str, state: FSMContext):
        """Set user's notification time"""
        user_id = callback.from_user.id
        
        try:
            # Parse time
            hour, minute = map(int, time_str.split(':'))
            notification_time = time(hour, minute)
            
            # Update user
            await DatabaseManager.create_or_update_user(user_id, notification_time=notification_time)
            
            # Log action
            await DatabaseManager.log_action(user_id, "time_set", {"time": time_str})
            
            # Get updated user and show main menu
            user = await DatabaseManager.get_user(user_id)
            keyboard = await self.get_main_menu_keyboard(user, language)
            
            await callback.message.edit_text(
                _("main_menu", language),
                reply_markup=keyboard
            )
            city_name = user.city or "your city"
            await callback.answer(_("time_set", language, time=time_str, city=city_name))
            await state.set_state(BotStates.MAIN_MENU)
        except ValueError:
            await callback.answer(_("invalid_time", language))
    
    async def show_user_status(self, callback: CallbackQuery, user: User, language: str):
        """Show user status"""
        notifications_status = "Вкл" if user.notifications_enabled else "Выкл" if language == "ru" else "On" if user.notifications_enabled else "Off"
        created_date = user.created_at.strftime("%Y-%m-%d") if user.created_at else "Unknown"
        
        status_text = _("status_info", language,
                       city=user.city or "Not set",
                       time=str(user.notification_time)[:5] if user.notification_time else "09:00",
                       notifications=notifications_status,
                       date=created_date)
        
        keyboard = await self.create_inline_keyboard([[(_("back", language), "settings")]])
        await callback.message.edit_text(status_text, reply_markup=keyboard)
        await callback.answer()
    
    async def show_help(self, callback: CallbackQuery, language: str):
        """Show help information"""
        help_text = _("help_text", language)
        keyboard = await self.create_inline_keyboard([[(_("back", language), "settings")]])
        await callback.message.edit_text(help_text, reply_markup=keyboard)
        await callback.answer()
    
    async def handle_hourly_forecast(self, callback: CallbackQuery, state: FSMContext):
        """Handle hourly forecast request"""
        user_id = callback.from_user.id
        
        # Apply throttling for weather requests
        if await self.is_throttled(user_id, 'weather'):
            await callback.answer()
            return
        
        user = await DatabaseManager.get_user(user_id)
        
        # If user doesn't exist, create with default language
        if not user:
            language = callback.from_user.language_code or "en"
            user = await DatabaseManager.create_or_update_user(user_id, language=language)
        
        language = user.language
        
        if not user.city or not user.city_lat or not user.city_lon:
            await callback.answer(_("setup_required", language))
            return
        
        # Get weather data with hourly forecast
        weather_data = await weather_api.get_weather_forecast(
            float(user.city_lat), 
            float(user.city_lon), 
            language,
            days=1
        )
        
        if weather_data and weather_data.get("hourly_forecast"):
            # Get current time in city's local timezone (same as main weather display)
            today_date, current_time = format_local_time(float(user.city_lat), float(user.city_lon))
            current_hour = int(current_time.split(':')[0])  # Extract hour from local time
            
            message = _("hourly_title", language, date=today_date) + "\n\n"
            
            hourly_data = weather_data["hourly_forecast"]
            
            # Show next 12 hours starting from current local hour
            for i, hour_data in enumerate(hourly_data[current_hour:current_hour+12]):
                if i < len(hourly_data):
                    # Get weather emoji based on weather code
                    weather_emoji = weather_api._get_weather_emoji(hour_data.get('weather_code', 0))
                    time_emoji = "🕐" if i == 0 else "⏰"
                    message += f"{time_emoji} {hour_data['time']}: {hour_data['temperature']}°C {weather_emoji} {hour_data['description']}\n"
            
            keyboard = await self.create_inline_keyboard([
                [(_("daily_forecast", language), "daily_forecast"), (_("weather_now", language), "weather_now")],
                [(_("back_to_menu", language), "main_menu")]
            ])
            
            await callback.message.edit_text(message, reply_markup=keyboard)
            await DatabaseManager.log_action(user_id, "hourly_forecast_requested")
        else:
            await callback.message.edit_text(_("weather_error", language))
        
        await callback.answer()
        await state.set_state(BotStates.VIEWING_WEATHER)
    
    async def handle_daily_forecast(self, callback: CallbackQuery, state: FSMContext):
        """Handle daily forecast request"""
        user_id = callback.from_user.id
        
        # Apply throttling for weather requests
        if await self.is_throttled(user_id, 'weather'):
            await callback.answer()
            return
        
        user = await DatabaseManager.get_user(user_id)
        
        # If user doesn't exist, create with default language
        if not user:
            language = callback.from_user.language_code or "en"
            user = await DatabaseManager.create_or_update_user(user_id, language=language)
        
        language = user.language
        
        if not user.city or not user.city_lat or not user.city_lon:
            await callback.answer(_("setup_required", language))
            return
        
        # Get weather data for 7 days
        weather_data = await weather_api.get_weather_forecast(
            float(user.city_lat), 
            float(user.city_lon), 
            language,
            days=7
        )
        
        if weather_data and weather_data.get("daily_forecast"):
            message = _("daily_title", language, days=7) + f" - {user.city}\n\n"
            
            daily_data = weather_data["daily_forecast"]
            
            for i, day_data in enumerate(daily_data):
                day_emoji = "📅" if i == 0 else "📆"
                day_name = _("today", language) if i == 0 else (_("tomorrow", language) if i == 1 else day_data["day_name"])
                
                # Get weather emoji based on weather code
                weather_emoji = weather_api._get_weather_emoji(day_data.get('weather_code', 0))
                
                message += f"{day_emoji} {day_name} ({day_data['date_display']}):\n"
                message += f"   🌡️ {day_data['min_temperature']}°C ... {day_data['max_temperature']}°C\n"
                message += f"   {weather_emoji} {day_data['description']}\n"
                if day_data['rain_probability'] > 0:
                    message += f"   🌧️ {day_data['rain_probability']}%\n"
                message += "\n"
            
            keyboard = await self.create_inline_keyboard([
                [(_("hourly_forecast", language), "hourly_forecast"), (_("weather_now", language), "weather_now")],
                [(_("back_to_menu", language), "main_menu")]
            ])
            
            await callback.message.edit_text(message, reply_markup=keyboard)
            await DatabaseManager.log_action(user_id, "daily_forecast_requested")
        else:
            await callback.message.edit_text(_("weather_error", language))
        
        await callback.answer()
        await state.set_state(BotStates.VIEWING_WEATHER)
    
    # Text message handlers for states
    async def handle_city_input(self, message: Message, state: FSMContext):
        """Handle city name input with multiple city selection"""
        user_id = message.from_user.id
        user = await DatabaseManager.get_user(user_id)
        
        # If user doesn't exist, create with default language
        if not user:
            language = message.from_user.language_code or "en"
            user = await DatabaseManager.create_or_update_user(user_id, language=language)
        
        language = user.language
        city_name = message.text.strip()
        
        # Show typing indicator and search message
        await self.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        
        # Send search message
        if language == "ru":
            search_msg = await message.answer("🔍 Ищу город...")
        elif language == "uk":
            search_msg = await message.answer("🔍 Шукаю місто...")
        else:
            search_msg = await message.answer("🔍 Searching for city...")
        
        try:
            # Search for multiple cities
            cities = await weather_api.search_cities(city_name, limit=5)
            
            # Delete search message
            await search_msg.delete()
            
            if not cities:
                await message.answer(_("city_not_found", language))
                return
            
            if len(cities) == 1:
                # Only one city found, set it directly
                city = cities[0]
                await self.set_user_city_from_data(
                    message, user_id, city, language, state
                )
            else:
                # Multiple cities found, show selection
                await self.show_city_selection(message, cities, language, state)
                
        except Exception as e:
            # Delete search message in case of error
            try:
                await search_msg.delete()
            except:
                pass
            
            logger.error(f"Error searching for city {city_name}: {e}")
            await message.answer(_("city_not_found", language))
    
    async def set_user_city_from_data(self, message, user_id: int, city_data: dict, language: str, state: FSMContext):
        """Set user city from city data"""
        city_display = city_data["readable_name"].split(',')[0]  # Take just the city name
        
        # Update user
        await DatabaseManager.create_or_update_user(
            user_id, 
            city=city_display,
            city_lat=city_data["lat"],
            city_lon=city_data["lon"]
        )
        
        # Log action
        await DatabaseManager.log_action(user_id, "city_set", {"city": city_display})
        
        # Get updated user and show main menu
        user = await DatabaseManager.get_user(user_id)
        keyboard = await self.get_main_menu_keyboard(user, language)
        
        await message.answer(
            _("main_menu", language),
            reply_markup=keyboard
        )
        await state.set_state(BotStates.MAIN_MENU)
    
    async def show_city_selection(self, message: Message, cities: list, language: str, state: FSMContext):
        """Show city selection menu with country flags"""
        if language == "ru":
            selection_text = "🏙 Найдено несколько городов. Выберите нужный:"
        elif language == "uk":
            selection_text = "🏙 Знайдено кілька міст. Оберіть потрібне:"
        else:
            selection_text = "🏙 Multiple cities found. Please select the one you need:"
        
        buttons = []
        for i, city in enumerate(cities):
            city_text = f"{city['country_emoji']} {city['readable_name']}"
            buttons.append([(city_text, f"select_city_{i}")])
        
        # Add back button
        buttons.append([(_("back_to_menu", language), "main_menu")])
        
        keyboard = await self.create_inline_keyboard(buttons)
        
        # Store cities data in state
        await state.update_data(cities=cities)
        
        await message.answer(selection_text, reply_markup=keyboard)
        await state.set_state(BotStates.SELECTING_CITY)
    
    async def handle_city_selection_from_list(self, callback: CallbackQuery, state: FSMContext):
        """Handle selection from multiple cities"""
        user_id = callback.from_user.id
        
        # Apply throttling for settings
        if await self.is_throttled(user_id, 'settings'):
            await callback.answer()
            return
        
        user = await DatabaseManager.get_user(user_id)
        
        # If user doesn't exist, create with default language
        if not user:
            language = callback.from_user.language_code or "en"
            user = await DatabaseManager.create_or_update_user(user_id, language=language)
        
        language = user.language
        
        # Get city index from callback data
        city_index = int(callback.data.split("_")[2])  # select_city_0 -> 0
        
        # Get cities from state
        data = await state.get_data()
        cities = data.get("cities", [])
        
        if city_index < len(cities):
            city = cities[city_index]
            city_display = city["readable_name"].split(',')[0]  # Take just the city name
            
            # Update user
            await DatabaseManager.create_or_update_user(
                user_id, 
                city=city_display,
                city_lat=city["lat"],
                city_lon=city["lon"]
            )
            
            # Log action
            await DatabaseManager.log_action(user_id, "city_set", {"city": city_display})
            
            # Get updated user and show main menu
            user = await DatabaseManager.get_user(user_id)
            keyboard = await self.get_main_menu_keyboard(user, language)
            
            await callback.message.edit_text(
                _("main_menu", language),
                reply_markup=keyboard
            )
            await callback.answer(_("city_set", language, city=city_display))
            await state.set_state(BotStates.MAIN_MENU)
        else:
            await callback.answer(_("city_not_found", language))
    
    async def handle_time_input(self, message: Message, state: FSMContext):
        """Handle time input"""
        user_id = message.from_user.id
        user = await DatabaseManager.get_user(user_id)
        
        # If user doesn't exist, create with default language
        if not user:
            language = message.from_user.language_code or "en"
            user = await DatabaseManager.create_or_update_user(user_id, language=language)
        
        language = user.language
        time_str = message.text.strip()
        
        try:
            # Parse time
            hour, minute = map(int, time_str.split(':'))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                notification_time = time(hour, minute)
                
                # Update user
                await DatabaseManager.create_or_update_user(user_id, notification_time=notification_time)
                
                # Log action
                await DatabaseManager.log_action(user_id, "time_set", {"time": time_str})
                
                # Get updated user and show main menu
                user = await DatabaseManager.get_user(user_id)
                keyboard = await self.get_main_menu_keyboard(user, language)
                
                await message.answer(
                    _("main_menu", language),
                    reply_markup=keyboard
                )
                await state.set_state(BotStates.MAIN_MENU)
            else:
                await message.answer(_("invalid_time", language))
        except ValueError:
            await message.answer(_("invalid_time", language))
    
    def register_handlers(self):
        """Register all bot handlers"""
        # Command handlers
        self.dp.message.register(self.cmd_start, Command("start"))
        
        # Callback handlers
        self.dp.callback_query.register(
            self.handle_language_selection, 
            F.data.startswith("lang_")
        )
        self.dp.callback_query.register(
            self.handle_main_menu, 
            F.data == "main_menu"
        )
        self.dp.callback_query.register(
            self.handle_city_selection, 
            F.data.in_(["select_city", "enter_custom_city"]) | F.data.startswith("city_")
        )
        self.dp.callback_query.register(
            self.handle_time_selection, 
            F.data.in_(["select_time", "enter_custom_time"]) | F.data.startswith("time_")
        )
        self.dp.callback_query.register(
            self.handle_settings, 
            F.data.in_(["settings", "select_language", "my_status", "help"])
        )
        self.dp.callback_query.register(
            self.handle_notifications_toggle, 
            F.data == "toggle_notifications"
        )
        self.dp.callback_query.register(
            self.handle_weather_now, 
            F.data == "weather_now"
        )
        self.dp.callback_query.register(
            self.handle_hourly_forecast, 
            F.data == "hourly_forecast"
        )
        self.dp.callback_query.register(
            self.handle_daily_forecast, 
            F.data == "daily_forecast"
        )
        self.dp.callback_query.register(
            self.handle_city_selection_from_list, 
            F.data.startswith("select_city_")
        )
        
        # Text message handlers for states
        self.dp.message.register(
            self.handle_city_input, 
            StateFilter(BotStates.WAITING_CITY)
        )
        self.dp.message.register(
            self.handle_time_input, 
            StateFilter(BotStates.WAITING_TIME)
        )


# Global bot instance
weather_bot = WeatherBot()

from typing import Dict, Any
from config import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE


class Localization:
    def __init__(self):
        self.translations = {
            "en": {
                # Welcome and setup
                "welcome_choose_language": "🌍 Choose your language:",
                "welcome_message": "Hello! 👋 I'll help you get daily weather forecasts.\n\nUse the buttons below to navigate:",
                "language_changed": "Language changed to English! 🇺🇸",
                
                # Main menu
                "main_menu": "🏠 Main Menu",
                "my_city": "🏙 My city: {city}",
                "my_city_not_set": "🏙 Set city",
                "notification_time": "⏰ Time: {time}",
                "notifications_on": "🔔 Notifications: On",
                "notifications_off": "🔔 Notifications: Off",
                "weather_now": "🌤 Weather now",
                "settings": "⚙️ Settings",
                
                # City selection
                "select_city": "🏙 Select your city:",
                "enter_city": "✏️ Enter another city",
                "city_not_found": "❌ City not found. Please try again.",
                "city_set": "✅ City set to: {city}",
                "enter_city_name": "Please enter your city name:",
                
                # Time selection
                "select_time": "⏰ Select notification time:\n\n🌍 Time zone: Based on your city ({city})\n✅ You can set notifications for any time (e.g., 07:23, 08:47, 14:15)",
                "custom_time": "✏️ Custom time",
                "time_set": "✅ Notification time set to: {time}\n🌍 Time zone: {city} local time\n📅 Next notification: tomorrow at {time} ({city} time)",
                "enter_time": "Please enter time in HH:MM format.\n\n🌍 ⚠️ IMPORTANT: Time will be in {city} LOCAL TIME\n✅ You can use any time (e.g., 07:23, 08:47, 14:15, 19:42)",
                "invalid_time": "❌ Invalid time format. Please use HH:MM (e.g., 09:30)",
                "city_timezone_info": "🌍 Your notifications will arrive at {time} {city} local time",
                
                # Settings menu
                "settings_menu": "⚙️ Settings",
                "change_city": "🏙 Change city",
                "change_time": "⏰ Change time",
                "toggle_notifications": "🔔 Notifications: {status}",
                "language": "🌍 Language: English",
                "my_status": "📊 My status",
                "help": "❓ Help",
                
                # Status
                "status_info": """📊 Your Status:
🏙 City: {city}
⏰ Time: {time}
🔔 Notifications: {notifications}
🌍 Language: English
📅 Member since: {date}""",
                
                # Help
                "help_text": """❓ How to use the bot:

🏙 Set your city to get weather forecasts
⏰ Choose when you want to receive daily notifications
🔔 Enable/disable notifications as needed
🌤 Check current weather anytime

⚠️ Important about notifications:
• You can set notifications for any time (e.g., 07:23, 08:47, 14:15)
• Time is based on your city's local timezone
• Notifications are sent daily at your chosen time
• You can change the time anytime in settings

The bot will send you daily weather forecasts with clothing recommendations!""",
                
                # Weather forecast
                "weather_in": "🌤 Weather in {city} for {date}",
                "current_temp": "🌡 Now: {temp}°C (feels like {feels_like}°C)",
                "today_range": "📊 Today: {min}°C ... {max}°C",
                "humidity": "💧 Humidity: {humidity}%",
                "wind": "🌬 Wind: {speed} m/s",
                "rain_prob": "🌧 Rain probability: {prob}%",
                "recommendation": "👕 Recommendation: {advice}",
                "have_great_day": "Have a great day! ☀️",
                "refresh": "🔄 Refresh",
                "weather_error": "❌ Unable to get weather data. Please try again later.",
                
                # Hourly and daily forecast
                "hourly_forecast": "📅 Hourly forecast",
                "daily_forecast": "📆 Daily forecast",
                "select_day": "📅 Select day",
                "today": "Today",
                "tomorrow": "Tomorrow",
                "hourly_title": "🕐 Hourly forecast for {date}",
                "daily_title": "📅 {days}-day forecast",
                
                # Navigation
                "back": "← Back",
                "back_to_menu": "← Back to menu",
                
                # Notifications
                "notifications_enabled": "✅ Daily notifications enabled!",
                "notifications_disabled": "❌ Daily notifications disabled.",
                
                # Errors
                "error_occurred": "❌ An error occurred. Please try again.",
                "setup_required": "Please set up your city and notification time first.",
                
                # Cities
                "popular_cities": {
                    "new_york": "🇺🇸 New York",
                    "london": "🇬🇧 London", 
                    "berlin": "🇩🇪 Berlin",
                    "paris": "🇫🇷 Paris",
                    "tokyo": "🇯🇵 Tokyo",
                    "sydney": "🇦🇺 Sydney"
                },
                
                # Time slots
                "time_slots": {
                    "07:00": "🌅 07:00",
                    "08:00": "🌄 08:00",
                    "09:00": "☀️ 09:00",
                    "12:00": "🌞 12:00",
                    "18:00": "🌇 18:00",
                    "21:00": "🌃 21:00"
                }
            },
            
            "ru": {
                # Welcome and setup
                "welcome_choose_language": "🌍 Выберите язык / Choose your language:",
                "welcome_message": "Привет! 👋 Я помогу тебе получать ежедневный прогноз погоды.\n\nИспользуй кнопки ниже для управления:",
                "language_changed": "Язык изменен на русский! 🇷🇺",
                
                # Main menu
                "main_menu": "🏠 Главное меню",
                "my_city": "🏙 Мой город: {city}",
                "my_city_not_set": "🏙 Выбрать город",
                "notification_time": "⏰ Время: {time}",
                "notifications_on": "🔔 Уведомления: Вкл",
                "notifications_off": "🔔 Уведомления: Выкл",
                "weather_now": "🌤 Погода сейчас",
                "settings": "⚙️ Настройки",
                
                # City selection
                "select_city": "🏙 Выберите ваш город:",
                "enter_city": "✏️ Ввести другой город",
                "city_not_found": "❌ Город не найден. Попробуйте еще раз.",
                "city_set": "✅ Город установлен: {city}",
                "enter_city_name": "Пожалуйста, введите название вашего города:",
                
                # Time selection
                "select_time": "⏰ Выберите время уведомлений:\n\n🌍 Часовой пояс: По времени вашего города ({city})\n✅ Можно установить уведомления на любое время (например, 07:23, 08:47, 14:15)",
                "custom_time": "✏️ Другое время",
                "time_set": "✅ Время уведомлений установлено: {time}\n🌍 Часовой пояс: местное время {city}\n📅 Следующее уведомление: завтра в {time} (время {city})",
                "enter_time": "Пожалуйста, введите время в формате ЧЧ:ММ.\n\n🌍 ⚠️ ВАЖНО: Время будет по МЕСТНОМУ времени {city}\n✅ Можно использовать любое время (например, 07:23, 08:47, 14:15, 19:42)",
                "invalid_time": "❌ Неверный формат времени. Используйте ЧЧ:ММ (например, 09:30)",
                "city_timezone_info": "🌍 Ваши уведомления будут приходить в {time} по местному времени {city}",
                
                # Settings menu
                "settings_menu": "⚙️ Настройки",
                "change_city": "🏙 Изменить город",
                "change_time": "⏰ Изменить время",
                "toggle_notifications": "🔔 Уведомления: {status}",
                "language": "🌍 Язык: Русский",
                "my_status": "📊 Мой статус",
                "help": "❓ Помощь",
                
                # Status
                "status_info": """📊 Ваш статус:
🏙 Город: {city}
⏰ Время: {time}
🔔 Уведомления: {notifications}
🌍 Язык: Русский
📅 Участник с: {date}""",
                
                # Help
                "help_text": """❓ Как пользоваться ботом:

🏙 Установите ваш город для получения прогнозов погоды
⏰ Выберите время получения ежедневных уведомлений
🔔 Включайте/отключайте уведомления по необходимости
🌤 Проверяйте текущую погоду в любое время

⚠️ Важно про уведомления:
• Можно установить уведомления на любое время (например, 07:23, 08:47, 14:15)
• Время основано на местном времени вашего города
• Уведомления приходят каждый день в выбранное время
• Время можно изменить в любой момент в настройках

Бот будет отправлять вам ежедневные прогнозы погоды с рекомендациями по одежде!""",
                
                # Weather forecast
                "weather_in": "🌤 Погода в {city} на {date}",
                "current_temp": "🌡 Сейчас: {temp}°C (ощущается как {feels_like}°C)",
                "today_range": "📊 Сегодня: {min}°C ... {max}°C",
                "humidity": "💧 Влажность: {humidity}%",
                "wind": "🌬 Ветер: {speed} м/с",
                "rain_prob": "🌧 Вероятность дождя: {prob}%",
                "recommendation": "👕 Рекомендация: {advice}",
                "have_great_day": "Хорошего дня! ☀️",
                "refresh": "🔄 Обновить",
                "weather_error": "❌ Не удалось получить данные о погоде. Попробуйте позже.",
                
                # Hourly and daily forecast
                "hourly_forecast": "📅 Почасовой прогноз",
                "daily_forecast": "📆 Прогноз по дням",
                "select_day": "📅 Выбрать день",
                "today": "Сегодня",
                "tomorrow": "Завтра",
                "hourly_title": "🕐 Почасовой прогноз на {date}",
                "daily_title": "📅 Прогноз на {days} дней",
                
                # Navigation
                "back": "← Назад",
                "back_to_menu": "← Назад в меню",
                
                # Notifications
                "notifications_enabled": "✅ Ежедневные уведомления включены!",
                "notifications_disabled": "❌ Ежедневные уведомления отключены.",
                
                # Errors
                "error_occurred": "❌ Произошла ошибка. Попробуйте еще раз.",
                "setup_required": "Пожалуйста, сначала настройте ваш город и время уведомлений.",
                
                # Cities
                "popular_cities": {
                    "new_york": "🇺🇸 Нью-Йорк",
                    "london": "🇬🇧 Лондон",
                    "berlin": "🇩🇪 Берлин",
                    "paris": "🇫🇷 Париж",
                    "tokyo": "🇯🇵 Токио",
                    "sydney": "🇦🇺 Сидней"
                },
                
                # Time slots
                "time_slots": {
                    "07:00": "🌅 07:00",
                    "08:00": "🌄 08:00",
                    "09:00": "☀️ 09:00",
                    "12:00": "🌞 12:00",
                    "18:00": "🌇 18:00",
                    "21:00": "🌃 21:00"
                }
            },
            
            "uk": {
                # Welcome and setup
                "welcome_choose_language": "🌍 Оберіть мову / Choose your language:",
                "welcome_message": "Привіт! 👋 Я допоможу тобі отримувати щоденний прогноз погоди.\n\nВикористовуй кнопки нижче для керування:",
                "language_changed": "Мову змінено на українську! 🇺🇦",
                
                # Main menu
                "main_menu": "🏠 Головне меню",
                "my_city": "🏙 Моє місто: {city}",
                "my_city_not_set": "🏙 Обрати місто",
                "notification_time": "⏰ Час: {time}",
                "notifications_on": "🔔 Сповіщення: Увімк",
                "notifications_off": "🔔 Сповіщення: Вимк",
                "weather_now": "🌤 Погода зараз",
                "settings": "⚙️ Налаштування",
                
                # City selection
                "select_city": "🏙 Оберіть ваше місто:",
                "enter_city": "✏️ Ввести інше місто",
                "city_not_found": "❌ Місто не знайдено. Спробуйте ще раз.",
                "city_set": "✅ Місто встановлено: {city}",
                "enter_city_name": "Будь ласка, введіть назву вашого міста:",
                
                # Time selection
                "select_time": "⏰ Оберіть час сповіщень:\n\n🌍 Часовий пояс: За часом вашого міста ({city})\n✅ Можна встановити сповіщення на будь-який час (наприклад, 07:23, 08:47, 14:15)",
                "custom_time": "✏️ Інший час",
                "time_set": "✅ Час сповіщень встановлено: {time}\n🌍 Часовий пояс: місцевий час {city}\n📅 Наступне сповіщення: завтра о {time} (час {city})",
                "enter_time": "Будь ласка, введіть час у форматі ГГ:ХХ.\n\n🌍 ⚠️ ВАЖЛИВО: Час буде за МІСЦЕВИМ часом {city}\n✅ Можна використовувати будь-який час (наприклад, 07:23, 08:47, 14:15, 19:42)",
                "invalid_time": "❌ Невірний формат часу. Використовуйте ГГ:ХХ (наприклад, 09:30)",
                "city_timezone_info": "🌍 Ваші сповіщення будуть приходити о {time} за місцевим часом {city}",
                
                # Settings menu
                "settings_menu": "⚙️ Налаштування",
                "change_city": "🏙 Змінити місто",
                "change_time": "⏰ Змінити час",
                "toggle_notifications": "🔔 Сповіщення: {status}",
                "language": "🌍 Мова: Українська",
                "my_status": "📊 Мій статус",
                "help": "❓ Допомога",
                
                # Status
                "status_info": """📊 Ваш статус:
🏙 Місто: {city}
⏰ Час: {time}
🔔 Сповіщення: {notifications}
🌍 Мова: Українська
📅 Учасник з: {date}""",
                
                # Help
                "help_text": """❓ Як користуватися ботом:

🏙 Встановіть ваше місто для отримання прогнозів погоди
⏰ Оберіть час отримання щоденних сповіщень
🔔 Вмикайте/вимикайте сповіщення за потребою
🌤 Перевіряйте поточну погоду в будь-який час

⚠️ Важливо про сповіщення:
• Можна встановити сповіщення на будь-який час (наприклад, 07:23, 08:47, 14:15)
• Час базується на місцевому часі вашого міста
• Сповіщення приходять щодня в обраний час
• Час можна змінити в будь-який момент в налаштуваннях

Бот буде надсилати вам щоденні прогнози погоди з рекомендаціями по одязі!""",
                
                # Weather forecast
                "weather_in": "🌤 Погода в {city} на {date}",
                "current_temp": "🌡 Зараз: {temp}°C (відчувається як {feels_like}°C)",
                "today_range": "📊 Сьогодні: {min}°C ... {max}°C",
                "humidity": "💧 Вологість: {humidity}%",
                "wind": "🌬 Вітер: {speed} м/с",
                "rain_prob": "🌧 Ймовірність дощу: {prob}%",
                "recommendation": "👕 Рекомендація: {advice}",
                "have_great_day": "Гарного дня! ☀️",
                "refresh": "🔄 Оновити",
                "weather_error": "❌ Не вдалося отримати дані про погоду. Спробуйте пізніше.",
                
                # Hourly and daily forecast
                "hourly_forecast": "📅 Погодинний прогноз",
                "daily_forecast": "📆 Прогноз по днях",
                "select_day": "📅 Обрати день",
                "today": "Сьогодні",
                "tomorrow": "Завтра",
                "hourly_title": "🕐 Погодинний прогноз на {date}",
                "daily_title": "📅 Прогноз на {days} днів",
                
                # Navigation
                "back": "← Назад",
                "back_to_menu": "← Назад в меню",
                
                # Notifications
                "notifications_enabled": "✅ Щоденні сповіщення увімкнено!",
                "notifications_disabled": "❌ Щоденні сповіщення вимкнено.",
                
                # Errors
                "error_occurred": "❌ Сталася помилка. Спробуйте ще раз.",
                "setup_required": "Будь ласка, спочатку налаштуйте ваше місто та час сповіщень.",
                
                # Cities
                "popular_cities": {
                    "new_york": "🇺🇸 Нью-Йорк",
                    "london": "🇬🇧 Лондон",
                    "berlin": "🇩🇪 Берлін",
                    "paris": "🇫🇷 Париж",
                    "tokyo": "🇯🇵 Токіо",
                    "sydney": "🇦🇺 Сідней"
                },
                
                # Time slots
                "time_slots": {
                    "07:00": "🌅 07:00",
                    "08:00": "🌄 08:00",
                    "09:00": "☀️ 09:00",
                    "12:00": "🌞 12:00",
                    "18:00": "🌇 18:00",
                    "21:00": "🌃 21:00"
                }
            }
        }
    
    def get_text(self, key: str, language: str = DEFAULT_LANGUAGE, **kwargs) -> str:
        """Get localized text by key"""
        if language not in SUPPORTED_LANGUAGES:
            language = DEFAULT_LANGUAGE
        
        # Navigate through nested keys (e.g., "popular_cities.moscow")
        keys = key.split('.')
        text = self.translations.get(language, self.translations[DEFAULT_LANGUAGE])
        
        for k in keys:
            if isinstance(text, dict) and k in text:
                text = text[k]
            else:
                # Fallback to default language
                text = self.translations[DEFAULT_LANGUAGE]
                for fallback_k in keys:
                    if isinstance(text, dict) and fallback_k in text:
                        text = text[fallback_k]
                    else:
                        return f"Missing translation: {key}"
                break
        
        # Format with provided kwargs
        if isinstance(text, str) and kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                return text
        
        return text if isinstance(text, str) else str(text)
    
    def get_language_keyboard(self):
        """Get language selection keyboard"""
        return [
            [("🇺🇸 English", "lang_en"), ("🇷🇺 Русский", "lang_ru"), ("🇺🇦 Українська", "lang_uk")]
        ]
    
    def get_popular_cities(self, language: str):
        """Get popular cities for the language"""
        cities = self.translations.get(language, {}).get("popular_cities", {})
        if language == "ru":
            return [
                [("🇺🇸 Нью-Йорк", "city_New York"), ("🇬🇧 Лондон", "city_London")],
                [("🇩🇪 Берлин", "city_Berlin"), ("🇫🇷 Париж", "city_Paris")],
                [("🇯🇵 Токио", "city_Tokyo"), ("🇦🇺 Сидней", "city_Sydney")]
            ]
        else:
            return [
                [("🇺🇸 New York", "city_New York"), ("🇬🇧 London", "city_London")],
                [("🇩🇪 Berlin", "city_Berlin"), ("🇫🇷 Paris", "city_Paris")],
                [("🇯🇵 Tokyo", "city_Tokyo"), ("🇦🇺 Sydney", "city_Sydney")]
            ]
    
    def get_time_slots(self, language: str):
        """Get time slot buttons"""
        return [
            [("🌅 07:00", "time_07:00"), ("🌄 08:00", "time_08:00"), ("☀️ 09:00", "time_09:00")],
            [("🌞 12:00", "time_12:00"), ("🌇 18:00", "time_18:00"), ("🌃 21:00", "time_21:00")]
        ]


# Global localization instance
localization = Localization()


def get_user_language(user_data: dict) -> str:
    """Get user's language from user data"""
    return user_data.get("language", DEFAULT_LANGUAGE)


def _(key: str, language: str = DEFAULT_LANGUAGE, **kwargs) -> str:
    """Shorthand function for getting localized text"""
    return localization.get_text(key, language, **kwargs)

import httpx
import asyncio
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging
from config import OPEN_METEO_URL, LOCATIONIQ_URL, WEATHER_API_URL, settings
from database import DatabaseManager

logger = logging.getLogger(__name__)


class WeatherAPI:
    def __init__(self):
        # Увеличиваем таймаут и добавляем retry логику
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        self.cache = {}
        self._last_locationiq_request = 0
        
    async def close(self):
        await self.client.aclose()
    
    async def get_city_coordinates(self, city_name: str) -> Optional[Tuple[float, float, str]]:
        """Get city coordinates using LocationIQ API with caching (single result)"""
        results = await self.search_cities(city_name, limit=1)
        if results:
            city = results[0]
            return city["lat"], city["lon"], city["display_name"]
        return None
    
    async def search_cities(self, city_name: str, limit: int = 5) -> list:
        """Search for multiple cities with the same name"""
        try:
            # Check cache first for matches
            cached_cities = await DatabaseManager.get_cached_cities(city_name)
            if cached_cities:
                cached_results = []
                for cached_city in cached_cities:
                    cached_results.append({
                        "lat": float(cached_city.latitude),
                        "lon": float(cached_city.longitude),
                        "display_name": cached_city.display_name,
                        "country": cached_city.country,
                        "country_emoji": self._get_country_emoji(cached_city.country)
                    })
                
                # If we have enough cached results, return them
                if len(cached_results) >= limit:
                    return cached_results[:limit]
                
                # If we only need one result and have cached data, return it
                if limit == 1 and cached_results:
                    return cached_results[:1]
            
            # Try fallback city search first (faster and more reliable)
            fallback_result = await self._search_cities_fallback(city_name)
            if fallback_result:
                return [fallback_result]
            
            # Rate limiting для LocationIQ
            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - self._last_locationiq_request
            if time_since_last < 1.0:
                await asyncio.sleep(1.0 - time_since_last)
            
            self._last_locationiq_request = asyncio.get_event_loop().time()
            
            # LocationIQ требует API ключ
            if not settings.locationiq_api_key:
                logger.warning("LocationIQ API key not set, using fallback")
                return await self._search_cities_builtin(city_name, limit)
            
            params = {
                "key": settings.locationiq_api_key,
                "q": city_name,
                "format": "json",
                "limit": limit,
                "addressdetails": 1,
                "accept-language": "en,ru,uk"
            }
            
            headers = {
                "User-Agent": "WeatherBot/1.0 (https://github.com/PLTMisha/weather-bot)"
            }
            
            # Добавляем retry логику
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = await self.client.get(
                        LOCATIONIQ_URL, 
                        params=params, 
                        headers=headers
                    )
                    response.raise_for_status()
                    break
                except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError) as e:
                    if attempt == max_retries - 1:
                        logger.error(f"LocationIQ API unavailable, using fallback: {e}")
                        # Используем встроенную базу городов
                        return await self._search_cities_builtin(city_name, limit)
                    
                    wait_time = 2
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
            
            data = response.json()
            if not data:
                logger.warning(f"No results found for city: {city_name}, trying fallback")
                return await self._search_cities_builtin(city_name, limit)
            
            cities = []
            for result in data:
                try:
                    lat = float(result["lat"])
                    lon = float(result["lon"])
                    display_name = result["display_name"]
                    address = result.get("address", {})
                    country = address.get("country", "")
                    state = address.get("state", "")
                    
                    # Create a more readable display name
                    city_display = result.get("name", city_name)
                    location_parts = []
                    
                    if state and state != country:
                        location_parts.append(state)
                    if country:
                        location_parts.append(country)
                    
                    readable_name = f"{city_display}"
                    if location_parts:
                        readable_name += f", {', '.join(location_parts)}"
                    
                    city_info = {
                        "lat": lat,
                        "lon": lon,
                        "display_name": display_name,
                        "readable_name": readable_name,
                        "country": country,
                        "state": state,
                        "country_emoji": self._get_country_emoji(country)
                    }
                    
                    cities.append(city_info)
                    
                    # Cache each city result
                    try:
                        await DatabaseManager.cache_city(city_name, lat, lon, country, display_name)
                    except Exception as cache_error:
                        # Log but don't fail if caching fails (might be duplicate)
                        logger.debug(f"Cache error for {city_display}: {cache_error}")
                        
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error processing city result: {e}")
                    continue
            
            logger.info(f"Found {len(cities)} cities for '{city_name}'")
            return cities
            
        except Exception as e:
            logger.error(f"Error searching cities: {e}")
            # Fallback to built-in city database
            return await self._search_cities_builtin(city_name, limit)
    
    def _get_weather_emoji(self, weather_code: int) -> str:
        """Get weather emoji based on weather code"""
        weather_emojis = {
            0: "☀️",    # Clear sky
            1: "🌤",    # Mainly clear
            2: "⛅",    # Partly cloudy
            3: "☁️",    # Overcast
            45: "🌫",   # Fog
            48: "🌫",   # Depositing rime fog
            51: "🌦",   # Light drizzle
            53: "🌦",   # Moderate drizzle
            55: "🌧",   # Dense drizzle
            56: "🌨",   # Light freezing drizzle
            57: "🌨",   # Dense freezing drizzle
            61: "🌧",   # Slight rain
            63: "🌧",   # Moderate rain
            65: "🌧",   # Heavy rain
            66: "🌨",   # Light freezing rain
            67: "🌨",   # Heavy freezing rain
            71: "❄️",   # Slight snow fall
            73: "🌨",   # Moderate snow fall
            75: "❄️",   # Heavy snow fall
            77: "❄️",   # Snow grains
            80: "🌦",   # Slight rain showers
            81: "🌧",   # Moderate rain showers
            82: "⛈",    # Violent rain showers
            85: "🌨",   # Slight snow showers
            86: "❄️",   # Heavy snow showers
            95: "⛈",    # Thunderstorm
            96: "⛈",    # Thunderstorm with slight hail
            99: "⛈"     # Thunderstorm with heavy hail
        }
        
        return weather_emojis.get(weather_code, "🌤")  # Default weather emoji
    
    def _get_country_emoji(self, country: str) -> str:
        """Get country flag emoji based on country name"""
        country_emojis = {
            # Major countries (English names)
            "United States": "🇺🇸",
            "United States of America": "🇺🇸",
            "USA": "🇺🇸",
            "United Kingdom": "🇬🇧",
            "UK": "🇬🇧",
            "Great Britain": "🇬🇧",
            "England": "🇬🇧",
            "Scotland": "🇬🇧",
            "Wales": "🇬🇧",
            "Northern Ireland": "🇬🇧",
            "Canada": "🇨🇦",
            "Australia": "🇦🇺",
            "Germany": "🇩🇪",
            "Deutschland": "🇩🇪",
            "France": "🇫🇷",
            "Italy": "🇮🇹",
            "Italia": "🇮🇹",
            "Spain": "🇪🇸",
            "España": "🇪🇸",
            "Netherlands": "🇳🇱",
            "Nederland": "🇳🇱",
            "Belgium": "🇧🇪",
            "België": "🇧🇪",
            "Belgique": "🇧🇪",
            "Switzerland": "🇨🇭",
            "Schweiz": "🇨🇭",
            "Suisse": "🇨🇭",
            "Svizzera": "🇨🇭",
            "Austria": "🇦🇹",
            "Österreich": "🇦🇹",
            "Sweden": "🇸🇪",
            "Sverige": "🇸🇪",
            "Norway": "🇳🇴",
            "Norge": "🇳🇴",
            "Denmark": "🇩🇰",
            "Danmark": "🇩🇰",
            "Finland": "🇫🇮",
            "Suomi": "🇫🇮",
            "Poland": "🇵🇱",
            "Polska": "🇵🇱",
            "Czech Republic": "🇨🇿",
            "Czechia": "🇨🇿",
            "Česká republika": "🇨🇿",
            "Hungary": "🇭🇺",
            "Magyarország": "🇭🇺",
            "Greece": "🇬🇷",
            "Ελλάδα": "🇬🇷",
            "Portugal": "🇵🇹",
            "Ireland": "🇮🇪",
            "Éire": "🇮🇪",
            "Japan": "🇯🇵",
            "日本": "🇯🇵",
            "China": "🇨🇳",
            "中国": "🇨🇳",
            "South Korea": "🇰🇷",
            "Korea": "🇰🇷",
            "대한민국": "🇰🇷",
            "India": "🇮🇳",
            "भारत": "🇮🇳",
            "Brazil": "🇧🇷",
            "Brasil": "🇧🇷",
            "Mexico": "🇲🇽",
            "México": "🇲🇽",
            "Argentina": "🇦🇷",
            "Chile": "🇨🇱",
            "South Africa": "🇿🇦",
            "Egypt": "🇪🇬",
            "مصر": "🇪🇬",
            "Turkey": "🇹🇷",
            "Türkiye": "🇹🇷",
            "Israel": "🇮🇱",
            "ישראל": "🇮🇱",
            "Thailand": "🇹🇭",
            "ประเทศไทย": "🇹🇭",
            "Singapore": "🇸🇬",
            "Malaysia": "🇲🇾",
            "Indonesia": "🇮🇩",
            "Philippines": "🇵🇭",
            "Vietnam": "🇻🇳",
            "Việt Nam": "🇻🇳",
            "New Zealand": "🇳🇿",
            "New Zealand / Aotearoa": "🇳🇿",
            
            # CIS and Eastern Europe (multiple language variants)
            "Russia": "🇷🇺",
            "Russian Federation": "🇷🇺",
            "Россия": "🇷🇺",
            "Российская Федерация": "🇷🇺",
            "Ukraine": "🇺🇦",
            "Україна": "🇺🇦",
            "Belarus": "🇧🇾",
            "Беларусь": "🇧🇾",
            "Белоруссия": "🇧🇾",
            "Kazakhstan": "🇰🇿",
            "Казахстан": "🇰🇿",
            "Қазақстан": "🇰🇿",
            "Uzbekistan": "🇺🇿",
            "Ўзбекистон": "🇺🇿",
            "Узбекистан": "🇺🇿",
            "Kyrgyzstan": "🇰🇬",
            "Кыргызстан": "🇰🇬",
            "Киргизия": "🇰🇬",
            "Tajikistan": "🇹🇯",
            "Тоҷикистон": "🇹🇯",
            "Таджикистан": "🇹🇯",
            "Turkmenistan": "🇹🇲",
            "Türkmenistan": "🇹🇲",
            "Туркменистан": "🇹🇲",
            "Azerbaijan": "🇦🇿",
            "Azərbaycan": "🇦🇿",
            "Азербайджан": "🇦🇿",
            "Armenia": "🇦🇲",
            "Հայաստան": "🇦🇲",
            "Армения": "🇦🇲",
            "Georgia": "🇬🇪",
            "საქართველო": "🇬🇪",
            "Грузия": "🇬🇪",
            "Moldova": "🇲🇩",
            "Молдова": "🇲🇩",
            "Lithuania": "🇱🇹",
            "Lietuva": "🇱🇹",
            "Литва": "🇱🇹",
            "Latvia": "🇱🇻",
            "Latvija": "🇱🇻",
            "Латвия": "🇱🇻",
            "Estonia": "🇪🇪",
            "Eesti": "🇪🇪",
            "Эстония": "🇪🇪",
            "Romania": "🇷🇴",
            "România": "🇷🇴",
            "Румыния": "🇷🇴",
            "Bulgaria": "🇧🇬",
            "България": "🇧🇬",
            "Болгария": "🇧🇬",
            "Serbia": "🇷🇸",
            "Србија": "🇷🇸",
            "Сербия": "🇷🇸",
            "Croatia": "🇭🇷",
            "Hrvatska": "🇭🇷",
            "Хорватия": "🇭🇷",
            "Slovenia": "🇸🇮",
            "Slovenija": "🇸🇮",
            "Словения": "🇸🇮",
            "Bosnia and Herzegovina": "🇧🇦",
            "Bosna i Hercegovina": "🇧🇦",
            "Босния и Герцеговина": "🇧🇦",
            "Montenegro": "🇲🇪",
            "Crna Gora": "🇲🇪",
            "Черногория": "🇲🇪",
            "North Macedonia": "🇲🇰",
            "Северна Македонија": "🇲🇰",
            "Северная Македония": "🇲🇰",
            "Albania": "🇦🇱",
            "Shqipëria": "🇦🇱",
            "Албания": "🇦🇱",
            "Kosovo": "🇽🇰",
            "Kosova": "🇽🇰",
            "Косово": "🇽🇰",
            
            # Middle East
            "Saudi Arabia": "🇸🇦",
            "المملكة العربية السعودية": "🇸🇦",
            "United Arab Emirates": "🇦🇪",
            "الإمارات العربية المتحدة": "🇦🇪",
            "UAE": "🇦🇪",
            "Qatar": "🇶🇦",
            "قطر": "🇶🇦",
            "Kuwait": "🇰🇼",
            "الكويت": "🇰🇼",
            "Bahrain": "🇧🇭",
            "البحرين": "🇧🇭",
            "Oman": "🇴🇲",
            "عُمان": "🇴🇲",
            "Jordan": "🇯🇴",
            "الأردن": "🇯🇴",
            "Lebanon": "🇱🇧",
            "لبنان": "🇱🇧",
            "Syria": "🇸🇾",
            "سوريا": "🇸🇾",
            "Iraq": "🇮🇶",
            "العراق": "🇮🇶",
            "Iran": "🇮🇷",
            "ایران": "🇮🇷",
            "Afghanistan": "🇦🇫",
            "افغانستان": "🇦🇫",
            "Pakistan": "🇵🇰",
            "پاکستان": "🇵🇰",
            
            # Africa
            "Nigeria": "🇳🇬",
            "Kenya": "🇰🇪",
            "Ghana": "🇬🇭",
            "Morocco": "🇲🇦",
            "المغرب": "🇲🇦",
            "Algeria": "🇩🇿",
            "الجزائر": "🇩🇿",
            "Tunisia": "🇹🇳",
            "تونس": "🇹🇳",
            "Libya": "🇱🇾",
            "ليبيا": "🇱🇾",
            "Ethiopia": "🇪🇹",
            "Tanzania": "🇹🇿",
            "Uganda": "🇺🇬",
            
            # Additional European countries
            "Iceland": "🇮🇸",
            "Ísland": "🇮🇸",
            "Исландия": "🇮🇸",
            "Luxembourg": "🇱🇺",
            "Lëtzebuerg": "🇱🇺",
            "Люксембург": "🇱🇺",
            "Malta": "🇲🇹",
            "Мальта": "🇲🇹",
            "Cyprus": "🇨🇾",
            "Κύπρος": "🇨🇾",
            "Кипр": "🇨🇾",
            "Monaco": "🇲🇨",
            "Монако": "🇲🇨",
            "San Marino": "🇸🇲",
            "Сан-Марино": "🇸🇲",
            "Vatican City": "🇻🇦",
            "Ватикан": "🇻🇦",
            "Andorra": "🇦🇩",
            "Андорра": "🇦🇩",
            "Liechtenstein": "🇱🇮",
            "Лихтенштейн": "🇱🇮",
            
            # More countries can be added as needed
        }
        
        return country_emojis.get(country, "🌍")  # Default globe emoji
    
    async def get_weather_forecast(self, latitude: float, longitude: float, 
                                 language: str = "en", days: int = 1) -> Optional[Dict]:
        """Get weather forecast using Open-Meteo API"""
        try:
            cache_key = f"{latitude}_{longitude}_{language}_{days}"
            
            # Check cache (30 minutes TTL)
            if cache_key in self.cache:
                cached_time, cached_data = self.cache[cache_key]
                if datetime.now() - cached_time < timedelta(minutes=30):
                    return cached_data
            
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "daily": "temperature_2m_max,temperature_2m_min,weathercode,precipitation_probability_max",
                "hourly": "temperature_2m,relative_humidity_2m,windspeed_10m,weathercode",
                "current_weather": True,
                "timezone": "auto",
                "forecast_days": min(days, 7)  # Max 7 days
            }
            
            response = await self.client.get(OPEN_METEO_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Process and format the data
            weather_data = self._process_weather_data(data, language, days)
            
            # Cache the result
            self.cache[cache_key] = (datetime.now(), weather_data)
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Error getting weather forecast: {e}")
            # Try fallback API if available
            return await self._get_weather_fallback(latitude, longitude, language)
    
    def _process_weather_data(self, data: Dict, language: str, days: int = 1) -> Dict:
        """Process raw weather data into user-friendly format"""
        current = data.get("current_weather", {})
        daily = data.get("daily", {})
        hourly = data.get("hourly", {})
        
        # Get current hour index
        current_time = datetime.now()
        current_hour_index = current_time.hour
        
        # Weather code mapping
        weather_codes = self._get_weather_codes(language)
        
        current_weather_code = current.get("weathercode", 0)
        current_description = weather_codes.get(current_weather_code, "Unknown")
        
        # Get today's data
        today_max = daily.get("temperature_2m_max", [0])[0] if daily.get("temperature_2m_max") else current.get("temperature", 0)
        today_min = daily.get("temperature_2m_min", [0])[0] if daily.get("temperature_2m_min") else current.get("temperature", 0)
        rain_probability = daily.get("precipitation_probability_max", [0])[0] if daily.get("precipitation_probability_max") else 0
        
        # Get current hour data if available
        humidity = 50  # default
        wind_speed = current.get("windspeed", 0)
        
        if hourly.get("relative_humidity_2m") and len(hourly["relative_humidity_2m"]) > current_hour_index:
            humidity = hourly["relative_humidity_2m"][current_hour_index]
        
        if hourly.get("windspeed_10m") and len(hourly["windspeed_10m"]) > current_hour_index:
            wind_speed = hourly["windspeed_10m"][current_hour_index]
        
        # Calculate feels like temperature (simple approximation)
        current_temp = current.get("temperature", 0)
        feels_like = self._calculate_feels_like(current_temp, humidity, wind_speed)
        
        # Process hourly data for today
        hourly_forecast = []
        if hourly.get("time") and hourly.get("temperature_2m"):
            times = hourly["time"]
            temperatures = hourly["temperature_2m"]
            weather_codes_hourly = hourly.get("weathercode", [])
            
            for i, time_str in enumerate(times[:24]):  # Today's 24 hours
                if i < len(temperatures):
                    hour_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    weather_code = weather_codes_hourly[i] if i < len(weather_codes_hourly) else 0
                    description = weather_codes.get(weather_code, "Unknown")
                    
                    hourly_forecast.append({
                        "time": hour_time.strftime("%H:%M"),
                        "temperature": round(temperatures[i]),
                        "description": description,
                        "weather_code": weather_code
                    })
        
        # Process daily data for multiple days
        daily_forecast = []
        if daily.get("time") and daily.get("temperature_2m_max"):
            times = daily["time"]
            max_temps = daily["temperature_2m_max"]
            min_temps = daily.get("temperature_2m_min", [])
            weather_codes_daily = daily.get("weathercode", [])
            rain_probs = daily.get("precipitation_probability_max", [])
            
            for i, date_str in enumerate(times[:days]):
                if i < len(max_temps):
                    date_obj = datetime.fromisoformat(date_str)
                    weather_code = weather_codes_daily[i] if i < len(weather_codes_daily) else 0
                    description = weather_codes.get(weather_code, "Unknown")
                    
                    daily_forecast.append({
                        "date": date_obj.strftime("%Y-%m-%d"),
                        "date_display": date_obj.strftime("%d.%m"),
                        "day_name": self._get_day_name(date_obj, language),
                        "max_temperature": round(max_temps[i]),
                        "min_temperature": round(min_temps[i]) if i < len(min_temps) else round(max_temps[i]),
                        "description": description,
                        "rain_probability": round(rain_probs[i]) if i < len(rain_probs) else 0,
                        "weather_code": weather_code
                    })
        
        return {
            "current_temperature": round(current_temp),
            "feels_like": round(feels_like),
            "min_temperature": round(today_min),
            "max_temperature": round(today_max),
            "description": current_description,
            "humidity": round(humidity),
            "wind_speed": round(wind_speed),
            "rain_probability": round(rain_probability),
            "weather_code": current_weather_code,
            "hourly_forecast": hourly_forecast,
            "daily_forecast": daily_forecast
        }
    
    def _get_day_name(self, date_obj: datetime, language: str) -> str:
        """Get day name in specified language"""
        if language == "ru":
            days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        elif language == "uk":
            days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
        else:
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        return days[date_obj.weekday()]
    
    def _calculate_feels_like(self, temp: float, humidity: float, wind_speed: float) -> float:
        """Simple feels-like temperature calculation"""
        # Heat index for warm weather
        if temp >= 27:
            heat_index = temp + 0.5 * (humidity - 50) / 10
            return heat_index
        
        # Wind chill for cold weather
        if temp <= 10 and wind_speed > 5:
            wind_chill = temp - (wind_speed * 0.5)
            return wind_chill
        
        return temp
    
    def _get_weather_codes(self, language: str) -> Dict[int, str]:
        """Get weather code descriptions in specified language"""
        if language == "ru":
            return {
                0: "Ясно",
                1: "В основном ясно",
                2: "Переменная облачность",
                3: "Пасмурно",
                45: "Туман",
                48: "Изморозь",
                51: "Легкая морось",
                53: "Умеренная морось",
                55: "Сильная морось",
                56: "Ледяная морось",
                57: "Сильная ледяная морось",
                61: "Легкий дождь",
                63: "Умеренный дождь",
                65: "Сильный дождь",
                66: "Ледяной дождь",
                67: "Сильный ледяной дождь",
                71: "Легкий снег",
                73: "Умеренный снег",
                75: "Сильный снег",
                77: "Снежные зерна",
                80: "Легкие ливни",
                81: "Умеренные ливни",
                82: "Сильные ливни",
                85: "Легкие снежные ливни",
                86: "Сильные снежные ливни",
                95: "Гроза",
                96: "Гроза с градом",
                99: "Сильная гроза с градом"
            }
        elif language == "uk":
            return {
                0: "Ясно",
                1: "В основному ясно",
                2: "Мінлива хмарність",
                3: "Похмуро",
                45: "Туман",
                48: "Паморозь",
                51: "Легка мряка",
                53: "Помірна мряка",
                55: "Сильна мряка",
                56: "Крижана мряка",
                57: "Сильна крижана мряка",
                61: "Легкий дощ",
                63: "Помірний дощ",
                65: "Сильний дощ",
                66: "Крижаний дощ",
                67: "Сильний крижаний дощ",
                71: "Легкий сніг",
                73: "Помірний сніг",
                75: "Сильний сніг",
                77: "Снігові зерна",
                80: "Легкі зливи",
                81: "Помірні зливи",
                82: "Сильні зливи",
                85: "Легкі снігові зливи",
                86: "Сильні снігові зливи",
                95: "Гроза",
                96: "Гроза з градом",
                99: "Сильна гроза з градом"
            }
        else:  # English
            return {
                0: "Clear sky",
                1: "Mainly clear",
                2: "Partly cloudy",
                3: "Overcast",
                45: "Fog",
                48: "Depositing rime fog",
                51: "Light drizzle",
                53: "Moderate drizzle",
                55: "Dense drizzle",
                56: "Light freezing drizzle",
                57: "Dense freezing drizzle",
                61: "Slight rain",
                63: "Moderate rain",
                65: "Heavy rain",
                66: "Light freezing rain",
                67: "Heavy freezing rain",
                71: "Slight snow fall",
                73: "Moderate snow fall",
                75: "Heavy snow fall",
                77: "Snow grains",
                80: "Slight rain showers",
                81: "Moderate rain showers",
                82: "Violent rain showers",
                85: "Slight snow showers",
                86: "Heavy snow showers",
                95: "Thunderstorm",
                96: "Thunderstorm with slight hail",
                99: "Thunderstorm with heavy hail"
            }
    
    async def _get_weather_fallback(self, latitude: float, longitude: float, 
                                  language: str) -> Optional[Dict]:
        """Fallback weather API (WeatherAPI.com)"""
        if not settings.weather_api_key:
            return None
            
        try:
            params = {
                "key": settings.weather_api_key,
                "q": f"{latitude},{longitude}",
                "days": 1,
                "aqi": "no",
                "alerts": "no"
            }
            
            response = await self.client.get(f"{WEATHER_API_URL}/forecast.json", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Process WeatherAPI.com data
            current = data.get("current", {})
            forecast = data.get("forecast", {}).get("forecastday", [{}])[0]
            day_data = forecast.get("day", {})
            
            return {
                "current_temperature": round(current.get("temp_c", 0)),
                "feels_like": round(current.get("feelslike_c", 0)),
                "min_temperature": round(day_data.get("mintemp_c", 0)),
                "max_temperature": round(day_data.get("maxtemp_c", 0)),
                "description": current.get("condition", {}).get("text", "Unknown"),
                "humidity": current.get("humidity", 50),
                "wind_speed": round(current.get("wind_kph", 0) / 3.6),  # Convert to m/s
                "rain_probability": day_data.get("daily_chance_of_rain", 0),
                "weather_code": 0  # Default code
            }
            
        except Exception as e:
            logger.error(f"Fallback weather API error: {e}")
            return None
    
    async def _search_cities_fallback(self, city_name: str) -> Optional[Dict]:
        """Fallback city search using WeatherAPI.com"""
        if not settings.weather_api_key:
            return None
            
        try:
            params = {
                "key": settings.weather_api_key,
                "q": city_name,
                "aqi": "no"
            }
            
            response = await self.client.get(f"{WEATHER_API_URL}/current.json", params=params)
            response.raise_for_status()
            
            data = response.json()
            location = data.get("location", {})
            
            if location:
                return {
                    "lat": location.get("lat", 0),
                    "lon": location.get("lon", 0),
                    "display_name": f"{location.get('name', city_name)}, {location.get('country', '')}",
                    "readable_name": f"{location.get('name', city_name)}, {location.get('country', '')}",
                    "country": location.get("country", ""),
                    "state": location.get("region", ""),
                    "country_emoji": self._get_country_emoji(location.get("country", ""))
                }
        except Exception as e:
            logger.debug(f"WeatherAPI fallback failed: {e}")
            return None
    
    async def _search_cities_builtin(self, city_name: str, limit: int = 5) -> list:
        """Built-in city database as last resort"""
        # Популярные города с координатами
        builtin_cities = {
            # Украина
            "киев": {"lat": 50.4501, "lon": 30.5234, "country": "Ukraine", "name": "Киев"},
            "kiev": {"lat": 50.4501, "lon": 30.5234, "country": "Ukraine", "name": "Kiev"},
            "kyiv": {"lat": 50.4501, "lon": 30.5234, "country": "Ukraine", "name": "Kyiv"},
            "полтава": {"lat": 49.5937, "lon": 34.5407, "country": "Ukraine", "name": "Полтава"},
            "poltava": {"lat": 49.5937, "lon": 34.5407, "country": "Ukraine", "name": "Poltava"},
            "харьков": {"lat": 49.9935, "lon": 36.2304, "country": "Ukraine", "name": "Харьков"},
            "kharkiv": {"lat": 49.9935, "lon": 36.2304, "country": "Ukraine", "name": "Kharkiv"},
            "одесса": {"lat": 46.4825, "lon": 30.7233, "country": "Ukraine", "name": "Одесса"},
            "odesa": {"lat": 46.4825, "lon": 30.7233, "country": "Ukraine", "name": "Odesa"},
            "львов": {"lat": 49.8397, "lon": 24.0297, "country": "Ukraine", "name": "Львов"},
            "lviv": {"lat": 49.8397, "lon": 24.0297, "country": "Ukraine", "name": "Lviv"},
            "днепр": {"lat": 48.4647, "lon": 35.0462, "country": "Ukraine", "name": "Днепр"},
            "dnipro": {"lat": 48.4647, "lon": 35.0462, "country": "Ukraine", "name": "Dnipro"},
            
            # Россия
            "москва": {"lat": 55.7558, "lon": 37.6176, "country": "Russia", "name": "Москва"},
            "moscow": {"lat": 55.7558, "lon": 37.6176, "country": "Russia", "name": "Moscow"},
            "санкт-петербург": {"lat": 59.9311, "lon": 30.3609, "country": "Russia", "name": "Санкт-Петербург"},
            "saint petersburg": {"lat": 59.9311, "lon": 30.3609, "country": "Russia", "name": "Saint Petersburg"},
            "новосибирск": {"lat": 55.0084, "lon": 82.9357, "country": "Russia", "name": "Новосибирск"},
            "novosibirsk": {"lat": 55.0084, "lon": 82.9357, "country": "Russia", "name": "Novosibirsk"},
            
            # Популярные мировые города
            "london": {"lat": 51.5074, "lon": -0.1278, "country": "United Kingdom", "name": "London"},
            "лондон": {"lat": 51.5074, "lon": -0.1278, "country": "United Kingdom", "name": "Лондон"},
            "paris": {"lat": 48.8566, "lon": 2.3522, "country": "France", "name": "Paris"},
            "париж": {"lat": 48.8566, "lon": 2.3522, "country": "France", "name": "Париж"},
            "berlin": {"lat": 52.5200, "lon": 13.4050, "country": "Germany", "name": "Berlin"},
            "берлин": {"lat": 52.5200, "lon": 13.4050, "country": "Germany", "name": "Берлин"},
            "new york": {"lat": 40.7128, "lon": -74.0060, "country": "United States", "name": "New York"},
            "нью-йорк": {"lat": 40.7128, "lon": -74.0060, "country": "United States", "name": "Нью-Йорк"},
            "tokyo": {"lat": 35.6762, "lon": 139.6503, "country": "Japan", "name": "Tokyo"},
            "токио": {"lat": 35.6762, "lon": 139.6503, "country": "Japan", "name": "Токио"},
            "beijing": {"lat": 39.9042, "lon": 116.4074, "country": "China", "name": "Beijing"},
            "пекин": {"lat": 39.9042, "lon": 116.4074, "country": "China", "name": "Пекин"},
            "sydney": {"lat": -33.8688, "lon": 151.2093, "country": "Australia", "name": "Sydney"},
            "сидней": {"lat": -33.8688, "lon": 151.2093, "country": "Australia", "name": "Сидней"},
            "dubai": {"lat": 25.2048, "lon": 55.2708, "country": "United Arab Emirates", "name": "Dubai"},
            "дубай": {"lat": 25.2048, "lon": 55.2708, "country": "United Arab Emirates", "name": "Дубай"},
            "istanbul": {"lat": 41.0082, "lon": 28.9784, "country": "Turkey", "name": "Istanbul"},
            "стамбул": {"lat": 41.0082, "lon": 28.9784, "country": "Turkey", "name": "Стамбул"},
            "rome": {"lat": 41.9028, "lon": 12.4964, "country": "Italy", "name": "Rome"},
            "рим": {"lat": 41.9028, "lon": 12.4964, "country": "Italy", "name": "Рим"},
            "madrid": {"lat": 40.4168, "lon": -3.7038, "country": "Spain", "name": "Madrid"},
            "мадрид": {"lat": 40.4168, "lon": -3.7038, "country": "Spain", "name": "Мадрид"},
            "amsterdam": {"lat": 52.3676, "lon": 4.9041, "country": "Netherlands", "name": "Amsterdam"},
            "амстердам": {"lat": 52.3676, "lon": 4.9041, "country": "Netherlands", "name": "Амстердам"},
            "vienna": {"lat": 48.2082, "lon": 16.3738, "country": "Austria", "name": "Vienna"},
            "вена": {"lat": 48.2082, "lon": 16.3738, "country": "Austria", "name": "Вена"},
            "prague": {"lat": 50.0755, "lon": 14.4378, "country": "Czech Republic", "name": "Prague"},
            "прага": {"lat": 50.0755, "lon": 14.4378, "country": "Czech Republic", "name": "Прага"},
            "warsaw": {"lat": 52.2297, "lon": 21.0122, "country": "Poland", "name": "Warsaw"},
            "варшава": {"lat": 52.2297, "lon": 21.0122, "country": "Poland", "name": "Варшава"},
        }
        
        city_lower = city_name.lower().strip()
        results = []
        
        # Точное совпадение
        if city_lower in builtin_cities:
            city_data = builtin_cities[city_lower]
            results.append({
                "lat": city_data["lat"],
                "lon": city_data["lon"],
                "display_name": f"{city_data['name']}, {city_data['country']}",
                "readable_name": f"{city_data['name']}, {city_data['country']}",
                "country": city_data["country"],
                "state": "",
                "country_emoji": self._get_country_emoji(city_data["country"])
            })
        
        # Частичное совпадение
        if not results:
            for key, city_data in builtin_cities.items():
                if city_lower in key or key in city_lower:
                    results.append({
                        "lat": city_data["lat"],
                        "lon": city_data["lon"],
                        "display_name": f"{city_data['name']}, {city_data['country']}",
                        "readable_name": f"{city_data['name']}, {city_data['country']}",
                        "country": city_data["country"],
                        "state": "",
                        "country_emoji": self._get_country_emoji(city_data["country"])
                    })
                    if len(results) >= limit:
                        break
        
        if results:
            logger.info(f"Found {len(results)} cities in built-in database for '{city_name}'")
            # Кэшируем результат
            try:
                city_data = results[0]
                await DatabaseManager.cache_city(
                    city_name, 
                    city_data["lat"], 
                    city_data["lon"], 
                    city_data["country"], 
                    city_data["display_name"]
                )
            except Exception as e:
                logger.debug(f"Cache error: {e}")
        
        return results
    
    def get_clothing_recommendation(self, weather_data: Dict, language: str) -> str:
        """Get clothing recommendation based on weather"""
        temp = weather_data.get("current_temperature", 0)
        rain_prob = weather_data.get("rain_probability", 0)
        wind_speed = weather_data.get("wind_speed", 0)
        
        if language == "ru":
            recommendations = []
            
            if temp < -10:
                recommendations.append("Теплая зимняя куртка, шапка, перчатки")
            elif temp < 0:
                recommendations.append("Зимняя куртка, шапка")
            elif temp < 10:
                recommendations.append("Теплая куртка или пальто")
            elif temp < 20:
                recommendations.append("Легкая куртка или свитер")
            elif temp < 25:
                recommendations.append("Легкая одежда, возможно кофта")
            else:
                recommendations.append("Легкая летняя одежда")
            
            if rain_prob > 50:
                recommendations.append("зонт или дождевик")
            
            if wind_speed > 10:
                recommendations.append("защита от ветра")
            
            return ", ".join(recommendations).capitalize()
        
        elif language == "uk":
            recommendations = []
            
            if temp < -10:
                recommendations.append("Тепла зимова куртка, шапка, рукавички")
            elif temp < 0:
                recommendations.append("Зимова куртка, шапка")
            elif temp < 10:
                recommendations.append("Тепла куртка або пальто")
            elif temp < 20:
                recommendations.append("Легка куртка або светр")
            elif temp < 25:
                recommendations.append("Легкий одяг, можливо кофта")
            else:
                recommendations.append("Легкий літній одяг")
            
            if rain_prob > 50:
                recommendations.append("парасолька або дощовик")
            
            if wind_speed > 10:
                recommendations.append("захист від вітру")
            
            return ", ".join(recommendations).capitalize()
        
        else:  # English
            recommendations = []
            
            if temp < -10:
                recommendations.append("Heavy winter coat, hat, gloves")
            elif temp < 0:
                recommendations.append("Winter coat, hat")
            elif temp < 10:
                recommendations.append("Warm jacket or coat")
            elif temp < 20:
                recommendations.append("Light jacket or sweater")
            elif temp < 25:
                recommendations.append("Light clothing, maybe a cardigan")
            else:
                recommendations.append("Light summer clothing")
            
            if rain_prob > 50:
                recommendations.append("umbrella or raincoat")
            
            if wind_speed > 10:
                recommendations.append("wind protection")
            
            return ", ".join(recommendations).capitalize()


# Global weather API instance
weather_api = WeatherAPI()

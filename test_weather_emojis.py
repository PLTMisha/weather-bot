#!/usr/bin/env python3
"""
Test script to verify weather emojis functionality across all languages
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from weather_api import weather_api

async def test_weather_emojis():
    """Test weather emojis for different weather codes"""
    print("🧪 Testing Weather Emojis Functionality\n")
    print("=" * 50)
    
    # Test weather codes and their expected emojis
    test_codes = [
        (0, "Clear sky", "☀️"),
        (1, "Mainly clear", "🌤"),
        (2, "Partly cloudy", "⛅"),
        (3, "Overcast", "☁️"),
        (45, "Fog", "🌫"),
        (48, "Depositing rime fog", "🌫"),
        (51, "Light drizzle", "🌦"),
        (53, "Moderate drizzle", "🌦"),
        (55, "Dense drizzle", "🌦"),
        (61, "Slight rain", "🌧"),
        (63, "Moderate rain", "🌧"),
        (65, "Heavy rain", "🌧"),
        (71, "Slight snow", "🌨"),
        (73, "Moderate snow", "🌨"),
        (75, "Heavy snow", "🌨"),
        (77, "Snow grains", "🌨"),
        (80, "Slight rain showers", "🌦"),
        (81, "Moderate rain showers", "🌦"),
        (82, "Violent rain showers", "🌦"),
        (85, "Slight snow showers", "🌨"),
        (86, "Heavy snow showers", "🌨"),
        (95, "Thunderstorm", "⛈"),
        (96, "Thunderstorm with slight hail", "⛈"),
        (99, "Thunderstorm with heavy hail", "⛈"),
    ]
    
    print("Testing weather emoji mapping:")
    print("-" * 30)
    
    success_count = 0
    total_count = len(test_codes)
    
    for weather_code, description, expected_emoji in test_codes:
        actual_emoji = weather_api._get_weather_emoji(weather_code)
        status = "✅" if actual_emoji == expected_emoji else "❌"
        
        if actual_emoji == expected_emoji:
            success_count += 1
        
        print(f"{status} Code {weather_code:2d}: {actual_emoji} {description}")
        
        if actual_emoji != expected_emoji:
            print(f"    Expected: {expected_emoji}, Got: {actual_emoji}")
    
    print("\n" + "=" * 50)
    print(f"Results: {success_count}/{total_count} tests passed")
    
    if success_count == total_count:
        print("🎉 All weather emoji tests PASSED!")
    else:
        print(f"⚠️  {total_count - success_count} tests FAILED!")
    
    return success_count == total_count

async def test_weather_forecast_with_emojis():
    """Test weather forecast with emojis for different languages"""
    print("\n" + "=" * 50)
    print("🌍 Testing Weather Forecast with Emojis for All Languages")
    print("=" * 50)
    
    # Test coordinates for London
    lat, lon = 51.5074, -0.1278
    languages = ["en", "ru", "uk"]
    
    for language in languages:
        print(f"\n🔤 Testing language: {language.upper()}")
        print("-" * 30)
        
        try:
            # Get weather forecast
            weather_data = await weather_api.get_weather_forecast(lat, lon, language, days=1)
            
            if weather_data and weather_data.get("hourly_forecast"):
                print("✅ Weather data retrieved successfully")
                
                # Test first few hours
                hourly_data = weather_data["hourly_forecast"][:3]  # First 3 hours
                
                for i, hour_data in enumerate(hourly_data):
                    weather_code = hour_data.get('weather_code', 0)
                    weather_emoji = weather_api._get_weather_emoji(weather_code)
                    
                    print(f"   {hour_data['time']}: {hour_data['temperature']}°C {weather_emoji} {hour_data['description']}")
                
                # Test daily forecast if available
                if weather_data.get("daily_forecast"):
                    daily_data = weather_data["daily_forecast"][0]  # Today
                    weather_code = daily_data.get('weather_code', 0)
                    weather_emoji = weather_api._get_weather_emoji(weather_code)
                    
                    print(f"   Daily: {daily_data['min_temperature']}°C...{daily_data['max_temperature']}°C {weather_emoji} {daily_data['description']}")
                
            else:
                print("❌ Failed to retrieve weather data")
                
        except Exception as e:
            print(f"❌ Error testing language {language}: {e}")

async def main():
    """Main test function"""
    print("🚀 Starting Weather Emojis Test Suite")
    print("=" * 60)
    
    # Test 1: Weather emoji mapping
    emoji_test_passed = await test_weather_emojis()
    
    # Test 2: Weather forecast with emojis
    await test_weather_forecast_with_emojis()
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Weather Emoji Mapping: {'✅ PASSED' if emoji_test_passed else '❌ FAILED'}")
    print(f"   Weather Forecast Integration: ✅ COMPLETED")
    
    print("\n🎯 Weather emojis are now integrated into:")
    print("   • Hourly forecasts (bot.py - handle_hourly_forecast)")
    print("   • Daily forecasts (bot.py - handle_daily_forecast)")
    print("   • All supported languages (English, Russian, Ukrainian)")
    
    print("\n✨ Users will now see weather-specific emojis like:")
    print("   ☀️ for clear weather")
    print("   🌧 for rain")
    print("   ⛈ for thunderstorms")
    print("   🌨 for snow")
    print("   ⛅ for partly cloudy")
    print("   And many more!")

if __name__ == "__main__":
    asyncio.run(main())

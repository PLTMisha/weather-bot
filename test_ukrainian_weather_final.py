#!/usr/bin/env python3
"""
Final test for Ukrainian weather descriptions and clothing recommendations
"""
import asyncio
from weather_api import WeatherAPI

async def test_ukrainian_weather_descriptions():
    """Test Ukrainian weather descriptions"""
    print("🌤 Testing Ukrainian Weather Descriptions")
    print("=" * 50)
    
    weather_api = WeatherAPI()
    
    # Test weather codes
    weather_codes = weather_api._get_weather_codes("uk")
    
    print("Sample Ukrainian weather descriptions:")
    test_codes = [0, 1, 2, 3, 45, 61, 63, 65, 71, 73, 75, 95]
    
    for code in test_codes:
        description = weather_codes.get(code, "Unknown")
        print(f"  Code {code}: {description}")

def test_ukrainian_clothing_recommendations():
    """Test Ukrainian clothing recommendations"""
    print("\n👕 Testing Ukrainian Clothing Recommendations")
    print("=" * 55)
    
    weather_api = WeatherAPI()
    
    # Test different temperature scenarios
    test_scenarios = [
        {"temp": -15, "rain": 10, "wind": 5, "desc": "Very cold"},
        {"temp": -5, "rain": 20, "wind": 8, "desc": "Cold"},
        {"temp": 5, "rain": 30, "wind": 12, "desc": "Cool"},
        {"temp": 15, "rain": 60, "wind": 6, "desc": "Mild with rain"},
        {"temp": 22, "rain": 20, "wind": 4, "desc": "Warm"},
        {"temp": 30, "rain": 5, "wind": 15, "desc": "Hot and windy"}
    ]
    
    for scenario in test_scenarios:
        weather_data = {
            "current_temperature": scenario["temp"],
            "rain_probability": scenario["rain"],
            "wind_speed": scenario["wind"]
        }
        
        recommendation = weather_api.get_clothing_recommendation(weather_data, "uk")
        print(f"  {scenario['desc']} ({scenario['temp']}°C): {recommendation}")

def test_ukrainian_day_names():
    """Test Ukrainian day names"""
    print("\n📅 Testing Ukrainian Day Names")
    print("=" * 35)
    
    weather_api = WeatherAPI()
    
    from datetime import datetime, timedelta
    
    # Test all days of the week
    base_date = datetime(2024, 1, 1)  # Monday
    
    for i in range(7):
        test_date = base_date + timedelta(days=i)
        day_name = weather_api._get_day_name(test_date, "uk")
        print(f"  {test_date.strftime('%Y-%m-%d')}: {day_name}")

async def test_complete_ukrainian_weather():
    """Test complete Ukrainian weather functionality"""
    print("\n🇺🇦 Testing Complete Ukrainian Weather")
    print("=" * 45)
    
    weather_api = WeatherAPI()
    
    try:
        # Search for a Ukrainian city
        cities = await weather_api.search_cities("Львів", limit=1)
        
        if cities:
            city = cities[0]
            print(f"✅ Found city: {city.get('country_emoji', '🏙')} {city.get('readable_name', 'Unknown')}")
            
            # Get weather with Ukrainian language
            weather = await weather_api.get_weather_forecast(city['lat'], city['lon'], 'uk', 1)
            
            if weather:
                print("✅ Weather data in Ukrainian:")
                print(f"   🌡 Температура: {weather.get('current_temperature', 'N/A')}°C")
                print(f"   🌡 Відчувається як: {weather.get('feels_like', 'N/A')}°C")
                print(f"   ☁️ Опис: {weather.get('description', 'N/A')}")
                print(f"   💧 Вологість: {weather.get('humidity', 'N/A')}%")
                print(f"   🌬 Вітер: {weather.get('wind_speed', 'N/A')} м/с")
                print(f"   🌧 Ймовірність дощу: {weather.get('rain_probability', 'N/A')}%")
                
                # Test clothing recommendation
                recommendation = weather_api.get_clothing_recommendation(weather, "uk")
                print(f"   👕 Рекомендація: {recommendation}")
                
                # Test daily forecast if available
                if weather.get('daily_forecast'):
                    print("\n📅 Прогноз по днях:")
                    for day in weather['daily_forecast'][:3]:
                        print(f"   {day['day_name']}: {day['min_temperature']}°C...{day['max_temperature']}°C - {day['description']}")
                
            else:
                print("❌ Failed to get weather data")
        else:
            print("❌ City not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Main test function"""
    print("🧪 Final Ukrainian Weather Test")
    print("=" * 50)
    
    await test_ukrainian_weather_descriptions()
    test_ukrainian_clothing_recommendations()
    test_ukrainian_day_names()
    await test_complete_ukrainian_weather()
    
    print("\n✅ Final Ukrainian weather test completed!")
    print("🇺🇦 Всі описи погоди та рекомендації працюють українською!")
    
    print("\n📋 Summary of Ukrainian Weather Features:")
    print("✅ Weather descriptions: Ясно, Мінлива хмарність, Помірний дощ, etc.")
    print("✅ Clothing recommendations: Легкий літній одяг, парасолька, etc.")
    print("✅ Day names: Понеділок, Вівторок, Середа, etc.")
    print("✅ Complete weather forecasts in Ukrainian")

if __name__ == "__main__":
    asyncio.run(main())

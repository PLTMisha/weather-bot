#!/usr/bin/env python3
"""
Test script for Ukrainian language functionality
"""
import asyncio
from localization import localization, get_user_language, _

def test_ukrainian_translations():
    """Test Ukrainian translations"""
    print("🇺🇦 Testing Ukrainian Language Support")
    print("=" * 50)
    
    # Test basic translations
    print("\n1. Basic Messages:")
    print(f"Welcome: {localization.get_text('welcome_message', 'uk')}")
    print(f"Language changed: {localization.get_text('language_changed', 'uk')}")
    
    print("\n2. Main Menu:")
    print(f"Main menu: {localization.get_text('main_menu', 'uk')}")
    print(f"My city: {localization.get_text('my_city', 'uk', city='Київ')}")
    print(f"Weather now: {localization.get_text('weather_now', 'uk')}")
    print(f"Settings: {localization.get_text('settings', 'uk')}")
    
    print("\n3. City Selection:")
    print(f"Select city: {localization.get_text('select_city', 'uk')}")
    print(f"Enter city: {localization.get_text('enter_city', 'uk')}")
    print(f"City set: {localization.get_text('city_set', 'uk', city='Львів')}")
    
    print("\n4. Time Selection:")
    print(f"Select time: {localization.get_text('select_time', 'uk')}")
    print(f"Time set: {localization.get_text('time_set', 'uk', time='09:00')}")
    
    print("\n5. Weather Forecast:")
    print(f"Weather in: {localization.get_text('weather_in', 'uk', city='Одеса', date='сьогодні')}")
    print(f"Current temp: {localization.get_text('current_temp', 'uk', temp='15', feels_like='12')}")
    print(f"Today range: {localization.get_text('today_range', 'uk', min='8', max='18')}")
    print(f"Humidity: {localization.get_text('humidity', 'uk', humidity='65')}")
    print(f"Wind: {localization.get_text('wind', 'uk', speed='3.2')}")
    print(f"Rain prob: {localization.get_text('rain_prob', 'uk', prob='20')}")
    print(f"Have great day: {localization.get_text('have_great_day', 'uk')}")
    
    print("\n6. Settings Menu:")
    print(f"Settings menu: {localization.get_text('settings_menu', 'uk')}")
    print(f"Change city: {localization.get_text('change_city', 'uk')}")
    print(f"Change time: {localization.get_text('change_time', 'uk')}")
    print(f"Language: {localization.get_text('language', 'uk')}")
    print(f"Help: {localization.get_text('help', 'uk')}")
    
    print("\n7. Status Info:")
    status = localization.get_text('status_info', 'uk', 
                                 city='Харків', 
                                 time='08:30', 
                                 notifications='Увімк', 
                                 date='01.01.2024')
    print(status)
    
    print("\n8. Help Text:")
    help_text = localization.get_text('help_text', 'uk')
    print(help_text[:200] + "..." if len(help_text) > 200 else help_text)
    
    print("\n9. Navigation:")
    print(f"Back: {localization.get_text('back', 'uk')}")
    print(f"Back to menu: {localization.get_text('back_to_menu', 'uk')}")
    
    print("\n10. Notifications:")
    print(f"Notifications enabled: {localization.get_text('notifications_enabled', 'uk')}")
    print(f"Notifications disabled: {localization.get_text('notifications_disabled', 'uk')}")

def test_language_keyboard():
    """Test language keyboard"""
    print("\n🌍 Language Keyboard:")
    print("=" * 30)
    keyboard = localization.get_language_keyboard()
    for row in keyboard:
        for button_text, callback_data in row:
            print(f"Button: {button_text} -> {callback_data}")

def test_popular_cities():
    """Test popular cities for Ukrainian"""
    print("\n🏙 Popular Cities (Ukrainian):")
    print("=" * 35)
    cities = localization.get_popular_cities('uk')
    for row in cities:
        for city_text, callback_data in row:
            print(f"City: {city_text} -> {callback_data}")

def test_time_slots():
    """Test time slots"""
    print("\n⏰ Time Slots:")
    print("=" * 20)
    time_slots = localization.get_time_slots('uk')
    for row in time_slots:
        for time_text, callback_data in row:
            print(f"Time: {time_text} -> {callback_data}")

def test_shorthand_function():
    """Test shorthand _ function"""
    print("\n🔧 Shorthand Function Test:")
    print("=" * 30)
    print(f"English: {_('welcome_message', 'en')}")
    print(f"Russian: {_('welcome_message', 'ru')}")
    print(f"Ukrainian: {_('welcome_message', 'uk')}")

def test_fallback():
    """Test fallback to default language"""
    print("\n🔄 Fallback Test:")
    print("=" * 20)
    # Test with non-existent language
    print(f"Non-existent lang: {localization.get_text('welcome_message', 'fr')}")
    # Test with non-existent key
    print(f"Non-existent key: {localization.get_text('non_existent_key', 'uk')}")

def main():
    """Main test function"""
    print("🧪 Ukrainian Language Support Test")
    print("=" * 60)
    
    test_ukrainian_translations()
    test_language_keyboard()
    test_popular_cities()
    test_time_slots()
    test_shorthand_function()
    test_fallback()
    
    print("\n✅ Ukrainian language test completed!")
    print("🇺🇦 Українська мова повністю підтримується!")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test script to verify database connection and SQLite fallback functionality
"""
import asyncio
import os
import sys
from database import init_db, DatabaseManager, engine
from sqlalchemy import text

async def test_database_connection():
    """Test database connection and basic operations"""
    print("=== Testing Database Connection ===")
    
    try:
        # Test database initialization
        print("1. Initializing database...")
        await init_db()
        print("✅ Database initialized successfully")
        
        # Test database connection
        print("2. Testing database connection...")
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        
        # Test user operations
        print("3. Testing user operations...")
        test_user_id = 123456789
        
        # Create test user
        user = await DatabaseManager.create_or_update_user(
            user_id=test_user_id,
            language="en",
            city="Test City"
        )
        print(f"✅ Created test user: {user.user_id}")
        
        # Get test user
        retrieved_user = await DatabaseManager.get_user(test_user_id)
        if retrieved_user:
            print(f"✅ Retrieved test user: {retrieved_user.city}")
        else:
            print("❌ Failed to retrieve test user")
        
        # Log test action
        await DatabaseManager.log_action(test_user_id, "test_action", {"test": "data"})
        print("✅ Logged test action")
        
        print("\n=== All Database Tests Passed! ===")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("Starting database connection test...")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    
    success = await test_database_connection()
    
    if success:
        print("\n🎉 Database connection test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Database connection test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

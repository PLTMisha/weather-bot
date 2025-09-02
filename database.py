from sqlalchemy import BigInteger, String, Boolean, Time, DECIMAL, DateTime, Integer, JSON, Text, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from config import settings
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from datetime import datetime, time as time_type

# Convert database URL for async usage
if settings.database_url.startswith("postgresql://"):
    async_database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif settings.database_url.startswith("sqlite://"):
    async_database_url = settings.database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
else:
    async_database_url = settings.database_url

# Create async engine
engine = create_async_engine(async_database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    language: Mapped[str] = mapped_column(String(2), default="en")
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    city_lat: Mapped[float] = mapped_column(DECIMAL(10, 8), nullable=True)
    city_lon: Mapped[float] = mapped_column(DECIMAL(11, 8), nullable=True)
    notification_time: Mapped[time_type] = mapped_column(Time, default=time_type(9, 0))
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class BotLog(Base):
    __tablename__ = "bot_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    action: Mapped[str] = mapped_column(String(50))
    data: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class CityCache(Base):
    __tablename__ = "city_cache"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    city_name: Mapped[str] = mapped_column(String(100), index=True)
    latitude: Mapped[float] = mapped_column(DECIMAL(10, 8))
    longitude: Mapped[float] = mapped_column(DECIMAL(11, 8))
    country: Mapped[str] = mapped_column(String(100))
    display_name: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Initialize database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Database operations
class DatabaseManager:
    @staticmethod
    async def get_user(user_id: int) -> User:
        async with AsyncSessionLocal() as session:
            result = await session.get(User, user_id)
            return result
    
    @staticmethod
    async def create_or_update_user(user_id: int, **kwargs) -> User:
        async with AsyncSessionLocal() as session:
            user = await session.get(User, user_id)
            if user:
                for key, value in kwargs.items():
                    setattr(user, key, value)
                user.updated_at = datetime.now()
            else:
                user = User(user_id=user_id, **kwargs)
                session.add(user)
            
            await session.commit()
            await session.refresh(user)
            return user
    
    @staticmethod
    async def get_users_for_notification(notification_time: str):
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            from datetime import time
            
            # Parse time string to time object
            try:
                hour, minute = map(int, notification_time.split(':'))
                time_obj = time(hour, minute)
            except ValueError:
                return []
            
            # Get users who should receive notifications at this time
            query = select(User).where(
                User.notifications_enabled == True,
                User.notification_time == time_obj
            )
            result = await session.execute(query)
            return result.scalars().all()
    
    @staticmethod
    async def log_action(user_id: int, action: str, data: dict = None):
        async with AsyncSessionLocal() as session:
            log_entry = BotLog(user_id=user_id, action=action, data=data)
            session.add(log_entry)
            await session.commit()
    
    @staticmethod
    async def get_cached_cities(city_name: str) -> list[CityCache]:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            
            query = select(CityCache).where(CityCache.city_name.ilike(f"%{city_name}%"))
            result = await session.execute(query)
            return result.scalars().all()
    
    @staticmethod
    async def cache_city(city_name: str, latitude: float, longitude: float, 
                        country: str, display_name: str) -> CityCache:
        async with AsyncSessionLocal() as session:
            city_cache = CityCache(
                city_name=city_name,
                latitude=latitude,
                longitude=longitude,
                country=country,
                display_name=display_name
            )
            session.add(city_cache)
            await session.commit()
            await session.refresh(city_cache)
            return city_cache

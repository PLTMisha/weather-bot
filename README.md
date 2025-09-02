# Weather Bot - Telegram Daily Weather Notifications

A comprehensive Telegram bot that provides daily weather forecasts with multi-language support, built for deployment on Render.com with BetterStack monitoring.

## Features

- 🌍 **Multi-language support** (English & Russian)
- 🏙️ **City-based weather forecasts** using Open-Meteo API
- ⏰ **Customizable daily notifications**
- 👕 **Smart clothing recommendations**
- 📊 **Comprehensive monitoring** with BetterStack
- 🔄 **Automatic keep-alive** for Render.com free tier
- 💾 **PostgreSQL database** for user data
- 🎯 **Inline keyboard interface** (no text commands except /start)

## Tech Stack

- **Backend**: FastAPI + aiogram 3.x
- **Database**: PostgreSQL with SQLAlchemy
- **Weather API**: Open-Meteo (free, no API key required)
- **Geocoding**: Nominatim OSM
- **Scheduler**: APScheduler
- **Monitoring**: BetterStack integration
- **Deployment**: Render.com

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Telegram Bot Token (from @BotFather)
- PostgreSQL database
- (Optional) BetterStack account for monitoring

### 2. Local Development

1. **Clone and setup**:
```bash
git clone <your-repo>
cd weather-bot
pip install -r requirements.txt
```

2. **Environment setup**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Required environment variables**:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_URL=postgresql://username:password@localhost:5432/weather_bot
WEBHOOK_URL=https://your-app.onrender.com/webhook  # For production
BETTER_STACK_TOKEN=your_token_here  # Optional
```

4. **Run locally**:
```bash
python main.py
```

### 3. Render.com Deployment

1. **Connect your GitHub repository** to Render.com

2. **Create PostgreSQL database**:
   - Go to Render Dashboard → New → PostgreSQL
   - Choose "Free" plan
   - Note the connection details

3. **Create Web Service**:
   - Go to Render Dashboard → New → Web Service
   - Connect your repository
   - Use these settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Set environment variables**:
   - `TELEGRAM_BOT_TOKEN`: Your bot token
   - `DATABASE_URL`: Auto-filled from database
   - `WEBHOOK_URL`: `https://your-app-name.onrender.com/webhook`
   - `BETTER_STACK_TOKEN`: Your monitoring token (optional)
   - `ENVIRONMENT`: `production`

5. **Deploy**: The app will automatically deploy and set up the database tables.

## Bot Usage

### User Commands

- `/start` - Initialize bot and select language

### Interface Navigation

All interactions happen through inline keyboards:

1. **Language Selection**: Choose English or Russian
2. **Main Menu**:
   - 🏙️ Set/change city
   - ⏰ Set notification time
   - 🔔 Toggle notifications
   - 🌤️ Get current weather
   - ⚙️ Settings

3. **City Selection**: Popular cities or custom input
4. **Time Selection**: Preset times or custom HH:MM format
5. **Settings**: Language, status, help

### Daily Notifications

Users receive automatic weather notifications at their chosen time with:
- Current temperature and "feels like"
- Min/max temperatures for the day
- Weather description
- Humidity and wind speed
- Rain probability
- Clothing recommendations

## API Endpoints

### Public Endpoints

- `GET /` - API information
- `GET /health` - Health check for monitoring
- `POST /webhook` - Telegram webhook endpoint

### Admin Endpoints

- `GET /status` - Detailed system status
- `GET /metrics` - Application metrics
- `POST /admin/test-notification/{user_id}` - Send test notification
- `GET /admin/users-at-time/{time}` - Users with notifications at specific time
- `GET /admin/scheduler-status` - Scheduler status

## Architecture

### Core Components

1. **main.py** - FastAPI application and lifecycle management
2. **bot.py** - Telegram bot logic and handlers
3. **database.py** - Database models and operations
4. **weather_api.py** - Weather data integration
5. **scheduler.py** - Daily notification scheduling
6. **localization.py** - Multi-language support
7. **monitoring.py** - BetterStack integration and metrics
8. **config.py** - Configuration management

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    language VARCHAR(2) DEFAULT 'en',
    city VARCHAR(100),
    city_lat DECIMAL(10, 8),
    city_lon DECIMAL(11, 8),
    notification_time TIME DEFAULT '09:00',
    timezone VARCHAR(50) DEFAULT 'UTC',
    notifications_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Logging table
CREATE TABLE bot_logs (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    action VARCHAR(50),
    data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- City cache for performance
CREATE TABLE city_cache (
    id SERIAL PRIMARY KEY,
    city_name VARCHAR(100) UNIQUE,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    country VARCHAR(100),
    display_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Monitoring & Observability

### BetterStack Integration

The bot includes comprehensive monitoring:

- **Uptime monitoring** via `/health` endpoint
- **Error tracking** with structured logging
- **Performance metrics** (response times, API calls)
- **User activity logging**
- **Scheduler status monitoring**

### Health Checks

The system monitors:
- Database connectivity
- Weather API availability
- Scheduler status
- Overall application health

### Metrics Tracked

- Total requests and success/error rates
- Weather API calls and response times
- Notifications sent/failed
- Active users (24h)
- System uptime

## Render.com Optimizations

### Free Tier Considerations

1. **Keep-alive mechanism**: Automatic pings every 10 minutes
2. **Fast webhook processing**: < 15 second response times
3. **Graceful cold start handling**: 30-60 second startup tolerance
4. **Efficient database queries**: Indexed and optimized
5. **Caching**: City coordinates and weather data

### Performance Features

- Asynchronous processing throughout
- Connection pooling for database
- Response time monitoring
- Automatic error recovery
- Batch notification processing

## Development

### Project Structure

```
weather-bot/
├── main.py              # FastAPI application
├── bot.py               # Telegram bot logic
├── database.py          # Database models & operations
├── weather_api.py       # Weather API integration
├── scheduler.py         # Notification scheduling
├── localization.py      # Multi-language support
├── monitoring.py        # BetterStack & metrics
├── config.py            # Configuration
├── requirements.txt     # Python dependencies
├── render.yaml          # Render.com configuration
├── .env.example         # Environment template
└── README.md           # This file
```

### Adding New Languages

1. Add language code to `SUPPORTED_LANGUAGES` in `config.py`
2. Add translations to `localization.py`
3. Update popular cities and time slots
4. Test all user flows

### Adding New Features

1. Update database models if needed
2. Add new handlers to `bot.py`
3. Update localization strings
4. Add monitoring/logging
5. Update documentation

## Troubleshooting

### Common Issues

1. **Bot not responding**:
   - Check webhook URL is correct
   - Verify bot token
   - Check `/health` endpoint

2. **Database connection errors**:
   - Verify DATABASE_URL format
   - Check database is running
   - Review connection limits

3. **Weather API failures**:
   - Open-Meteo is free and reliable
   - Check internet connectivity
   - Review API response format

4. **Notifications not sending**:
   - Check scheduler status via `/admin/scheduler-status`
   - Verify user notification settings
   - Check logs for errors

### Logs and Debugging

- Application logs via Render.com dashboard
- BetterStack logs (if configured)
- Database query logs
- Structured JSON logging format

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check this README
2. Review application logs
3. Check `/health` and `/status` endpoints
4. Create an issue in the repository

---

**Built with ❤️ for reliable weather notifications on Render.com**

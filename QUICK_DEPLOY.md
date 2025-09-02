# ⚡ Быстрый деплой Weather Bot на Render.com

## 🚀 За 10 минут до продакшена!

### 1. Подготовка (2 минуты)
```bash
# Создай GitHub репозиторий и загрузи код
git init
git add .
git commit -m "Weather Bot ready for deploy"
git remote add origin https://github.com/YOUR_USERNAME/weather-bot.git
git push -u origin main
```

### 2. Создай Telegram бота (1 минута)
1. Напиши [@BotFather](https://t.me/botfather) → `/newbot`
2. Скопируй токен: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### 3. Render.com деплой (5 минут)
1. Зайди на [render.com](https://render.com) → **New +** → **Web Service**
2. Подключи GitHub репозиторий
3. Настройки:
   - **Name**: `weather-bot`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 4. Переменные окружения (1 минута)
Добавь в **Environment Variables**:
```
TELEGRAM_BOT_TOKEN=твой_токен_бота
WEBHOOK_URL=https://weather-bot.onrender.com/webhook
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 5. База данных (1 минута)
1. **New +** → **PostgreSQL**
2. **Name**: `weather-bot-db`
3. **Plan**: Free
4. В веб-сервисе добавь: `DATABASE_URL=${{weather-bot-db.DATABASE_URL}}`

### 6. BetterStack мониторинг (опционально)
1. Зарегистрируйся на [betterstack.com](https://betterstack.com)
2. Создай проект → скопируй токен
3. Добавь: `BETTER_STACK_TOKEN=твой_токен`
4. Настрой uptime мониторинг на `/health`

## ✅ Проверка
1. Открой `https://weather-bot.onrender.com/health`
2. Найди бота в Telegram → `/start`
3. Настрой город и время уведомлений

## 🎯 Готово!
Твой бот работает 24/7 с:
- ☀️ Погодными эмодзи
- 🌍 3 языками (EN/RU/UK)
- 📊 Мониторингом BetterStack
- 🔔 Ежедневными уведомлениями
- 📱 Красивым интерфейсом

---
📖 **Подробная инструкция**: `RENDER_DEPLOY_GUIDE.md`

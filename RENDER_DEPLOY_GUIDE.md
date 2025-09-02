# 🚀 Полное руководство по деплою Weather Bot на Render.com + BetterStack

## 📋 Предварительные требования

### 1. Создание Telegram бота
1. Найди [@BotFather](https://t.me/botfather) в Telegram
2. Отправь `/newbot`
3. Следуй инструкциям для создания бота
4. Сохрани **TELEGRAM_BOT_TOKEN** (например: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Регистрация на Render.com
1. Перейди на [render.com](https://render.com)
2. Зарегистрируйся через GitHub (рекомендуется)
3. Подтверди email

### 3. Регистрация на BetterStack
1. Перейди на [betterstack.com](https://betterstack.com)
2. Зарегистрируйся (есть бесплатный план)
3. Создай новый проект для логирования
4. Получи **BETTER_STACK_TOKEN** из настроек проекта

## 🔧 Подготовка кода

### 1. Создание GitHub репозитория
```bash
# Инициализация git репозитория
git init
git add .
git commit -m "Initial commit: Weather Bot"

# Создай репозиторий на GitHub и добавь remote
git remote add origin https://github.com/YOUR_USERNAME/weather-bot.git
git branch -M main
git push -u origin main
```

### 2. Проверка файлов
Убедись, что у тебя есть все необходимые файлы:
- ✅ `render.yaml` - конфигурация Render
- ✅ `requirements.txt` - зависимости Python
- ✅ `main.py` - веб-сервер FastAPI
- ✅ `bot.py` - логика Telegram бота
- ✅ `weather_api.py` - API погоды
- ✅ `database.py` - работа с БД
- ✅ `scheduler.py` - планировщик уведомлений
- ✅ `monitoring.py` - мониторинг BetterStack
- ✅ `config.py` - конфигурация
- ✅ `localization.py` - локализация

## 🚀 Деплой на Render.com

### Шаг 1: Создание веб-сервиса
1. Войди в [Render Dashboard](https://dashboard.render.com)
2. Нажми **"New +"** → **"Web Service"**
3. Подключи свой GitHub репозиторий
4. Выбери репозиторий с ботом

### Шаг 2: Настройка сервиса
**Основные настройки:**
- **Name**: `weather-bot` (или любое другое имя)
- **Environment**: `Python 3`
- **Region**: `Frankfurt (EU Central)` (ближе к пользователям)
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Шаг 3: Настройка переменных окружения
В разделе **Environment Variables** добавь:

```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
BETTER_STACK_TOKEN=your_betterstack_token_here
WEBHOOK_URL=https://your-app-name.onrender.com/webhook
ENVIRONMENT=production
LOG_LEVEL=INFO
```

⚠️ **ВАЖНО**: Замени `your-app-name` на реальное имя твоего сервиса!

### Шаг 4: Создание базы данных
1. В Render Dashboard нажми **"New +"** → **"PostgreSQL"**
2. **Name**: `weather-bot-db`
3. **Plan**: `Free` (1GB, достаточно для старта)
4. **Region**: тот же, что и веб-сервис
5. Нажми **"Create Database"**

### Шаг 5: Подключение БД к сервису
1. Перейди в настройки веб-сервиса
2. В **Environment Variables** добавь:
```
DATABASE_URL=${{weather-bot-db.DATABASE_URL}}
```

### Шаг 6: Деплой
1. Нажми **"Create Web Service"**
2. Render автоматически начнет деплой
3. Процесс займет 5-10 минут

## 📊 Настройка мониторинга BetterStack

### Шаг 1: Uptime мониторинг
1. В BetterStack перейди в **Uptime**
2. Нажми **"Create monitor"**
3. **URL**: `https://your-app-name.onrender.com/health`
4. **Name**: `Weather Bot Health`
5. **Check frequency**: `60 seconds`
6. **Timeout**: `30 seconds`
7. Настрой алерты на email/Slack

### Шаг 2: Логирование
1. В BetterStack перейди в **Logs**
2. Создай новый **Source**
3. Скопируй **Source Token** - это твой `BETTER_STACK_TOKEN`
4. Добавь токен в переменные окружения Render

### Шаг 3: Настройка алертов
Рекомендуемые алерты:
- **Uptime < 99%** - уведомление через 5 минут
- **Response time > 2s** - уведомление через 3 неудачных проверки
- **Error rate > 5%** - мгновенное уведомление
- **Database connection failed** - критический алерт

## 🔧 Настройка Telegram Webhook

После успешного деплоя:

### Автоматическая настройка
Webhook настроится автоматически при запуске приложения.

### Ручная настройка (если нужно)
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-app-name.onrender.com/webhook"}'
```

### Проверка webhook
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

## ✅ Проверка работоспособности

### 1. Проверка сервиса
- Открой `https://your-app-name.onrender.com/` - должен показать статус API
- Открой `https://your-app-name.onrender.com/health` - должен показать "healthy"

### 2. Проверка бота
1. Найди своего бота в Telegram
2. Отправь `/start`
3. Выбери язык и настрой город
4. Проверь прогноз погоды

### 3. Проверка уведомлений
1. Настрой время уведомления на ближайшие минуты
2. Дождись уведомления
3. Проверь логи в BetterStack

## 🛠 Полезные команды для отладки

### Просмотр логов Render
```bash
# В Render Dashboard → твой сервис → Logs
```

### Проверка статуса через API
```bash
curl https://your-app-name.onrender.com/status
```

### Проверка метрик
```bash
curl https://your-app-name.onrender.com/metrics
```

### Отправка тестового уведомления
```bash
curl -X POST https://your-app-name.onrender.com/admin/test-notification/YOUR_USER_ID
```

## 🚨 Решение проблем

### Проблема: Сервис "засыпает"
**Решение**: Render Free tier засыпает после 15 минут неактивности.
- Используй внешний uptime мониторинг (BetterStack)
- Настрой пинг каждые 10 минут

### Проблема: База данных недоступна
**Решение**:
1. Проверь `DATABASE_URL` в переменных окружения
2. Убедись, что БД создана в том же регионе
3. Проверь логи подключения

### Проблема: Webhook не работает
**Решение**:
1. Проверь `WEBHOOK_URL` в переменных окружения
2. Убедись, что URL доступен извне
3. Проверь логи webhook запросов

### Проблема: Уведомления не отправляются
**Решение**:
1. Проверь планировщик: `/admin/scheduler-status`
2. Проверь пользователей: `/admin/users-at-time/09:00`
3. Проверь логи в BetterStack

## 📈 Мониторинг и метрики

### Доступные эндпоинты
- `/` - Главная страница API
- `/health` - Проверка здоровья системы
- `/status` - Детальный статус всех компонентов
- `/metrics` - Метрики производительности
- `/admin/scheduler-status` - Статус планировщика
- `/admin/users-at-time/{time}` - Пользователи по времени

### Метрики в BetterStack
- Количество запросов
- Время ответа API
- Ошибки и исключения
- Активность пользователей
- Статус планировщика
- Работа с Weather API

## 🎯 Оптимизация для Free Tier

### Render.com Free Tier ограничения:
- 750 часов в месяц (достаточно для 24/7)
- Засыпание после 15 минут неактивности
- 512MB RAM
- Общий CPU

### Оптимизации:
1. **Keep-alive**: BetterStack пингует каждые 60 сек
2. **Кэширование**: Координаты городов кэшируются
3. **Батчинг**: Уведомления отправляются группами
4. **Асинхронность**: Все операции асинхронные

## 🔐 Безопасность

### Переменные окружения
- Никогда не коммить токены в git
- Используй Render Environment Variables
- Регулярно обновляй токены

### Webhook безопасность
- Webhook URL должен быть HTTPS
- Проверяй подпись Telegram (опционально)

## 📞 Поддержка

### Если что-то не работает:
1. Проверь логи в Render Dashboard
2. Проверь статус в BetterStack
3. Используй `/health` и `/status` эндпоинты
4. Проверь переменные окружения

### Полезные ссылки:
- [Render Documentation](https://render.com/docs)
- [BetterStack Documentation](https://betterstack.com/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

🎉 **Поздравляю! Твой Weather Bot теперь работает 24/7 с полным мониторингом!**

# 🚀 Пошаговый деплой на Render.com (ПРАВИЛЬНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ)

## ⚠️ ВАЖНО: Правильный порядок действий!

Render.com требует определенной последовательности. Сначала веб-сервис, потом база данных.

## 📋 Шаг 1: Создание веб-сервиса

### 1.1 Заходим на Render.com
1. Перейди на https://render.com
2. Нажми **"Get Started for Free"** или **"Sign Up"**
3. Зарегистрируйся через GitHub (рекомендуется)

### 1.2 Подключаем GitHub репозиторий
1. В Dashboard нажми **"New +"**
2. Выбери **"Web Service"**
3. Нажми **"Connect GitHub"** (если еще не подключен)
4. Найди и выбери репозиторий **"weather-bot"**
5. Нажми **"Connect"**

### 1.3 Настройки веб-сервиса
**Основные настройки:**
- **Name**: `weather-bot` (или любое другое имя)
- **Environment**: `Python 3`
- **Region**: `Frankfurt (EU Central)` (ближе к пользователям)
- **Branch**: `main`
- **Root Directory**: оставь пустым
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Plan:**
- Выбери **"Free"** (0$/месяц, 750 часов)

### 1.4 Переменные окружения (Environment Variables)
Добавь следующие переменные:

```
TELEGRAM_BOT_TOKEN=твой_токен_от_BotFather
WEBHOOK_URL=https://weather-bot.onrender.com/webhook
ENVIRONMENT=production
LOG_LEVEL=INFO
```

⚠️ **ВАЖНО**: Замени `weather-bot` в WEBHOOK_URL на реальное имя твоего сервиса!

### 1.5 Создание сервиса
1. Нажми **"Create Web Service"**
2. Подожди 5-10 минут пока Render соберет и запустит приложение
3. Статус должен стать **"Live"** (зеленый)

## 📋 Шаг 2: Создание базы данных

### 2.1 Создаем PostgreSQL базу
1. В том же Dashboard нажми **"New +"**
2. Выбери **"PostgreSQL"**
3. **Name**: `weather-bot-db`
4. **Database**: `weather_bot` (или оставь по умолчанию)
5. **User**: `weather_user` (или оставь по умолчанию)
6. **Region**: **тот же что и веб-сервис** (Frankfurt EU Central)
7. **Plan**: выбери **"Free"** (1GB, 0$/месяц)
8. Нажми **"Create Database"**

### 2.2 Подключаем базу к веб-сервису
1. Перейди в настройки **веб-сервиса** (не базы данных!)
2. Найди раздел **"Environment Variables"**
3. Нажми **"Add Environment Variable"**
4. **Key**: `DATABASE_URL`
5. **Value**: `${{weather-bot-db.DATABASE_URL}}`

⚠️ **ВАЖНО**: Замени `weather-bot-db` на реальное имя твоей базы данных!

### 2.3 Перезапуск сервиса
1. В настройках веб-сервиса нажми **"Manual Deploy"**
2. Выбери **"Deploy latest commit"**
3. Подожди пока сервис перезапустится

## 📋 Шаг 3: Проверка работоспособности

### 3.1 Проверяем веб-сервис
1. Открой URL твоего сервиса (например: https://weather-bot.onrender.com)
2. Должен показать JSON с информацией о боте
3. Проверь `/health` endpoint: https://weather-bot.onrender.com/health
4. Должен показать `{"status": "healthy"}`

### 3.2 Проверяем базу данных
1. В логах веб-сервиса должно быть: `"Database initialized"`
2. Не должно быть ошибок подключения к БД

### 3.3 Проверяем бота
1. Найди своего бота в Telegram
2. Отправь `/start`
3. Выбери язык
4. Настрой город и время уведомлений

## 🚨 Возможные проблемы и решения

### Проблема: "Build failed"
**Причины:**
- Неправильный Build Command
- Отсутствует requirements.txt
- Ошибки в коде

**Решение:**
1. Проверь Build Command: `pip install -r requirements.txt`
2. Проверь что requirements.txt есть в репозитории
3. Посмотри логи сборки для деталей

### Проблема: "Deploy failed" 
**Причины:**
- Неправильный Start Command
- Отсутствуют переменные окружения
- Ошибки в main.py

**Решение:**
1. Проверь Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
2. Убедись что все переменные окружения добавлены
3. Проверь логи для деталей ошибки

### Проблема: "Database connection failed"
**Причины:**
- База данных не создана
- Неправильная DATABASE_URL
- База и сервис в разных регионах

**Решение:**
1. Убедись что PostgreSQL база создана
2. Проверь DATABASE_URL: `${{имя-базы.DATABASE_URL}}`
3. Убедись что база и сервис в одном регионе

### Проблема: "Webhook not working"
**Причины:**
- Неправильный WEBHOOK_URL
- Telegram не может достучаться до сервиса
- Сервис не отвечает на /webhook

**Решение:**
1. Проверь WEBHOOK_URL в переменных окружения
2. Убедись что сервис доступен извне
3. Проверь логи webhook запросов

## 📊 Мониторинг (опционально)

### BetterStack настройка:
1. Зарегистрируйся на https://betterstack.com
2. Создай новый проект
3. Скопируй Source Token
4. Добавь в переменные окружения: `BETTER_STACK_TOKEN=твой_токен`
5. Настрой Uptime мониторинг на твой `/health` endpoint

## ✅ Финальная проверка

После всех настроек у тебя должно быть:
- ✅ Веб-сервис со статусом "Live"
- ✅ PostgreSQL база данных
- ✅ Все переменные окружения настроены
- ✅ Бот отвечает в Telegram
- ✅ `/health` endpoint возвращает "healthy"

---

🎉 **Поздравляю! Твой Weather Bot работает 24/7 на Render.com!**

# Deployment Checklist for Weather Bot

## Pre-Deployment Checklist

### 1. Prerequisites ✅
- [ ] Python 3.11+ installed locally
- [ ] Git repository created
- [ ] Telegram Bot Token obtained from @BotFather
- [ ] Render.com account created
- [ ] (Optional) BetterStack account for monitoring

### 2. Local Testing ✅
- [ ] Clone/download project files
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Copy `.env.example` to `.env`
- [ ] Set required environment variables in `.env`
- [ ] Run tests: `python test_bot.py`
- [ ] Verify all tests pass
- [ ] Test bot locally (optional): `python main.py`

### 3. Code Repository ✅
- [ ] Push code to GitHub/GitLab repository
- [ ] Ensure `.env` is in `.gitignore` (security)
- [ ] Verify all necessary files are committed
- [ ] Repository is public or accessible to Render.com

## Render.com Deployment Steps

### 1. Database Setup 🗄️
1. **Create PostgreSQL Database**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "PostgreSQL"
   - Choose "Free" plan (1GB storage)
   - Set database name: `weather-bot-db`
   - Region: Choose closest to your users
   - Click "Create Database"

2. **Note Database Details**:
   - Copy the "External Database URL" 
   - Save for later use in web service

### 2. Web Service Setup 🚀
1. **Create Web Service**:
   - Go to Render Dashboard
   - Click "New" → "Web Service"
   - Connect your GitHub/GitLab repository
   - Select the weather bot repository

2. **Configure Service**:
   - **Name**: `weather-bot` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or paid for better performance)

3. **Set Environment Variables**:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
   DATABASE_URL=postgresql://... (from database step)
   WEBHOOK_URL=https://your-service-name.onrender.com/webhook
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   BETTER_STACK_TOKEN=your_token (optional)
   ```

4. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Check logs for any errors

### 3. Post-Deployment Verification ✅

1. **Check Service Health**:
   - Visit: `https://your-service-name.onrender.com/health`
   - Should return status "healthy"
   - Check all health checks pass

2. **Verify Bot Webhook**:
   - Visit: `https://your-service-name.onrender.com/`
   - Should show API information
   - Webhook should be automatically set

3. **Test Bot Functionality**:
   - Send `/start` to your bot in Telegram
   - Verify language selection works
   - Test city selection and weather requests
   - Verify notifications can be enabled

4. **Monitor Logs**:
   - Check Render.com service logs
   - Look for any errors or warnings
   - Verify database connections work

## BetterStack Monitoring Setup (Optional)

### 1. Create BetterStack Account
- Sign up at [BetterStack](https://betterstack.com)
- Create new source for logs
- Copy the source token

### 2. Configure Monitoring
- Add `BETTER_STACK_TOKEN` to Render environment variables
- Set up uptime monitoring for your service URL
- Configure alerts for downtime/errors

### 3. Monitoring Endpoints
- **Health Check**: `https://your-service.onrender.com/health`
- **Status**: `https://your-service.onrender.com/status`
- **Metrics**: `https://your-service.onrender.com/metrics`

## Troubleshooting Common Issues

### Bot Not Responding
1. **Check Webhook URL**:
   - Ensure `WEBHOOK_URL` matches your Render service URL
   - Format: `https://your-service-name.onrender.com/webhook`

2. **Verify Bot Token**:
   - Check `TELEGRAM_BOT_TOKEN` is correct
   - Test token with Telegram Bot API

3. **Check Service Logs**:
   - Go to Render Dashboard → Your Service → Logs
   - Look for startup errors or webhook failures

### Database Connection Issues
1. **Verify DATABASE_URL**:
   - Should start with `postgresql://`
   - Check username, password, host, and database name

2. **Database Permissions**:
   - Ensure database is accessible from web service
   - Check connection limits (free tier has limits)

### Weather API Issues
1. **Open-Meteo API**:
   - No API key required
   - Check internet connectivity from service
   - Verify API response format hasn't changed

2. **Nominatim Rate Limits**:
   - 1 request per second limit
   - Bot includes automatic rate limiting
   - City coordinates are cached

### Performance Issues (Free Tier)
1. **Cold Starts**:
   - Free tier services "sleep" after 15 minutes
   - Keep-alive mechanism pings every 10 minutes
   - First request after sleep may be slow

2. **Database Connections**:
   - Free PostgreSQL has connection limits
   - Bot uses connection pooling
   - Monitor connection usage

## Maintenance Tasks

### Regular Monitoring
- [ ] Check service uptime weekly
- [ ] Review error logs monthly
- [ ] Monitor database storage usage
- [ ] Verify notification delivery

### Updates and Improvements
- [ ] Keep dependencies updated
- [ ] Monitor for API changes
- [ ] Add new features based on user feedback
- [ ] Optimize performance as needed

### Backup Strategy
- [ ] Database backups (Render provides automatic backups)
- [ ] Code repository backups
- [ ] Environment variables documentation

## Security Considerations

### Environment Variables
- [ ] Never commit `.env` files to repository
- [ ] Use Render's environment variable system
- [ ] Rotate tokens periodically

### API Security
- [ ] Bot token kept secure
- [ ] Database credentials protected
- [ ] Monitor for unusual activity

### User Data
- [ ] Minimal data collection (only necessary info)
- [ ] Secure database storage
- [ ] GDPR compliance considerations

## Success Metrics

### Technical Metrics
- [ ] Uptime > 99%
- [ ] Response time < 2 seconds
- [ ] Error rate < 1%
- [ ] Successful notification delivery > 95%

### User Metrics
- [ ] Daily active users
- [ ] Notification engagement
- [ ] User retention
- [ ] Feature usage statistics

## Support and Documentation

### For Users
- [ ] Bot includes help command
- [ ] Clear error messages
- [ ] Intuitive interface

### For Developers
- [ ] Code documentation
- [ ] API endpoint documentation
- [ ] Troubleshooting guides
- [ ] Monitoring dashboards

---

## Quick Reference

### Important URLs
- **Service**: `https://your-service-name.onrender.com`
- **Health Check**: `https://your-service-name.onrender.com/health`
- **Webhook**: `https://your-service-name.onrender.com/webhook`
- **Admin Status**: `https://your-service-name.onrender.com/status`

### Key Commands
```bash
# Local testing
python test_bot.py

# Local development
python main.py

# Check logs (Render Dashboard)
# Monitor → Logs → Your Service
```

### Emergency Contacts
- Render.com Support: [support.render.com](https://support.render.com)
- Telegram Bot API: [core.telegram.org/bots/api](https://core.telegram.org/bots/api)
- Open-Meteo API: [open-meteo.com](https://open-meteo.com)

---

**🎉 Congratulations! Your Weather Bot is now deployed and ready to serve users with daily weather notifications!**

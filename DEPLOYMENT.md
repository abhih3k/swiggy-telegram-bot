# Deployment Guide

## GitHub Repository
Your code is now live at: **https://github.com/abhih3k/swiggy-telegram-bot**

## Deploy to Railway (Step-by-Step)

### Option 1: Quick Deploy with Railway Button

Click this button to deploy directly:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/abhih3k/swiggy-telegram-bot)

### Option 2: Manual Deployment

1. **Sign up/Login to Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with your GitHub account

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `abhih3k/swiggy-telegram-bot`

3. **Configure Deployment**
   - Railway will auto-detect Python
   - It will use the `Procfile` to run: `python sm_swiggy.py`
   - Python version from `runtime.txt`: 3.11.6

4. **Deploy**
   - Click "Deploy Now"
   - Wait 2-3 minutes for deployment
   - Your bot will be running 24/7!

5. **Check Deployment Logs**
   - Click on your project
   - Go to "Deployments" tab
   - Check logs to see: "✅ Bot running..."

## Environment Variables (Optional - For Security)

Currently, the bot token is hardcoded. For better security:

1. In Railway dashboard → Select your project
2. Go to "Variables" tab
3. Add variable:
   - Key: `BOT_TOKEN`
   - Value: `8257175809:AAEShGpg_tnhrW0V4Fj_dQomuH1AsKVazgk`

4. Update `sm_swiggy.py` line 26:
   ```python
   import os
   BOT_TOKEN = os.getenv("BOT_TOKEN", "8257175809:AAEShGpg_tnhrW0V4Fj_dQomuH1AsKVazgk")
   ```

5. Redeploy from Railway dashboard

## Verify Bot is Running

1. Open Telegram
2. Search for your bot
3. Send `/start` command
4. You should see the welcome message!

## Troubleshooting

### Bot not responding?
- Check Railway deployment logs
- Ensure bot token is correct
- Verify the bot is running (should see "Bot running..." in logs)

### Deployment failed?
- Check Railway build logs
- Ensure `requirements.txt` has correct dependencies
- Verify Python version compatibility

## Update Your Bot

To push updates:

```bash
cd c:\Users\MSI\Desktop\swiggy
git add .
git commit -m "Your update message"
git push
```

Railway will automatically redeploy!

## Cost

Railway offers:
- **Free tier**: 500 hours/month (perfect for 24/7 bot)
- **Pro plan**: $5/month (if you exceed free tier)

Your bot should run perfectly on the free tier!

## Support

If you need help:
- Check Railway logs for errors
- Verify bot token is active in BotFather
- Ensure all files are committed to GitHub

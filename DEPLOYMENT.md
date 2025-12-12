# Healing Guru - Deployment Guide

## 🚀 Deploy to Railway (Free)

### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Sign up with GitHub (recommended)

### Step 2: Deploy Your App
1. Click "Deploy from GitHub repo"
2. Connect your GitHub account
3. Push your code to GitHub first (see below)
4. Select your repository
5. Railway will automatically detect it's a Python app and deploy it

### Step 3: Get Your URL
- Railway will give you a URL like: `https://healingguru-production.up.railway.app`
- Share this URL with anyone - works worldwide!
- Automatically includes HTTPS (required for PWA)

## 📦 Push to GitHub First

```bash
cd ~/healing_guru_app
git init
git add .
git commit -m "Initial commit - Healing Guru app"

# Create new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/healing-guru.git
git push -u origin main
```

## Alternative: Deploy Directly from Local

```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Login and deploy
railway login
railway init
railway up
```

## Other Free Options

### Render.com
- Free tier: 750 hours/month
- URL: `https://healingguru.onrender.com`
- HTTPS included

### Fly.io
- Free tier: 3 small apps
- URL: `https://healingguru.fly.dev`
- Requires credit card (not charged on free tier)

### PythonAnywhere
- Free tier: 1 web app
- URL: `https://yourusername.pythonanywhere.com`
- Manual setup required

## 💰 Add Payments After Deployment

Once live with HTTPS, add Stripe:
1. Create Stripe account
2. Add payment page
3. Gate access to chat after payment

Need help with any step?

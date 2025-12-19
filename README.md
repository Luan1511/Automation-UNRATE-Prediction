# UNRATE Forecast Web App

Automated US Unemployment Rate forecasting web application with email notifications.

## Features

- 📊 **Auto-fetch FRED data** - Weekly updates every Monday
- 🤖 **ARIMA Forecasting** - Next month prediction using ARIMA(2,1,2)
- 📧 **Email Notifications** - Biweekly forecast emails to subscribers
- 🚀 **Railway Ready** - Configured for easy deployment

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `FRED_API_KEY` - Get from https://fred.stlouisfed.org/docs/api/api_key.html
- `EMAIL_USER` - Your Gmail address
- `EMAIL_PASSWORD` - Gmail app password (not your account password!)
- `SECRET_KEY` - Random secret key for Flask

### 3. Gmail App Password Setup

1. Enable 2-factor authentication on your Gmail account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an app password for "Mail"
4. Use this password in `EMAIL_PASSWORD`

### 4. Run Locally

```bash
python app.py
```

Visit http://localhost:5000

## Deploy to Railway

### Method 1: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Set environment variables
railway variables set FRED_API_KEY=your_key_here
railway variables set EMAIL_USER=your_email@gmail.com
railway variables set EMAIL_PASSWORD=your_app_password
railway variables set SECRET_KEY=your_secret_key

# Deploy
railway up
```

### Method 2: GitHub Integration

1. Push code to GitHub repository
2. Go to https://railway.app
3. Create new project from GitHub repo
4. Add environment variables in Railway dashboard
5. Deploy automatically

## Scheduled Tasks

- **Weekly Data Fetch**: Every Monday at 9:00 AM
- **Biweekly Emails**: Every other Monday at 10:00 AM

## API Endpoints

- `GET /` - Home page with latest forecast
- `POST /api/subscribe` - Subscribe to email notifications
- `POST /api/unsubscribe` - Unsubscribe from emails
- `GET /api/forecast` - Get latest forecast JSON
- `POST /api/trigger-fetch` - Manual trigger for data fetch (testing)

## Project Structure

```
unrate_forecast_web/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Procfile           # Railway deployment config
├── railway.json       # Railway build config
├── .env.example       # Environment variables template
├── utils/
│   ├── __init__.py
│   ├── fred_fetcher.py    # FRED API integration
│   ├── forecast.py        # ARIMA forecasting
│   └── email_sender.py    # Email notifications
├── templates/
│   └── index.html     # Home page template
├── static/
│   └── style.css      # Styling
└── data/
    ├── subscribers.json       # Email subscribers (auto-generated)
    └── latest_forecast.json   # Latest forecast (auto-generated)
```

## Notes

- Data folder is created automatically on first run
- Initial forecast is generated on first startup
- Scheduler runs in background using APScheduler
- Email uses Gmail SMTP (can be changed in email_sender.py)

## Troubleshooting

### Emails not sending
- Check EMAIL_USER and EMAIL_PASSWORD are correct
- Ensure Gmail app password is used (not account password)
- Check Gmail allows "less secure apps" or use app password

### Scheduled tasks not running
- Check logs for scheduler errors
- Verify server timezone settings
- Test with `/api/trigger-fetch` endpoint

### Railway deployment issues
- Ensure all environment variables are set
- Check Railway logs for errors
- Verify Procfile is correct

## License

MIT

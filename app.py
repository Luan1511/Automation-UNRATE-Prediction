"""
UNRATE Forecast Web App
Auto-fetch FRED data weekly, forecast with ARIMA, send email notifications
"""

from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
import json
import logging

from utils.fred_fetcher import fetch_fred_data
from utils.forecast import generate_arima_forecast
from utils.email_sender import send_forecast_email

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data storage
SUBSCRIBERS_FILE = 'data/subscribers.json'
FORECAST_FILE = 'data/latest_forecast.json'

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()


def load_subscribers():
    """Load subscribers from JSON file"""
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_subscribers(subscribers):
    """Save subscribers to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open(SUBSCRIBERS_FILE, 'w') as f:
        json.dump(subscribers, f, indent=2)


def save_forecast(forecast_data):
    """Save forecast to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open(FORECAST_FILE, 'w') as f:
        json.dump(forecast_data, f, indent=2)


def load_forecast():
    """Load latest forecast"""
    if os.path.exists(FORECAST_FILE):
        with open(FORECAST_FILE, 'r') as f:
            return json.load(f)
    return None


def weekly_data_fetch():
    """Fetch FRED data weekly and generate forecast"""
    logger.info("Starting weekly data fetch and forecast generation")
    try:
        # Fetch data from FRED
        data = fetch_fred_data()
        
        # Generate ARIMA forecast
        forecast = generate_arima_forecast(data)
        
        # Save forecast
        forecast_data = {
            'date': datetime.now().isoformat(),
            'forecast_value': float(forecast['value']),
            'forecast_month': forecast['month'],
            'current_value': float(data['current_value']),
            'current_month': data['current_month']
        }
        save_forecast(forecast_data)
        
        logger.info(f"Forecast generated: {forecast_data}")
        
    except Exception as e:
        logger.error(f"Error in weekly data fetch: {str(e)}")


def biweekly_email_notification():
    """Send email notifications biweekly"""
    logger.info("Starting biweekly email notification")
    try:
        subscribers = load_subscribers()
        forecast = load_forecast()
        
        if not forecast:
            logger.warning("No forecast available to send")
            return
        
        if not subscribers:
            logger.info("No subscribers to notify")
            return
        
        # Send emails
        for subscriber in subscribers:
            try:
                send_forecast_email(subscriber['email'], forecast)
                logger.info(f"Email sent to {subscriber['email']}")
            except Exception as e:
                logger.error(f"Failed to send email to {subscriber['email']}: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error in biweekly email notification: {str(e)}")


# Schedule tasks
# Weekly data fetch: Every Monday at 9 AM
scheduler.add_job(
    func=weekly_data_fetch,
    trigger="cron",
    day_of_week='mon',
    hour=9,
    minute=0,
    id='weekly_fetch'
)

# Biweekly email: Every other Monday at 10 AM
scheduler.add_job(
    func=biweekly_email_notification,
    trigger="cron",
    day_of_week='mon',
    week='*/2',
    hour=10,
    minute=0,
    id='biweekly_email'
)


@app.route('/')
def index():
    """Home page"""
    forecast = load_forecast()
    return render_template('index.html', forecast=forecast)


@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    """Subscribe to email notifications"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        subscribers = load_subscribers()
        
        # Check if already subscribed
        if any(s['email'] == email for s in subscribers):
            return jsonify({'message': 'Already subscribed'}), 200
        
        # Add subscriber
        subscribers.append({
            'email': email,
            'subscribed_at': datetime.now().isoformat()
        })
        save_subscribers(subscribers)
        
        logger.info(f"New subscriber: {email}")
        return jsonify({'message': 'Successfully subscribed'}), 200
        
    except Exception as e:
        logger.error(f"Error in subscribe: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/unsubscribe', methods=['POST'])
def unsubscribe():
    """Unsubscribe from email notifications"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        subscribers = load_subscribers()
        subscribers = [s for s in subscribers if s['email'] != email]
        save_subscribers(subscribers)
        
        logger.info(f"Unsubscribed: {email}")
        return jsonify({'message': 'Successfully unsubscribed'}), 200
        
    except Exception as e:
        logger.error(f"Error in unsubscribe: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/forecast')
def get_forecast():
    """Get latest forecast"""
    forecast = load_forecast()
    if forecast:
        return jsonify(forecast), 200
    return jsonify({'error': 'No forecast available'}), 404


@app.route('/api/trigger-fetch', methods=['POST'])
def trigger_fetch():
    """Manual trigger for data fetch (for testing)"""
    try:
        weekly_data_fetch()
        return jsonify({'message': 'Data fetch triggered'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/forecast-now', methods=['POST'])
def forecast_now():
    """Manual trigger to fetch data and generate forecast immediately"""
    try:
        # Generate latest forecast
        weekly_data_fetch()

        # Load forecast and subscribers
        forecast = load_forecast()
        subscribers = load_subscribers()

        if not forecast:
            return jsonify({'error': 'Forecast generation failed'}), 500

        # Send emails to all subscribers
        emails_sent = 0
        email_errors = []
        for s in subscribers:
            try:
                send_forecast_email(s['email'], forecast)
                emails_sent += 1
            except Exception as e:
                logger.error(f"Failed to send email to {s['email']}: {str(e)}")
                email_errors.append({'email': s['email'], 'error': str(e)})

        return jsonify({
            'message': 'Forecast generated and notifications sent',
            'forecast': forecast,
            'emails_sent': emails_sent,
            'email_errors': email_errors
        }), 200
    except Exception as e:
        logger.error(f"Error in forecast-now: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Run initial fetch if no forecast exists
    if not load_forecast():
        logger.info("No existing forecast, running initial fetch")
        try:
            weekly_data_fetch()
        except Exception as e:
            logger.error(f"Initial fetch failed: {str(e)}")
    
    # Run Flask app
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

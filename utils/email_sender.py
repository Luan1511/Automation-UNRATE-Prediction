"""
Email Sender
Send forecast notifications to subscribers
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


def send_forecast_email(to_email, forecast_data):
    """
    Send forecast email to subscriber
    
    Args:
        to_email: Recipient email address
        forecast_data: Dictionary with forecast information
    """
    # Email configuration
    smtp_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('EMAIL_PORT', 587))
    smtp_user = os.getenv('EMAIL_USER')
    smtp_password = os.getenv('EMAIL_PASSWORD')
    from_email = os.getenv('EMAIL_FROM', smtp_user)
    
    if not smtp_user or not smtp_password:
        raise ValueError("Email credentials not configured")
    
    # Create email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"UNRATE Forecast: {forecast_data['forecast_month']}"
    msg['From'] = from_email
    msg['To'] = to_email
    
    # Email body
    text = f"""
US Unemployment Rate Forecast

Current UNRATE: {forecast_data['current_value']:.2f}% ({forecast_data['current_month']})

Forecast for {forecast_data['forecast_month']}: {forecast_data['forecast_value']:.2f}%

This forecast was generated using ARIMA model on {forecast_data['date'][:10]}.

---
To unsubscribe, visit: https://your-app-url.railway.app/unsubscribe?email={to_email}
    """
    
    html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2E86AB;">📊 US Unemployment Rate Forecast</h2>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p style="margin: 5px 0;"><strong>Current UNRATE:</strong> {forecast_data['current_value']:.2f}% ({forecast_data['current_month']})</p>
            <p style="margin: 5px 0; font-size: 18px; color: #2E86AB;"><strong>Forecast for {forecast_data['forecast_month']}:</strong> {forecast_data['forecast_value']:.2f}%</p>
        </div>
        
        <p style="font-size: 12px; color: #666;">
            This forecast was generated using ARIMA model on {forecast_data['date'][:10]}.
        </p>
        
        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
        
        <p style="font-size: 11px; color: #999;">
            To unsubscribe, <a href="https://your-app-url.railway.app/unsubscribe?email={to_email}">click here</a>
        </p>
    </div>
</body>
</html>
    """
    
    # Attach both plain text and HTML versions
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    
    # Send email
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)


if __name__ == '__main__':
    # Test
    from dotenv import load_dotenv
    load_dotenv()
    
    test_forecast = {
        'current_value': 4.3,
        'current_month': '2025-07',
        'forecast_value': 4.25,
        'forecast_month': '2025-08',
        'date': '2025-07-15T10:00:00'
    }
    
    test_email = os.getenv('EMAIL_USER')
    if test_email:
        send_forecast_email(test_email, test_forecast)
        print(f"Test email sent to {test_email}")

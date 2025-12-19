"""
ARIMA Forecast Generator
Generate next month UNRATE forecast using ARIMA
"""

from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta


def generate_arima_forecast(data_dict):
    """
    Generate ARIMA forecast for next month
    
    Args:
        data_dict: Dictionary with 'data' (DataFrame), 'current_value', 'current_month'
    
    Returns:
        Dictionary with forecast value and month
    """
    df = data_dict['data']
    
    # Fit ARIMA model (2, 1, 2)
    model = ARIMA(df['value'], order=(2, 1, 2))
    fitted_model = model.fit()
    
    # Forecast next month
    forecast = fitted_model.forecast(steps=1)
    forecast_value = float(forecast.iloc[0])
    
    # Calculate next month
    current_date = df['date'].iloc[-1]
    next_month = current_date + relativedelta(months=1)
    forecast_month = next_month.strftime('%Y-%m')
    
    return {
        'value': forecast_value,
        'month': forecast_month,
        'model': 'ARIMA(2,1,2)',
        'generated_at': datetime.now().isoformat()
    }


if __name__ == '__main__':
    # Test with sample data
    from fred_fetcher import fetch_fred_data
    from dotenv import load_dotenv
    load_dotenv()
    
    data = fetch_fred_data()
    forecast = generate_arima_forecast(data)
    
    print(f"Current: {data['current_value']}% ({data['current_month']})")
    print(f"Forecast: {forecast['value']:.3f}% ({forecast['month']})")

"""
FRED Data Fetcher
Fetch UNRATE data from FRED API
"""

from fredapi import Fred
import pandas as pd
import os
from datetime import datetime


def fetch_fred_data():
    """Fetch latest UNRATE data from FRED"""
    api_key = os.getenv('FRED_API_KEY')
    
    if not api_key:
        raise ValueError("FRED_API_KEY not set in environment variables")
    
    fred = Fred(api_key=api_key)
    
    # Fetch UNRATE series
    unrate = fred.get_series('UNRATE')
    
    # Convert to DataFrame
    df = pd.DataFrame({'date': unrate.index, 'value': unrate.values})
    df['date'] = pd.to_datetime(df['date'])
    
    # Get current (latest) value
    current_value = df['value'].iloc[-1]
    current_month = df['date'].iloc[-1].strftime('%Y-%m')
    
    return {
        'data': df,
        'current_value': current_value,
        'current_month': current_month,
        'last_updated': datetime.now().isoformat()
    }


if __name__ == '__main__':
    # Test
    from dotenv import load_dotenv
    load_dotenv()
    
    data = fetch_fred_data()
    print(f"Current UNRATE: {data['current_value']}% ({data['current_month']})")
    print(f"Total records: {len(data['data'])}")

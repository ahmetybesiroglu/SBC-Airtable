import os
from pyairtable import Api
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from scipy.stats import norm
from dateutil.relativedelta import relativedelta

# Load environment variables from .env file
load_dotenv()

# Retrieve Airtable credentials from environment variables
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = os.getenv('BASE_ID')
TRANCHES_TABLE_ID = os.getenv('TRANCHES_TABLE_ID')
OPTION_VALUATIONS_TABLE_ID = os.getenv('OPTION_VALUATIONS_TABLE_ID')
VOLATILITY_DATA_TABLE_ID = os.getenv('VOLATILITY_DATA_TABLE_ID')
PUBLIC_COMP_SET_TABLE_ID = os.getenv('PUBLIC_COMP_SET_TABLE_ID')

# Initialize the API client
api = Api(AIRTABLE_API_KEY)

# Initialize Airtable tables
tranches_table = api.table(BASE_ID, TRANCHES_TABLE_ID)
option_valuations_table = api.table(BASE_ID, OPTION_VALUATIONS_TABLE_ID)
volatility_data_table = api.table(BASE_ID, VOLATILITY_DATA_TABLE_ID)
public_comp_set_table = api.table(BASE_ID, PUBLIC_COMP_SET_TABLE_ID)

# Define functions for fetching data and calculations
def calculate_volatility(ticker, start_date, end_date, frequency='daily'):
    data = yf.download(ticker, start=start_date, end=end_date, interval='1d')

    if data.empty:
        raise ValueError(f"No data found for {ticker} from {start_date} to {end_date}")

    adj_close = data['Adj Close']

    if frequency == 'daily':
        prices = adj_close
        annual_factor = np.sqrt(252)
    elif frequency == 'weekly':
        prices = adj_close.resample('W-FRI').last()
        annual_factor = np.sqrt(52)
    elif frequency == 'monthly':
        prices = adj_close.resample('M').last()
        annual_factor = np.sqrt(12)
    else:
        raise ValueError("Invalid frequency. Use 'daily', 'weekly', or 'monthly'.")

    log_returns = np.log(prices / prices.shift(1)).dropna()
    volatility = log_returns.std() * annual_factor
    return round(volatility, 4)

def fetch_treasury_yield(ticker, date):
    target_date = datetime.strptime(date, '%Y-%m-%d')
    start_date = target_date - timedelta(days=7)
    end_date = target_date + timedelta(days=1)
    data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    
    if data.empty:
        raise ValueError(f"No data found for {ticker} around {date}")
    
    if date in data.index.strftime('%Y-%m-%d'):
        latest_yield = data.loc[date, 'Close']
    else:
        latest_yield = data['Close'].iloc[-1]
    
    return round(latest_yield / 100, 4)

def black_scholes(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    option_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return round(option_price, 4)

# Fetch all valuation records
valuation_records = option_valuations_table.all()

# Sort valuation records by valuation_id
sorted_valuation_records = sorted(valuation_records, key=lambda x: x['fields'].get('valuation_id', 0))

# Process each sorted valuation record
for valuation_record in sorted_valuation_records:
    valuation = valuation_record['fields']

    # Check if option_value is already calculated
    if 'option_value' in valuation and valuation['option_value'] is not None:
        continue

    print("Processing Valuation Record:", valuation)

    # Get the necessary fields from the valuation record
    valuation_date = valuation['valuation_date']
    expected_term = valuation['expected_term']
    
    # Use .get() to safely handle missing 'public_comp_set'
    public_comps = valuation.get('public_comp_set', [])
    volatility_frequency = valuation['volatility_frequency']

    # Check if public_comps is empty and handle it gracefully
    if not public_comps:
        print(f"Warning: No public_comp_set provided for valuation record {valuation['valuation_id']}. Skipping this record.")
        continue

    # Calculate the start and end dates for the volatility calculation
    end_date = datetime.strptime(valuation_date, '%Y-%m-%d')
    start_date = (end_date - timedelta(days=int(expected_term * 365))).strftime('%Y-%m-%d')

    # Calculate volatility for each ticker
    volatilities = []
    for comp_id in public_comps:
        comp_record = public_comp_set_table.get(comp_id)  # Updated to use the public_comp_set_table instance
        ticker = comp_record['fields']['ticker']
        try:
            volatility = calculate_volatility(ticker, start_date, valuation_date, volatility_frequency.lower())
            volatilities.append({'ticker': ticker, 'comp_id': comp_id, f"{start_date} to {valuation_date}": volatility})
            print(f"Volatility for {ticker}: {volatility}")
        except Exception as e:
            print(f"Error for {ticker} from {start_date} to {valuation_date}: {e}")

    # Calculate average volatility if there are any valid volatilities
    if volatilities:
        average_volatility = round(np.mean([vol[f"{start_date} to {valuation_date}"] for vol in volatilities]), 4)
    else:
        average_volatility = float('nan')

    print(f"Average Volatility: {average_volatility}")

    # Fetch treasury yields and extrapolate to expected term
    treasury_tickers = {
        "1-year": "^IRX",
        "5-year": "^FVX",
        "10-year": "^TNX",
        "30-year": "^TYX"
    }
    treasury_yields = {}
    for term, ticker in treasury_tickers.items():
        try:
            treasury_yields[term] = fetch_treasury_yield(ticker, valuation_date)
        except Exception as e:
            print(f"Error fetching treasury yield {term}: {e}")

    # Extrapolate yield to match expected term
    if expected_term <= 1:
        risk_free_rate = treasury_yields.get("1-year", np.nan)
    elif expected_term <= 5:
        risk_free_rate = treasury_yields.get("1-year", np.nan) + (treasury_yields.get("5-year", np.nan) - treasury_yields.get("1-year", np.nan)) * (expected_term - 1) / 4
    elif expected_term <= 10:
        risk_free_rate = treasury_yields.get("5-year", np.nan) + (treasury_yields.get("10-year", np.nan) - treasury_yields.get("5-year", np.nan)) * (expected_term - 5) / 5
    else:
        risk_free_rate = treasury_yields.get("10-year", np.nan) + (treasury_yields.get("30-year", np.nan) - treasury_yields.get("10-year", np.nan)) * (expected_term - 10) / 20

    print(f"Extrapolated risk-free rate for expected term {expected_term} years: {risk_free_rate}")

    # Get the stock price and strike price from the valuation record
    share_price = valuation['share_price']
    strike_price = valuation['strike_price']

    # Calculate the option value using Black-Scholes
    option_value = black_scholes(share_price, strike_price, expected_term, risk_free_rate, average_volatility)
    print(f"Calculated option value: {option_value}")

    # Store volatility in the Volatility Data table (skip computed fields)
# Store volatility in the Volatility Data table (skip computed fields)
    vol_ids = []
    for vol in volatilities:
        ticker = vol['ticker']
        comp_id = vol['comp_id']
        volatility = vol[f"{start_date} to {valuation_date}"]

        # Exclude computed fields (like 'date_from') in the creation payload
        try:
            vol_record = volatility_data_table.create({
                'ticker': [comp_id],  # Link to Public Comp Set table using comp_id
                'volatility': volatility
            })
            print("Volatility record created:", vol_record)
            vol_ids.append(vol_record['id'])
        except Exception as e:
            print(f"Error creating volatility record for {ticker}: {e}")


    # Update the Valuations table with the option value, risk-free rate, and link to volatilities
    try:
        update_fields = {
            'option_value': option_value,
            'volatility_id': vol_ids,  # Linking the created volatility records
            'risk_free_rate': risk_free_rate  # Adding the calculated risk-free rate
        }
        
        updated_valuation = option_valuations_table.update(valuation_record['id'], update_fields)
        print("Updated valuation record:", updated_valuation)
    except Exception as e:
        print(f"Error updating valuation record: {e}")

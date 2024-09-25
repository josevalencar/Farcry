import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import MinMaxScaler
import warnings
import os
import streamlit_shadcn_ui as ui
import altair as alt
import locale
import requests 
import yfinance as yf
from datetime import datetime, timedelta

# Suprimir avisos
warnings.filterwarnings("ignore")

st.set_page_config(layout="wide")

# Combined CSS to hide Streamlit's menu and header, and customize sliders
custom_styles = """
    <style>
    /* Hide Streamlit menu and header */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .buy-card {
        background-color: #e0ffe0;
        color: #008000;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
    }
    .dont-buy-card {
        background-color: #ffe0e0;
        color: #ff0000;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
    }
    </style>
"""

# Apply the combined CSS styles using markdown with HTML allowed
st.markdown(custom_styles, unsafe_allow_html=True)

def get_yesterdays_value(ticker_symbol):
    """
    Fetch yesterday's closing price for a given cryptocurrency using yfinance.
    """
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    # Fetch historical data for the past 2 days to ensure we get the last valid closing price
    data = yf.download(ticker_symbol, start=yesterday.strftime('%Y-%m-%d'), end=today.strftime('%Y-%m-%d'))
    
    # Return the closing price from yesterday, if available
    if not data.empty:
        return data['Close'].iloc[-1]  # Last available closing price
    return None

# Fetch yesterday's value for BTC and ETH
btc_yesterday_value = get_yesterdays_value('BTC-USD')
eth_yesterday_value = get_yesterdays_value('ETH-USD')

btc_yesterday_formatted = f"${btc_yesterday_value:,.2f}" if btc_yesterday_value else "N/A"
eth_yesterday_formatted = f"${eth_yesterday_value:,.2f}" if eth_yesterday_value else "N/A"

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    st.error("Locale setting 'pt_BR.UTF-8' is not supported on this system. Please ensure your environment supports this locale.")

def load_regression_model():
    pass

# Interface Streamlit
st.title('Farcry: Cryptocurrency Forecasting Tool')

value = ui.tabs(options=['Dashboard', 'Forecasting', 'What-If', 'History'], default_value='Dashboard', key="kanaries")
st.header(value)

if value == "Dashboard":
    st.write('Welcome to the Farcry Dashboard. Here you can view the latest predictions and recommendations for Bitcoin (BTC) and Ethereum (ETH), using our Regression Model.')

    # Fetch the predictions for BTC and ETH from the API
    prediction_btc = None
    prediction_eth = None
    try:
        response = requests.get("http://127.0.0.1:8000/predictRegression")
        if response.status_code == 200:
            data = response.json()
            prediction_btc = data.get('Prediction BTC', 0)  # Extract the BTC prediction value
            prediction_eth = data.get('Prediction ETH', 0)  # Extract the ETH prediction value
        else:
            st.error(f"Error fetching prediction: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch predictions: {e}")

    # Format the predictions as currency if available
    prediction_btc_formatted = f"${prediction_btc:,.2f}" if prediction_btc else "N/A"
    prediction_eth_formatted = f"${prediction_eth:,.2f}" if prediction_eth else "N/A"

    # Determine if the user should BUY or DON'T BUY based on prediction vs yesterday's value
    def recommendation_card(prediction, yesterday_value, crypto_name):
        if prediction > yesterday_value:
            return f'<div class="buy-card"><strong>BUY</strong> more {crypto_name}</div>'
        else:
            return f'<div class="dont-buy-card"><strong>DON\'T BUY</strong> more {crypto_name}</div>'

    # Create two columns for the metrics
    cols = st.columns(2)

    with cols[0]:
        ui.metric_card(
        title="Bitcoin (BTC) Today's Prediction",
        content=prediction_btc_formatted,  # Insert the BTC prediction here
        description=f"Yesterday's value: {btc_yesterday_formatted}",  # Insert BTC's yesterday value here
        key=f"1"
        )
        # Show recommendation card for BTC
        if prediction_btc and btc_yesterday_value:
            st.markdown(recommendation_card(prediction_btc, btc_yesterday_value, "BTC"), unsafe_allow_html=True)

    with cols[1]:
        ui.metric_card(
        title="Ethereum (ETH) Today's Prediction",
        content=prediction_eth_formatted,  # Insert the ETH prediction here
        description=f"Yesterday's value: {eth_yesterday_formatted}",  # Insert ETH's yesterday value here
        key=f"2"
        )
        # Show recommendation card for ETH
        if prediction_eth and eth_yesterday_value:
            st.markdown(recommendation_card(prediction_eth, eth_yesterday_value, "ETH"), unsafe_allow_html=True)

elif value == "Forecasting":
    st.write('Previsões de Série Temporal (ARIMA)')

elif value == "What-If":
    st.write('Análise What-If com Rede Neural')

elif value == "History":
    st.write('Logs from the system')

# st.sidebar.markdown("---")
st.sidebar.info("Farcry is the all-in-one cryptocurrency forecasting tool that uses Machine Learning models to predict future values, so that you can either buy or sell your cryptos.")
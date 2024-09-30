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

warnings.filterwarnings("ignore")

st.set_page_config(layout="wide")

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
        margin-bottom: 20px;  /* Added padding below */
    }
    .dont-buy-card {
        background-color: #ffe0e0;
        color: #ff0000;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 20px;  /* Added padding below */
    }
    </style>
"""

st.markdown(custom_styles, unsafe_allow_html=True)

def get_yesterdays_value(ticker_symbol):
    """
    Fetch yesterday's closing price for a given cryptocurrency using yfinance.
    """
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    for attempt in range(3):
        try:
            data = yf.download(ticker_symbol, start=(yesterday - timedelta(days=attempt)).strftime('%Y-%m-%d'), end=today.strftime('%Y-%m-%d'))

            if not data.empty:
                return data['Close'].iloc[-1] 

        except Exception as e:
            st.error(f"Failed to fetch data for {ticker_symbol}: {e}")

    st.warning(f"Could not fetch data for {ticker_symbol}. Please check the ticker or try again later.")
    return None

btc_yesterday_value = get_yesterdays_value('BTC-USD')
eth_yesterday_value = get_yesterdays_value('ETH-USD')

btc_yesterday_formatted = f"${btc_yesterday_value:,.2f}" if btc_yesterday_value else "N/A"
eth_yesterday_formatted = f"${eth_yesterday_value:,.2f}" if eth_yesterday_value else "N/A"

def fetch_time_series():
    try:
        response = requests.get("http://backend:8000/predictTimeSeries")
        if response.status_code == 200:
            data = response.json()
            btc_ts_historical = data.get('BTC', {}).get('historical', {})
            btc_ts_forecast = data.get('BTC', {}).get('forecast', {})
            eth_ts_historical = data.get('ETH', {}).get('historical', {})
            eth_ts_forecast = data.get('ETH', {}).get('forecast', {})
            return btc_ts_historical, btc_ts_forecast, eth_ts_historical, eth_ts_forecast
        else:
            st.error(f"Error fetching prediction: {response.status_code}")
            return None, None, None, None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch predictions: {e}")
        return None, None, None, None
    
def fetch_logs():
    try:
        response = requests.get("http://backend:8000/logs")
        if response.status_code == 200:
            logs = response.json()
            return logs
        else:
            st.error(f"Error fetching logs: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch logs: {e}")
        return []

st.title('Farcry: Cryptocurrency Forecasting Tool')

value = ui.tabs(options=['Dashboard', 'History'], default_value='Dashboard', key="kanaries")
st.header(value)

if value == "Dashboard":
    st.write('Welcome to the Farcry Dashboard. Here you can view the latest predictions and recommendations for Bitcoin (BTC) and Ethereum (ETH)')

    with st.spinner('Fetching the latest predictions, please wait...'):
        prediction_btc = None
        prediction_eth = None
        try:
            response = requests.get("http://backend:8000/predictRegression")
            if response.status_code == 200:
                data = response.json()
                prediction_btc = data.get('Prediction BTC', 0) 
                prediction_eth = data.get('Prediction ETH', 0)  
            else:
                st.error(f"Error fetching prediction: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch predictions: {e}")

    prediction_btc_formatted = f"${prediction_btc:,.2f}" if prediction_btc else "N/A"
    prediction_eth_formatted = f"${prediction_eth:,.2f}" if prediction_eth else "N/A"

    def recommendation_card(prediction, yesterday_value, crypto_name):
        if prediction > yesterday_value:
            return f'<div class="buy-card"><strong>BUY</strong> more {crypto_name}</div>'
        else:
            return f'<div class="dont-buy-card"><strong>DON\'T BUY</strong> more {crypto_name}</div>'

    cols = st.columns(2)

    with st.spinner('Fetching historical and forecasted data, please wait...'):
        btc_ts_historical, btc_ts_forecast, eth_ts_historical, eth_ts_forecast = fetch_time_series()

    with cols[0]:
        ui.metric_card(
        title="Bitcoin (BTC) Today's Prediction",
        content=prediction_btc_formatted, 
        description=f"Yesterday's actual value: {btc_yesterday_formatted}", 
        key=f"1"
        )
        if prediction_btc and btc_yesterday_value:
            st.markdown(recommendation_card(prediction_btc, btc_yesterday_value, "BTC"), unsafe_allow_html=True)

        if btc_ts_historical and btc_ts_forecast:
            forecast_df = pd.DataFrame({
                'Date': list(btc_ts_forecast.keys())[:-3], 
                'Value': list(btc_ts_forecast.values())[:-3], 
                'Type': 'Previsão'
            })

            historical_df = pd.DataFrame({
                'Date': list(btc_ts_historical.keys()),
                'Value': list(btc_ts_historical.values()),
                'Type': 'Histórico'
            })
            
            combined_df = pd.concat([historical_df, forecast_df])

            chart = alt.Chart(combined_df).mark_line().encode(
                x=alt.X('Date:T', title='Data'),
                y=alt.Y('Value:Q', title='Valor'),
                color='Type:N'
            ).properties(
                width=600,
                height=400,
                title=f'Previsão BTC SARIMA'
            )
            
            st.altair_chart(chart, use_container_width=True)
        # st.write(combined_df)

    with cols[1]:
        ui.metric_card(
        title="Ethereum (ETH) Today's Prediction",
        content=prediction_eth_formatted,  
        description=f"Yesterday's actual value: {eth_yesterday_formatted}",  
        key=f"2"
        )
        if prediction_eth and eth_yesterday_value:
            st.markdown(recommendation_card(prediction_eth, eth_yesterday_value, "ETH"), unsafe_allow_html=True)
        
        if eth_ts_historical and eth_ts_forecast:
            forecast_df = pd.DataFrame({
                'Date': list(eth_ts_forecast.keys()),
                'Value': list(eth_ts_forecast.values()),
                'Type': 'Previsão'
            })

            historical_df = pd.DataFrame({
                'Date': list(eth_ts_historical.keys()),
                'Value': list(eth_ts_historical.values()),
                'Type': 'Histórico'
            })

            combined_df = pd.concat([historical_df, forecast_df])

            chart = alt.Chart(combined_df).mark_line().encode(
                x=alt.X('Date:T', title='Data'),
                y=alt.Y('Value:Q', title='Valor'),
                color='Type:N'
            ).properties(
                width=600,
                height=400,
                title=f'Previsão ETH Prophet'
            )

            st.altair_chart(chart, use_container_width=True)

elif value == "History":
    st.write('Logs from the system')

    logs = fetch_logs()

    if logs:
        logs_df = pd.DataFrame(logs)

        logs_df['datetime'] = pd.to_datetime(logs_df['datetime']).dt.strftime('%Y-%m-%d %H:%M:%S')

        st.dataframe(logs_df)

    else:
        st.info("No logs available at the moment.")

st.sidebar.info("Farcry is the all-in-one cryptocurrency forecasting tool that uses Machine Learning models to predict future values, so that you can either buy or sell your cryptos.")
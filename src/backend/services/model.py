import numpy as np
import pickle
from fastapi import HTTPException
import logging
from datetime import datetime, timedelta
import yfinance as yf
from ta import add_all_ta_features
import joblib
import pandas as pd
import os
from supabase import Client
from pycaret.regression import load_model
from statsmodels.tsa.statespace.sarimax import SARIMAXResults
import gzip

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from datetime import datetime

def insert_log(supabase, system, action, code):
    try:
        log_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        log_entry = {
            "datetime": log_timestamp,
            "system": system,
            "action": action,
            "code": code
        }

        supabase.table("logs").insert(log_entry).execute()

    except Exception as e:
        logger.error(f"Error while inserting log: {str(e)}")

def fetch_btc_data():
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    thirty_days_ago = yesterday - timedelta(days=29)
    
    start_date = thirty_days_ago.strftime('%Y-%m-%d')
    end_date = yesterday.strftime('%Y-%m-%d') 
    
    logger.info(f"Fetching BTC data from {start_date} to {end_date}.")
    
    btc_data = yf.download('BTC-USD', start=start_date, end=end_date, interval='1d')
    
    if not btc_data.empty:
        btc_data = btc_data[['Open', 'High', 'Low', 'Close', 'Volume']]
        btc_data['Adj Close'] = btc_data['Close']
        logger.info("Successfully fetched BTC data.")
        return btc_data
    else:
        raise ValueError("No data fetched for BTC")

# Function to fetch Ethereum data for the last 30 days
def fetch_eth_data():
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    thirty_days_ago = yesterday - timedelta(days=29)
    
    start_date = thirty_days_ago.strftime('%Y-%m-%d')
    end_date = yesterday.strftime('%Y-%m-%d')
    
    logger.info(f"Fetching ETH data from {start_date} to {end_date}.")
    
    eth_data = yf.download('ETH-USD', start=start_date, end=end_date, interval='1d')
    
    if not eth_data.empty:
        eth_data = eth_data[['Open', 'High', 'Low', 'Close', 'Volume']]
        eth_data['Adj Close'] = eth_data['Close']
        logger.info("Successfully fetched ETH data.")
        return eth_data
    else:
        raise ValueError("No data fetched for ETH")

# Function to add technical analysis indicators to the DataFrame
def add_technical_indicators(df):
    try:
        logger.info("Adding technical indicators to the data.")
        return add_all_ta_features(
            df, open="Open", high="High", low="Low", close="Close", volume="Volume", fillna=True)
    except Exception as e:
        logger.error(f"Error adding technical indicators: {str(e)}")
        raise

# Preprocess the data before prediction (for both BTC and ETH)
def preprocess_for_prediction(df):
    try:
        logger.info("Starting preprocessing of data.")
        
        if df.shape[0] < 2:
            raise ValueError("Not enough data to compute technical indicators.")
        
        df = add_technical_indicators(df)
        logger.debug(f"Data after adding technical indicators: {df.head()}")

        df = df.drop(['others_dr', 'others_dlr', 'others_cr'], axis=1, errors='ignore')
        df = df.dropna()
        
        logger.info(f"Preprocessed DataFrame columns: {df.columns}")
        logger.info(f"Preprocessed DataFrame shape: {df.shape}")

        return df
    
    except ValueError as ve:
        logger.error(f"Error during preprocessing: {ve}")
        raise ve
    except Exception as e:
        logger.error(f"Unexpected error during preprocessing: {str(e)}")
        raise

# Function to download the model from Supabase Storage using the provided Supabase client
def download_model_from_supabase(supabase, bucket_name: str, model_path: str):
    try:
        logger.info(f"Downloading model from Supabase bucket: {bucket_name}, path: {model_path}")
        response = supabase.storage.from_(bucket_name).download(model_path)
        model_file_path = f"/tmp/{os.path.basename(model_path)}"  # Save the model in a temporary directory
        
        with open(model_file_path, "wb") as f:
            f.write(response)
        
        logger.info(f"Model {model_path} downloaded successfully.")
        return model_file_path
    
    except Exception as e:
        logger.error(f"Error downloading model from Supabase: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download model from Supabase: {str(e)}")

# Function to load the model and make a prediction (for both BTC and ETH)
def load_model_and_predict(supabase, data, bucket_name, model_path):
    try:
        logger.info("Loading pre-trained PyCaret model.")
        
        # Download the model from Supabase
        model_file_path = download_model_from_supabase(supabase, bucket_name, model_path)
        
        # Load the model using PyCaret's load_model function
        model = load_model(model_file_path.replace('.pkl', ''))  # Remove .pkl from file path for PyCaret
        
        logger.info(f"Model loaded successfully.")
        
        latest_data = data.iloc[-1:].fillna(0)
        
        logger.debug("Latest data for prediction:")
        logger.debug(latest_data)
        
        prediction = model.predict(latest_data)
        rounded_prediction = np.round(prediction, 2)
        logger.info(f"Prediction result: {rounded_prediction}")
        
        return rounded_prediction  
    
    except Exception as e:
        logger.error(f"Error during model prediction: {str(e)}")
        raise

# Main function to run the regression prediction for both BTC and ETH
def regression_prediction(supabase=Client):
    try:
        logger.info("Starting regression prediction process for BTC and ETH.")
        
        # BTC Prediction
        btc_df = fetch_btc_data()
        btc_df_processed = preprocess_for_prediction(btc_df)
        btc_prediction = load_model_and_predict(supabase, btc_df_processed, 'regression_models', 'BTC/btc_br_model.pkl')
        
        # ETH Prediction
        eth_df = fetch_eth_data()
        eth_df_processed = preprocess_for_prediction(eth_df)
        eth_prediction = load_model_and_predict(supabase, eth_df_processed, 'regression_models', 'ETH/eth_br_model.pkl')
        
        logger.info("Regression prediction completed successfully for both BTC and ETH.")
        insert_log(supabase, system="model_service", action="predict_regression", code=200)
        return {"Prediction BTC": btc_prediction[0], "Prediction ETH": eth_prediction[0]}

    
    except Exception as e:
        logger.error(f"Error in regression prediction: {str(e)}")
        insert_log(supabase, system="model_service", action="predict_regression", code=500)
        return {"Error": str(e)}
    
def time_series_prediction(supabase):
    logger = logging.getLogger(__name__)
    logger.info("Starting time series prediction process for BTC and ETH")

    try:
        # Model paths and download
        bucket_name = 'time_series_models'
        btc_model_path = 'BTC/btc_sarima_model.pkl.gz'
        eth_model_path = 'ETH/eth_prophet_model.pkl'

        # Fetch historical data
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        btc_data = yf.download('BTC-USD', start=start_date, end=end_date, interval='1d')
        eth_data = yf.download('ETH-USD', start=start_date, end=end_date, interval='1d')

        btc_data['Close_log'] = np.log(btc_data['Close'])

        # Load BTC SARIMA model
        btc_model_file_path = download_model_from_supabase(supabase, bucket_name, btc_model_path)
        with gzip.open(btc_model_file_path, 'rb') as f:
            btc_model = SARIMAXResults.load(f)
            # Assuming btc_data['Close_log'] is your endogenous variable:
            # btc_model.model.endog = btc_data['Close_log'].values
            # btc_model.model.nobs = len(btc_data['Close_log'])
            # btc_model.model.k_endog = 1  # if it's univariate

        # Load ETH Prophet model
        eth_model_file_path = download_model_from_supabase(supabase, bucket_name, eth_model_path)
        with open(eth_model_file_path, 'rb') as f:
            eth_model = pickle.load(f)

        # Make BTC forecast
        btc_forecast_log = btc_model.get_forecast(steps=90)
        btc_forecast = np.exp(btc_forecast_log.predicted_mean)

        btc_forecast_dates = pd.date_range(start=btc_data.index[-1] + timedelta(days=1), periods=90, freq='D')
        btc_forecast_df = pd.DataFrame({'Forecast': btc_forecast}, index=btc_forecast_dates)
        btc_forecast_df = btc_forecast_df.fillna(0)

        # Make ETH forecast
        eth_future_dates = pd.DataFrame({'ds': pd.date_range(start=eth_data.index[-1] + timedelta(days=1), periods=90, freq='D')})
        eth_forecast = eth_model.predict(eth_future_dates)
        eth_forecast.set_index('ds', inplace=True)
        eth_forecast.rename(columns={'yhat': 'Forecast'}, inplace=True)

        # Serialize results
        result = {
            "BTC": {
                "historical": btc_data['Close'].to_dict(),
                "forecast": btc_forecast_df['Forecast'].apply(float).to_dict()
            },
            "ETH": {
                "historical": eth_data['Close'].to_dict(),
                "forecast": eth_forecast['Forecast'].apply(float).to_dict()
            }
        }
        logger.info("Time series prediction completed successfully for both BTC and ETH")
        insert_log(supabase, system="model_service", action="predict_time_series", code=200)
        return result

    except Exception as e:
        logger.error(f"Error in time series prediction: {str(e)}")
        insert_log(supabase, system="model_service", action="predict_time_series", code=500)
        raise Exception(f"Failed to make time series prediction: {str(e)}")
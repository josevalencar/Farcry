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

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Function to fetch Bitcoin data for the last 30 days
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
def regression_prediction(supabase):
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
        return {"Prediction BTC": btc_prediction[0], "Prediction ETH": eth_prediction[0]}
    
    except Exception as e:
        logger.error(f"Error in regression prediction: {str(e)}")
        return {"Error": str(e)}
import numpy as np
import pickle
from fastapi import HTTPException
import logging
from datetime import datetime, timedelta
import yfinance as yf
from ta import add_all_ta_features
import joblib
import pandas as pd

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

# Function to load the model and make a prediction (for both BTC and ETH)
def load_model_and_predict(data, model_path):
    try:
        logger.info("Loading pre-trained model.")
        model = joblib.load(model_path)
        
        logger.info(f"Data shape before prediction: {data.shape}")
        logger.info(f"Model expects {model.n_features_in_} features.")
        
        logger.debug(f"Data columns: {data.columns.tolist()}")
        logger.debug(f"Model feature names: {model.feature_names_in_}") 

        if data.shape[1] != model.n_features_in_:
            logger.error(f"Mismatch! Data has {data.shape[1]} columns but model expects {model.n_features_in_} features.")
            
            missing_columns = set(model.feature_names_in_) - set(data.columns)
            logger.error(f"Missing columns: {missing_columns}")
            
            raise ValueError(f"Expected {model.n_features_in_} features, but got {data.shape[1]}.")

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
def regression_prediction():
    try:
        logger.info("Starting regression prediction process for BTC and ETH.")
        
        # BTC Prediction
        btc_df = fetch_btc_data()
        btc_df_processed = preprocess_for_prediction(btc_df)
        btc_prediction = load_model_and_predict(btc_df_processed, 'utils/btc_br_model.pkl')
        
        # ETH Prediction
        eth_df = fetch_eth_data()
        eth_df_processed = preprocess_for_prediction(eth_df)
        eth_prediction = load_model_and_predict(eth_df_processed, 'utils/eth_br_model.pkl')
        
        logger.info("Regression prediction completed successfully for both BTC and ETH.")
        return {"Prediction BTC": btc_prediction[0], "Prediction ETH": eth_prediction[0]}
    
    except Exception as e:
        logger.error(f"Error in regression prediction: {str(e)}")
        return {"Error": str(e)}

# Running the function
if __name__ == "__main__":
    result = regression_prediction()
    logger.info(f"Result: {result}")
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

# Suprimir avisos
warnings.filterwarnings("ignore")

st.set_page_config(layout="wide")

# Combined CSS to hide Streamlit's menu and header, and customize sliders
custom_styles = """
    <style>
    /* Hide Streamlit menu and header */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""

# Apply the combined CSS styles using markdown with HTML allowed
st.markdown(custom_styles, unsafe_allow_html=True)


try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    st.error("Locale setting 'pt_BR.UTF-8' is not supported on this system. Please ensure your environment supports this locale.")


# Interface Streamlit
st.title('Farcry: Cryptocurrency Forecasting Tool')

value = ui.tabs(options=['Dashboard', 'Forecasting', 'What-If'], default_value='Dashboard', key="kanaries")
st.header(value)

if value == "Dashboard":
    st.write('Dashboard de Análise Financeira')

elif value == "Forecasting":
    st.write('Previsões de Série Temporal (ARIMA)')

elif value == "What-If":
    st.write('Análise What-If com Rede Neural')

# st.sidebar.markdown("---")
st.sidebar.info("Farcry is the all-in-one cryptocurrency forecasting tool that uses Machine Learning models to predict future values, so that you can either buy or sell your cryptos.")
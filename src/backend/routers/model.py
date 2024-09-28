from fastapi import APIRouter, HTTPException, Depends, status
from services.model import regression_prediction
from services.model import time_series_prediction

from supabase import Client
from database.supabase import create_supabase_client

router = APIRouter(tags=["model"])

def get_supabase_client() -> Client:
    return create_supabase_client()

@router.get("/predictRegression/")
async def predict_regression(supabase: Client = Depends(get_supabase_client)):

    prediction_result = regression_prediction(supabase=supabase)
    return prediction_result

@router.get("/predictTimeSeries/")
async def predict_time_series(supabase: Client = Depends(get_supabase_client)):

    prediction_result = time_series_prediction(supabase=supabase)
    return prediction_result
from fastapi import APIRouter, HTTPException, Depends, status
from services.model import regression_prediction

# from supabase import Client

# from database.supabase import create_supabase_client
router = APIRouter(tags=["model"])

# def get_supabase_client() -> Client:
#     return create_supabase_client()

@router.get("/predictRegression/")
# async def predict_regression(data: RegressionInput, supabase: Client = Depends(get_supabase_client)):
async def predict_regression():

    # my_prediction = prediction(knr=knr, supabase=supabase)
    prediction_result = regression_prediction()
    return prediction_result
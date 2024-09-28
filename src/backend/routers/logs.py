from fastapi import APIRouter, HTTPException, Depends, status
from services.logs import get_logs

from supabase import Client
from database.supabase import create_supabase_client

router = APIRouter(tags=["logs"])

def get_supabase_client() -> Client:
    return create_supabase_client()

@router.get("/logs/")
async def return_logs(supabase: Client = Depends(get_supabase_client)):
    logs_result = get_logs(supabase=supabase)
    return logs_result
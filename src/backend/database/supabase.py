from supabase import Client, create_client
import os
import tempfile

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

api_url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

def create_supabase_client():
    supabase: Client = create_client(api_url, key)
    return supabase
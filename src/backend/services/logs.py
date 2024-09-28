def get_logs(supabase):
    try:
        response = supabase.table("logs").select("datetime, system, action, code").execute()
        return response.data
    except AttributeError as e:
        print(f"AttributeError: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
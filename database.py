import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.getenv("SUPABASE_URL", "")
key: str = os.getenv("SUPABASE_KEY", "")

def get_supabase() -> Client:
    if not url or not key:
        raise ValueError("Supabase URL or Key not set in environment variables.")
    return create_client(url, key)

def get_campaign_mappings():
    supabase = get_supabase()
    response = supabase.table("campaign_mappings").select("*").execute()
    return {
        str(row["sender_name"]).strip().lower(): {
            "campaign_id": row["campaign_id"],
            "linkedin_account_id": row.get("linkedin_account_id", 0),
            "original_name": row["sender_name"] # Keep original name for UI display
        }
        for row in response.data
    }

def check_duplicate_lead(linkedin_url: str, sender: str) -> bool:
    supabase = get_supabase()
    response = supabase.table("leads").select("id").eq("linkedin_url", linkedin_url).eq("sender", sender).execute()
    return len(response.data) > 0

def insert_lead(lead_data: dict):
    supabase = get_supabase()
    response = supabase.table("leads").insert(lead_data).execute()
    return response.data

def get_pending_leads():
    supabase = get_supabase()
    response = supabase.table("leads").select("*").eq("status", "pending").execute()
    return response.data

def update_lead_status(lead_id: str, status: str):
    supabase = get_supabase()
    import datetime
    now = datetime.datetime.utcnow().isoformat()
    response = supabase.table("leads").update({"status": status, "processed_at": now}).eq("id", lead_id).execute()
    return response.data

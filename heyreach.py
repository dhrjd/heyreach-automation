import os
import requests
from dotenv import load_dotenv

load_dotenv()

def push_lead_to_heyreach(campaign_id: int, linkedin_account_id: int, first_name: str, last_name: str, linkedin_url: str, company_name: str) -> bool:
    """
    Pushes a lead to a Heyreach campaign.
    Returns True if successful, False otherwise.
    """
    api_key = os.getenv("HEYREACH_API_KEY")
    if not api_key:
        print("Heyreach API key not configured.")
        return False
        
    url = "https://api.heyreach.io/api/public/campaign/AddLeadsToCampaign"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "campaignId": int(campaign_id),
        "accountLeadPairs": [
            {
                "linkedInAccountId": int(linkedin_account_id),
                "lead": {
                    "firstName": first_name,
                    "lastName": last_name if last_name else "a",
                    "companyName": company_name,
                    "profileUrl": linkedin_url
                }
            }
        ],
        "resumeFinishedCampaign": False,
        "resumePausedCampaign": True
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        # Heyreach returns the number of leads added as plain text (e.g., '1' or '0')
        if response.text.strip() == '0':
            print(f"Heyreach returned 0 (Lead was silently rejected). URL might be invalid or lead is a duplicate. URL: {linkedin_url}")
            return False
            
        return True
    except Exception as e:
        print(f"Heyreach API Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

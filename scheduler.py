import datetime
import pytz
from database import get_pending_leads, update_lead_status
from heyreach import push_lead_to_heyreach
from telegram_helper import send_telegram_alert
from collections import defaultdict

def is_time_in_window(timezone_str: str):
    try:
        tz = pytz.timezone(timezone_str)
        local_time = datetime.datetime.now(tz)
        return local_time.hour == 10, local_time.hour
    except Exception as e:
        print(f"Timezone error for {timezone_str}: {e}")
        return False, -1

def process_pending_leads():
    print("Starting background check for pending leads...")
    try:
        leads = get_pending_leads()
        if not leads:
            print("No pending leads found in the database.")
    except Exception as e:
        print(f"Error fetching leads: {e}")
        return

    batch_results = defaultdict(lambda: {"success": defaultdict(int), "failed": []})
    
    for lead in leads:
        lead_id = lead['id']
        tz = lead.get('timezone', 'UTC')
        
        # If batch_name is None (like for old leads), fallback
        batch_name = lead.get('batch_name')
        if not batch_name:
            batch_name = f"Dheeraj_{lead.get('campaign_id', 'Unknown')}_LegacyBatch"
            
        in_window, current_hour = is_time_in_window(tz)
        
        if in_window:
            print(f"Lead {lead['jirst_name']} {lead['last_name']} is in the 10-11 AM window (TZ: {tzg). Pushing to Heyreach...")
            
            campaign_id = lead.get('campaign_id')
            linkedin_account_id = lead.get('linkedin_account_id')
            
            if not campaign_id or not linkedin_account_id:
                print(f"Warning: Lead {lead_id} has missing campaign or account ID mapping. Skipping.")
                continue
                
            success = push_lead_to_heyreach(
                campaign_id=int(campaign_id),
                linkedin_account_id=int(linkedin_account_id),
                first_name=lead['first_name'],
                last_name=lead['last_name'],
                linkedin_url=lead['linkedin_url'],
                company_name=lead['company_name']
            )
            
            if success:
                update_lead_status(lead_id, 'success')
                batch_results[batch_name]["success"][tz] += 1
            else:
                update_lead_status(lead_id, 'failed')
                batch_results[batch_name]["failed"].append(f"- {lead['first_name']} {lead['last_name']} ({lead['company_name']}) - {tz}")
        else:
            print(f"Skipping {lead['first_name']} {lead['last_name']}: Timezone is {tz}. It is currently {current_hour}:00 locally, waiting for 10:00 AM.")
            
    for batch_name, results in batch_results.items():
        total_success = sum(results["success"].values())
        total_failed = len(results["failed"])
        
        msg = f"📊 <b>Campaign Report: {batch_name}</b>\n#<i>(Processed during the local 10:00 AM window)</i>\n\n"
        msg += f"🍹 <b>Successful Leads ({total_success} total):</b>\n"
        
        if total_success > 0:
            for tz, count in results["success"].items():
                msg += f"- {tz}: {count}\n"
        else:
            msg += "- None\n"
            
        msg += f"\n❌ <b>Failed Leads ({total_failed} total):</b>\n"
        if total_failed > 0:
            for fail_msg in results["failed"]:
                msg += f"{fail_msg}\n"
        else:
            msg += "- 0 failed\n"
            
        send_telegram_alert(msg)

    print("Finished checking leads.")

if __name__ == '__main__':
    process_pending_leads()
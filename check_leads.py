from database import get_supabase
import datetime
import pytz

supabase = get_supabase()
response = supabase.table('leads').select('*').execute()
leads = response.data

ist = pytz.timezone('Asia/Kolkata')
today_date = datetime.datetime.now(ist).date()

today_leads = []
for lead in leads:
    try:
        created_at_dt = datetime.datetime.fromisoformat(lead['created_at'].replace('Z', '+00:00'))
        if created_at_dt.astimezone(ist).date() == today_date:
            today_leads.append(lead)
    except:
        pass

if not today_leads:
    print('No leads were uploaded today.')
else:
    print(f'Found {len(today_leads)} leads uploaded today.')
    for lead in today_leads:
        tz_str = lead.get('timezone', 'UTC')
        try:
            target_tz = pytz.timezone(tz_str)
            now_target = datetime.datetime.now(target_tz)
            target_10am = now_target.replace(hour=10, minute=0, second=0, microsecond=0)
            if now_target.hour >= 10:
                target_10am += datetime.timedelta(days=1)
            
            target_10am_ist = target_10am.astimezone(ist)
            print(f"- {lead['first_name']} {lead['last_name']} ({tz_str}) -> Scheduled for {target_10am_ist.strftime('%I:%M %p IST on %b %d')}, Status: {lead['status']}")
        except Exception as e:
            print(f"- {lead['first_name']} {lead['last_name']}: Error calculating time ({e})")

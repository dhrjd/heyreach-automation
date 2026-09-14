from database import get_supabase
from telegram_helper import send_telegram_alert
from collections import defaultdict
import datetime

supabase = get_supabase()
response = supabase.table('leads').select('*').in_('status', ['success', 'failed']).execute()
leads = response.data

batch_results = defaultdict(lambda: {'success': defaultdict(int), 'failed': []})
for lead in leads:
    tz = lead.get('timezone', 'UTC')
    batch_name = lead.get('batch_name')
    if not batch_name:
        batch_name = f"Dheeraj_{lead.get('campaign_id', 'Unknown')}_LegacyBatch"
    if lead['status'] == 'success':
        batch_results[batch_name]['success'][tz] += 1
    else:
        batch_results[batch_name]['failed'].append(f"- {lead['first_name']} {lead['last_name']} ({lead['company_name']}) - {tz}")

for batch_name, results in batch_results.items():
    total_success = sum(results['success'].values())
    total_failed = len(results['failed'])
    
    msg = f"üìä <b>Retroactive Campaign Report: {batch_name}</b>\n<i>(Previously processed leads)</i>\n\n"
    msg += f"üçπ <b>Successful Leads ({total_success} total):</b>\n"
    
    if total_success > 0:
        for tz, count in results['success'].items():
            msg += f"- {tz}: {count}\n"
    else:
        msg += "- None\n"
        
    msg += f"\nçå <b>Failed Leads ({total_failed} total):</b>\n"
    if total_failed > 0:
        for fail_msg in results['failed']:
            msg += f"{fail_msg}\n"
    else:
        msg += "- 0 failed\n"
        
    send_telegram_alert(msg)
print('Sent retroactive report')
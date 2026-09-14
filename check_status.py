from database import get_supabase

supabase = get_supabase()
response = supabase.table('leads').select('*').execute()
leads = response.data

success_count = 0
pending_count = 0
failed_count = 0

print(f'Checking ALL {len(leads)} leads in database:')
for lead in leads:
    if lead['status'] == 'success': success_count += 1
    elif lead['status'] == 'pending': pending_count += 1
    else: failed_count += 1

print(f'\nTotal Summary: {success_count} success, {pending_count} pending, {failed_count} failed')

print('\nPending leads details:')
for lead in leads:
    if lead['status'] == 'pending':
        print(f"- {lead['first_name']} {lead['last_name']} ({lead['timezone']})")

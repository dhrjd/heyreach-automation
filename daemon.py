from apscheduler.schedulers.blocking import BlockingScheduler
from scheduler import process_pending_leads
import datetime

print(f"[{datetime.datetime.now()}] Heyreach Engine Started. Waiting for the next hourly check...")

scheduler = BlockingScheduler()

# Run the job at the start of every hour
scheduler.add_job(process_pending_leads, 'cron', minute=0)

try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    pass

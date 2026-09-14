import streamlit as st
import pandas as pd
from database import get_supabase, get_campaign_mappings, check_duplicate_lead, insert_lead
from openai_helper import get_timezone_from_segment
import os
import datetime

st.set_page_config(page_title="Heyreach Automation Engine", layout="wide")

st.title("Heyreach Automation Engine")

tab1, tab2, tab3 = st.tabs(["Upload Leads", "Campaign Mappings", "Logs & Dashboard"])

# --- TAB 2: Mappings ---
with tab2:
    st.header("Sender to Campaign Mappings")
    st.write("These mappings are read from the Supabase campaign_mappings table.")
    
    try:
        mappings = get_campaign_mappings()
        if mappings:
            # Flatten the dictionary for display
            flat_mappings = [{"Sender": v["original_name"], "Campaign ID": v["campaign_id"], "LinkedIn Account ID": v["linkedin_account_id"]} for k, v in mappings.items()]
            st.table(pd.DataFrame(flat_mappings))
        else:
            st.info("No mappings found. Please add them in Supabase.")
    except Exception as e:
        st.error(f"Error loading mappings (check your .env and Supabase connection): {e}")

# --- TAB 1: Upload ---
with tab1:
    st.header("Upload CSV")
    st.markdown("Required columns: <firstName>, <lastName>, <Linkedin URL>, <CompanyName>, <Sender>, <Segment>")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Preview:")
        st.dataframe(df.head())
        
        if st.button("Process & Upload to Database"):
            try:
                mappings = get_campaign_mappings()
                supabase = get_supabase()
                
                success_count = 0
                duplicate_count = 0
                unmapped_count = 0
                
                progress_bar = st.progress(0)
                total = len(df)
                
                today_str = datetime.datetime.now().strftime("%d%b%Y")
                
                # Pre-calculate batch numbers for campaigns present in this CSV
                next_batch_numbers = {}
                
                for index, row in df.iterrows():
                    first_name = str(row.get('<firstName>', row.get('firstName', ''))).strip()
                    last_name = str(row.get('<lastName>', row.get('lastName', 'a'))).strip()
                    linkedin_url = str(row.get('<Linkedin URL>', row.get('Linkedin URL', ''))).strip()
                    company = str(row.get('<CompanyName>', row.get('CompanyName', ''))).strip()
                    original_sender = str(row.get('<Sender>', row.get('Sender', ''))).strip()
                    sender_key = original_sender.lower()
                    segment = str(row.get('<Segment>', row.get('Segment', ''))).strip()
                    
                    if not sender_key in mappings:
                        st.warning(f"Row {index+1}: Sender '{original_sender}' has no mapped campaign! Skipping lead {first_name}.")
                        unmapped_count += 1
                        continue
                    
                    mapping_data = mappings[sender_key]
                    campaign_id = mapping_data["campaign_id"]
                    linkedin_account_id = mapping_data["linkedin_account_id"]
                    
                    if not linkedin_account_id:
                         st.warning(f"Row {index+1}: Sender '{original_sender}' has no LinkedIn Account ID mapped! Skipping.")
                         unmapped_count += 1
                         continue
                         
                    # Determine batch name if not already done for this campaign
                    if campaign_id not in next_batch_numbers:
                        # Fetch existing batches for today
                        resp = supabase.table('leads').select('batch_name').ilike('batch_name', f'Dheeraj_{campaign_id}_{today_str}_%').execute()
                        existing_batches = set(r['batch_name'] for r in resp.data if r['batch_name'])
                        next_batch_numbers[campaign_id] = len(existing_batches) + 1
                    
                    batch_name = f"Dheeraj_{campaign_id}_{today_str}_{next_batch_numbers[campaign_id]}"
                    
                    # Duplicate Check
                    if check_duplicate_lead(linkedin_url, original_sender):
                        st.warning(f"Row {index+1}: Duplicate Lead found for {linkedin_url} with sender '{original_sender}'. Skipping.")
                        duplicate_count += 1
                        continue
                        
                    # Get Timezone
                    tz = get_timezone_from_segment(segment)
                    
                    # Insert Lead
                    lead_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "linkedin_url": linkedin_url,
                        "company_name": company,
                        "sender": original_sender,
                        "segment": segment,
                        "timezone": tz,
                        "status": "pending",
                        "campaign_id": str(campaign_id),
                        "linkedin_account_id": int(linkedin_account_id),
                        "batch_name": batch_name
                    }
                    insert_lead(lead_data)
                    success_count += 1
                    progress_bar.progress((index + 1) / total)
                    
                st.success(f"Upload complete! Added {success_count} leads. {duplicate_count} duplicates skipped. {unmapped_count} skipped due to missing mappings.")
                
            except Exception as e:
                st.error(f"An error occurred: {e}")

# --- TAB 3: Logs ---
with tab3:
    st.header("Database Records")
    if st.button("Refresh Data"):
        try:
            supabase = get_supabase()
            response = supabase.table("leads").select("*").order("created_at", desc=True).limit(100).execute()
            if response.data:
                df_logs = pd.DataFrame(response.data)
                st.dataframe(df_logs)
            else:
                st.info("No leads found.")
        except Exception as e:
            st.error(f"Failed to fetch records: {e}")

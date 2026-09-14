# HeyReach Automation Engine

HeyReach Automation Engine is a Streamlit-based application designed to streamline the process of uploading, mapping, and managing leads for your HeyReach campaigns. It integrates with Supabase for data storage and utilizes OpenAI for intelligent data parsing (like determining timezones based on segments).

## Features

- **Upload Leads**: Seamlessly upload CSV files containing your lead information.
- **Campaign Mapping**: Automatically map senders to their respective Campaign IDs and LinkedIn Account IDs using data from Supabase.
- **Duplicate Checking**: Prevents uploading duplicate leads based on their LinkedIn URL and sender.
- **Timezone Detection**: Uses OpenAI to automatically infer the timezone from the segment data.
- **Logs & Dashboard**: View recently processed leads and system logs directly from the Streamlit interface.

## Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dhrjd/heyreach-automation.git
   cd heyreach-automation
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**:
   Create a `.env` file in the root directory and add the necessary API keys and credentials:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   OPENAI_API_KEY=your_openai_api_key
   # Add any other required keys
   ```

4. **Database Setup**:
   Ensure your Supabase project is set up with the required tables (`leads` and `campaign_mappings`). You can refer to `schema.sql` for the database schema.

## Usage

Run the Streamlit application:

```bash
streamlit run app.py
```

Navigate to the local URL provided by Streamlit (usually `http://localhost:8501`) to access the dashboard.

## Background Services
The engine also includes daemon and scheduler scripts (`daemon.py`, `scheduler.py`) to process pending leads in the background automatically.

## Requirements

The required Python packages are listed in `requirements.txt`.

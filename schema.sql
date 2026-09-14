-- Supabase SQL Schema for Heyreach Automation

-- Create Leads table
CREATE TABLE leads (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    linkedin_url TEXT NOT NULL,
    company_name TEXT NOT NULL,
    sender TEXT NOT NULL,
    segment TEXT,
    timezone TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'failed')),
    campaign_id TEXT,
    linkedin_account_id BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Create Campaign Mappings table
CREATE TABLE campaign_mappings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sender_name TEXT UNIQUE NOT NULL,
    campaign_id TEXT NOT NULL,
    linkedin_account_id BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster querying by linkedin_url and status
CREATE INDEX idx_leads_linkedin_url ON leads(linkedin_url);
CREATE INDEX idx_leads_status ON leads(status);

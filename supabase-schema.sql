-- ════════════════════════════════════════════════════════
-- anymetric.ai — Supabase schema for form submissions
-- Paste this into Supabase → SQL Editor → Run
-- ════════════════════════════════════════════════════════

-- Table: captures every form submission from the site
create table if not exists public.leads (
  id              uuid primary key default gen_random_uuid(),
  created_at      timestamptz not null default now(),
  form_source     text,                    -- which form: audit-intake, playbook-download, etc.
  page            text,                    -- which URL submitted from
  submitted_at    timestamptz,             -- client-side timestamp
  name            text,
  email           text not null,
  company         text,
  role            text,
  focus           text,                    -- selected service area
  challenge       text,                    -- the textarea content
  raw             jsonb                    -- full payload, for any fields we add later
);

-- Index for fast lookups by email and recent submissions
create index if not exists leads_email_idx on public.leads (email);
create index if not exists leads_created_at_idx on public.leads (created_at desc);

-- ════════════════════════════════════════════════════════
-- Row Level Security — public inserts, no public reads
-- ════════════════════════════════════════════════════════
alter table public.leads enable row level security;

-- Anyone with the anon key can INSERT (needed for form submission)
create policy "allow anon insert" on public.leads
  for insert to anon
  with check (true);

-- Nobody can SELECT via anon key (only you via dashboard or service role)
-- No read policy = read blocked by default. Good.

-- ════════════════════════════════════════════════════════
-- How to wire your forms to this table
-- ════════════════════════════════════════════════════════
-- 1. In Supabase → Project Settings → API: copy the Project URL + anon key
-- 2. In each HTML file, find the UNIVERSAL FORM HANDLER script at the bottom
-- 3. Set:
--    const FORM_ENDPOINT = "https://YOUR-PROJECT.supabase.co/rest/v1/leads";
-- 4. Uncomment the headers block and paste your anon key:
--    "apikey": "YOUR_ANON_KEY",
--    "Authorization": "Bearer YOUR_ANON_KEY",
--    "Prefer": "return=minimal"
-- 5. Push to GitHub. Submit a test form. Check the leads table in Supabase.

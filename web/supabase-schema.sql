-- Run this in the Supabase SQL editor to create the waitlist table

create table if not exists waitlist (
  id bigint generated always as identity primary key,
  email text not null unique,
  created_at timestamptz not null default now()
);

-- Enable RLS but only allow server-side access (service role key)
alter table waitlist enable row level security;

-- Index for upsert performance
create index if not exists waitlist_email_idx on waitlist (email);

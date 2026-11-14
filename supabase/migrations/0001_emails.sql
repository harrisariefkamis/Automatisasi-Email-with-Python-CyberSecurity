create table if not exists public.emails (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  provider text not null check (provider in ('gmail')),
  provider_message_id text not null check (char_length(provider_message_id) <= 256),
  thread_id text not null default '' check (char_length(thread_id) <= 256),
  sender text not null default '' check (char_length(sender) <= 320),
  subject text not null default '' check (char_length(subject) <= 998),
  body_text text null,
  received_at text null,
  headers jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (user_id, provider, provider_message_id)
);

alter table public.emails enable row level security;
alter table public.emails force row level security;

create policy "users can read own emails" on public.emails
  for select to authenticated using ((select auth.uid()) = user_id);
create policy "users can insert own emails" on public.emails
  for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "users can update own emails" on public.emails
  for update to authenticated using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);
create policy "users can delete own emails" on public.emails
  for delete to authenticated using ((select auth.uid()) = user_id);

create index if not exists emails_user_created_idx on public.emails (user_id, created_at desc);

-- Do not create a service-role client in the application. The repository must send
-- the authenticated user's JWT so these RLS policies are enforced.

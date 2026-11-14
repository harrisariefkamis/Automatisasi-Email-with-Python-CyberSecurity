# Deployment Plan

## Architecture decisions

For the public website demo, use Streamlit Community Cloud for the UI, Supabase Auth for website login, and a separate Gmail OAuth flow with read-only scope. Keep all destructive email actions disabled until the security review is complete.

## Phase A: deploy Streamlit demo

1. Push the repo to GitHub.
2. In Streamlit Community Cloud, connect the repository and choose `streamlit_app.py` as the app entry file.
3. Set `SUPABASE_URL` and `SUPABASE_ANON_KEY` in Streamlit secrets.
4. Leave Gmail and AI services disabled until the OAuth and consent flows are implemented.

Example secrets:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your-public-anon-key"
```

## Phase B: Gmail OAuth (separate from website login)

1. Register an OAuth client in Google Cloud Console.
2. Use a server-side authorization code flow with CSRF state validation.
3. Request the minimum Gmail scope: `gmail.readonly`.
4. Store user tokens in encrypted server-side storage mapped to the authenticated user ID.
5. Never store Gmail tokens in Git, frontend state, or public logs.
6. Keep all actions read-only in the MVP.

## Phase C: Supabase RLS and data storage

1. Run the migration in `supabase/migrations/0001_emails.sql`.
2. Use the authenticated user JWT so `auth.uid() = user_id` is enforced by RLS.
3. Do not use the service-role key in the app.
4. Keep email content minimal and consent-gated.

## Phase D: AI processing

1. Add any AI provider key in platform-managed secrets only.
2. Require explicit user consent before sending email content to an external model.
3. Redact personal data, validate schema outputs, and fail safely to the deterministic rule-based triage.
4. Treat email content as untrusted input and never let the model write to Gmail or the database.

## Phase E: actions

For the MVP, do not support send, delete, move, label, or unsubscribe actions. If those features are added later, require explicit action confirmation, audit logs, and undo support.

## Vercel note

Vercel can be used for API endpoints if a separate backend is introduced later, but it is not the right host for the main Streamlit UI.

## Security checklist before real inbox access

- [ ] Website login works through Supabase Auth.
- [ ] RLS blocks cross-user access.
- [ ] Gmail OAuth hasState CSRF validation and secure token storage.
- [ ] Consent for Gmail and AI is explicit and separate.
- [ ] No secrets are committed to Git or exposed in logs.
- [ ] Error handling covers malformed payloads and provider failures.

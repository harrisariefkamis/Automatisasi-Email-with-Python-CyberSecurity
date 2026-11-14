# Integrasi Gmail, Supabase, dan AI — batas keamanan

## Kondisi implementasi

Sudah tersedia komponen server-side untuk Gmail read-only, normalisasi model email, pemanggilan `core.triage_email()`, penyimpanan Supabase opsional berbasis user JWT/RLS, adapter OpenAI dengan consent dan schema validation, audit metadata, serta primitive approval. Namun integrasi **belum production-ready**: tidak ada OAuth web flow, session/authentication aplikasi, Supabase Auth wiring, consent UI, rate limiting aplikasi, durable audit store, atau Gmail write executor. Endpoint Vercel hanya triase teks stateless.

## Alur yang disarankan

1. **Auth/consent aplikasi**: autentikasi pengguna dan sesi server. Consent untuk membaca Gmail, menyimpan email, dan mengirim teks ke AI harus terpisah, eksplisit, dapat dicabut, dan dicatat.
2. **OAuth Google**: Authorization Code flow server-side; validasi `state`, redirect URI, issuer/audience; Gmail scope hanya `gmail.readonly`. Simpan refresh/access token terenkripsi server-side, sediakan revoke. Jangan menerima credential dari request body atau browser storage.
3. **Fetch/read**: `GmailReadOnlyClient` membatasi 20 pesan terbaru, hanya menyediakan list/get, dan normalisasi body/header dengan batas panjang. Jangan membuka URL atau lampiran otomatis.
4. **Triage**: panggil `triage_message(EmailMessage)` yang mendelegasikan ke `core.triage_email()`.
5. **Supabase**: jalankan migration. Gunakan Supabase Auth JWT pengguna + anon key dari server. RLS memvalidasi `auth.uid() = user_id`. Jangan pernah gunakan service-role key di request path. `PERSIST_EMAIL_BODY=false` adalah default desain; repository menghilangkan body kecuali opsi `store_body=True` dan consent persistence diberikan. Terapkan retensi/penghapusan dan enkripsi sesuai kebutuhan.
6. **AI**: OpenAI bersifat optional dan hanya dipanggil pada kategori job bila `external_processing_consent=True`. Redaksi email/telepon, batas ukuran, timeout, strict JSON schema/Pydantic validation, tanpa tools. Prompt injection diuji; rules tetap sumber fallback. Pastikan kebijakan provider dan disclosure data sesuai kebutuhan sebelum mengirim data.
7. **Approval/audit**: audit event tidak berisi body, sender, prompt, token, atau secret. `ApprovalService` hanya mencatat proposal/approval dan tidak menjalankan tindakan. Approval saat ini belum one-time persisted; jangan jadikan sebagai authorization produksi.
8. **Actions**: tidak ada API Gmail mutation. Jangan menambah send/delete/move/unsubscribe sebelum authenticated one-time approval, authorization check, idempotency, dry-run, audit durable, undo/rollback, dan review keamanan tersedia.

Contoh komposisi service (credentials dan identitas harus berasal dari auth layer tepercaya):

```python
from email_assistant.integrations.gmail_client import GmailReadOnlyClient
from email_assistant.services.email_triage_service import triage_message

client = GmailReadOnlyClient(server_side_google_credentials)
for normalized_email in client.list_recent(max_results=10):
    result = triage_message(normalized_email)
    # Persist only after separate, explicit user consent.
```

## Supabase setup

1. Buat project Supabase.
2. Jalankan `supabase/migrations/0001_emails.sql` di Supabase SQL editor/migration workflow.
3. Atur `SUPABASE_URL` dan anon key di server secret store. Gunakan access JWT pengguna pada repository; jangan memakai service role.
4. Uji RLS dengan dua user: user A tidak boleh membaca/menulis record user B, termasuk lewat filter yang dimanipulasi.
5. Tentukan retensi sebelum mengaktifkan body persistence. Body tidak disimpan secara default oleh repository.

## Vercel deployment

`vercel.json` mendefinisikan Python serverless API `api/triage.py`. Deploy dengan mengimpor GitHub repository ke Vercel atau menjalankan Vercel CLI di akun Anda; sesi Copilot ini tidak memiliki akses ke akun Vercel, jadi saya tidak dapat membuat deployment live atau mengatur secrets di dashboard.

Set `API_ACCESS_TOKEN` di Vercel Environment Variables untuk Preview/Production, lalu deploy. Endpoint saat ini hanya menerima teks triase dengan bearer token dan batas request; ia **tidak** menggunakan Gmail/OpenAI/Supabase. Sebelum endpoint publik, aktifkan rate limit/WAF dan autentikasi per pengguna. Jangan masukkan bearer token di browser publik.

## Sebelum mengaktifkan fitur nyata

- [ ] OAuth flow, CSRF/state, server sessions, logout/revoke, encrypted token storage diuji.
- [ ] Consent terpisah dan dapat dicabut untuk Gmail read, penyimpanan, dan AI.
- [ ] Scope OAuth dan data minimization direview; lampiran/URL tidak di-fetch otomatis.
- [ ] Supabase RLS diuji dengan akun berbeda dan service-role key tidak digunakan.
- [ ] Prompt-injection, MIME/HTML malformed, input oversize, invalid schema, rate limits, timeouts, dan outage diuji.
- [ ] Secret scanning, dependency checks, CI, rate limiting, deployment logs redaction, privacy/retention policy aktif.
- [ ] Tindakan tulis tetap tidak tersedia sampai threat model dan approval flow durable ditinjau.

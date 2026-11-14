# Panduan Integrasi Gmail, Supabase, dan AI — batas keamanan

## Status implementasi

Repo memiliki UI demo Streamlit di `streamlit_app.py`, Gmail read-only adapter, model internal `EmailMessage`, service yang memanggil `core.triage_email()`, Supabase repository dengan user JWT/RLS, adapter OpenAI dengan consent/schema validation, serta endpoint Vercel untuk triase teks. Namun login website, OAuth callback/session Gmail, token storage per-user, consent UI, dan koneksi komponen tersebut ke UI belum tersedia end-to-end.

## Arsitektur prototipe yang direkomendasikan

- Streamlit Community Cloud: hosting UI Streamlit.
- Supabase Auth: login website email/kata sandi dan manajemen akun.
- Google OAuth Gmail: izin terpisah, dimulai read-only.
- Supabase Postgres: data aplikasi dengan RLS per pengguna.
- OpenAI: opsional, hanya untuk data yang dipilih pengguna setelah consent.
- Vercel: hanya bila backend API dipisahkan kemudian; bukan untuk host Streamlit persisten.

Login ke website tidak memberi izin Gmail; persetujuan Gmail tidak berarti persetujuan AI.

Detail deployment dan tahapan implementasi ada di [DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md).

## Batas keamanan

1. Gunakan Gmail scope `gmail.readonly` untuk MVP.
2. OAuth harus server-side dengan state/CSRF validation, exact redirect URI, sesi terautentikasi, token terenkripsi, revoke/disconnect. Jangan menerima Google token dari request body atau menyimpannya di Git/URL.
3. Supabase memakai user JWT agar RLS berlaku. Jangan gunakan service-role key pada jalur request pengguna.
4. Body email tidak disimpan default; persistence membutuhkan consent terpisah dan kebijakan retensi.
5. OpenAI hanya dipanggil setelah consent AI eksplisit; minimalkan/redaksi PII dan validasi schema.
6. Email adalah input tidak tepercaya. AI tidak mendapat tool akses Gmail/database dan tidak boleh memicu tindakan.
7. Audit log tidak boleh merekam body email, token, prompt, atau kredensial.
8. Tidak ada Gmail write action. Proposal approval bukan izin produksi dan tidak menjalankan tindakan.

## Status deployment

Untuk deploy UI, pilih `streamlit_app.py` sebagai main file di Streamlit Community Cloud. Vercel endpoint `api/triage.py` hanya melakukan triase teks manual dan tidak menghubungkan Gmail, Supabase, atau OpenAI.

# Email Job Assistant

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)

Prototipe triase email yang menghubungkan Gmail **read-only**, aturan triase Python, penyimpanan Supabase opsional dengan RLS, dan analisis OpenAI opsional yang memerlukan consent eksplisit.

> **Peringatan status:** Adapter Gmail dan AI tersedia sebagai komponen server-side, tetapi OAuth login/callback dan session management belum disediakan. Endpoint Vercel hanya menerima teks untuk triase aturan; ia tidak menyinkronkan Gmail, menulis ke Supabase, atau memanggil OpenAI. Jangan aktifkan akses inbox/AI untuk pengguna sebelum OAuth, autentikasi, RLS, consent UI, rate limiting, dan review keamanan selesai.

## Jalankan demo lokal

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -e .
streamlit run app.py
```

## Integrasi server-side

1. Salin `.env.example` sebagai template lokal; aplikasi saat ini tidak memuat `.env` otomatis. Jangan commit secret.
2. Implementasikan OAuth Authorization Code flow di server dengan Gmail scope read-only dan state/CSRF validation. Berikan OAuth credentials ke `GmailReadOnlyClient` dari session server yang terautentikasi; jangan menerima token dari body request.
3. Normalisasi pesan ke `EmailMessage`, lalu panggil `triage_message()` untuk memakai fungsi `core.triage_email()` yang ada.
4. Simpan email hanya bila pengguna menyetujui persistence. Jalankan SQL migration di `supabase/migrations/0001_emails.sql`; repository menggunakan anon key dan JWT pengguna agar RLS berlaku. Jangan gunakan service-role key.
5. Panggil `OpenAIJobAssistant` hanya setelah consent terpisah untuk pemrosesan eksternal; hasil divalidasi dengan Pydantic. Isi email adalah input tidak tepercaya, bukan instruksi.
6. Proposal approval dan audit hanya mencatat metadata. Belum ada Gmail write executor—tidak ada tindakan yang akan dijalankan.

Detail, contoh pemakaian dan checklist keamanan: [Panduan Integrasi](docs/INTEGRATION_GUIDE.md).

## Deploy ke Vercel

Repo berisi Python serverless function `api/triage.py` dan `vercel.json`. Endpoint `/api/triage` hanya melakukan triase teks stateless dengan bearer token `API_ACCESS_TOKEN`; bukan OAuth callback dan tidak mengakses Gmail, Supabase, atau OpenAI.

Untuk deploy: import repository di Vercel, tambahkan `API_ACCESS_TOKEN` sebagai Environment Variable (gunakan nilai acak kuat), lalu deploy. Vercel CLI/dashboard harus dijalankan dengan akun pemilik; tidak ada kredensial deployment yang tersedia dari sesi ini. Lindungi endpoint dengan rate limiting/WAF sebelum dibuka publik. Hindari mengirim data pribadi ke endpoint yang belum memiliki user authentication.

## Uji

```bash
python -m unittest discover -s tests
```

## Lisensi dan kontributor

MIT; lihat `LICENSE`. Pemilik/kontributor: [@harrisariefkamis](https://github.com/harrisariefkamis).

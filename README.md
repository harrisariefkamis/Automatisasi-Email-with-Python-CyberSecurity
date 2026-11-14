# Email Job Assistant

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)

Prototipe triase email dengan rules Python, adapter Gmail read-only, penyimpanan Supabase opsional, dan analisis OpenAI opsional yang membutuhkan consent.

> **Penting:** `app.py` adalah entrypoint Python untuk Vercel. UI Streamlit dipindah ke `streamlit_app.py`. Endpoint Vercel hanya menangani triase teks; OAuth pengguna, koneksi inbox, Supabase, dan AI belum terhubung ke endpoint. Jangan menaruh token rahasia di browser.

## Jalankan UI Streamlit lokal

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -e .
streamlit run streamlit_app.py
```

## Deploy ke Vercel

Import repositori ke Vercel. Tambahkan `API_ACCESS_TOKEN` sebagai Environment Variable dengan nilai acak kuat untuk Preview dan Production, lalu deploy. Vercel mengekspos endpoint `POST /api/triage` (dan root `app.py` juga mengekspor handler untuk kompatibilitas entrypoint). Endpoint memerlukan `Authorization: Bearer <API_ACCESS_TOKEN>` dan JSON `{ "from": "...", "subject": "...", "body": "..." }`.

```bash
curl -X POST "$VERCEL_URL/api/triage" \
  -H "Authorization: Bearer $API_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"from":"recruiter@example.com","subject":"Python job opening","body":"We are hiring"}'
```

Endpoint membatasi ukuran payload, tidak mencatat request, memakai response `no-store`, dan tidak mengakses Gmail, Supabase, maupun OpenAI. Tambahkan rate limiting/WAF sebelum endpoint digunakan secara publik. Streamlit bukan Vercel function; jalankan terpisah pada host yang mendukung Streamlit.

## Integrasi Gmail, Supabase, dan AI

Komponen server-side ada di `src/email_assistant`. Implementasikan OAuth callback/session dan consent UI sebelum digunakan dengan akun/email nyata. Gunakan Gmail scope read-only, Supabase user JWT dengan RLS (jangan service-role key), dan kirim konten ke OpenAI hanya setelah consent eksplisit. Lihat [panduan integrasi](docs/INTEGRATION_GUIDE.md).

## Pengujian

```bash
python -m unittest discover -s tests
```

## Lisensi dan kontributor

MIT; lihat `LICENSE`. Pemilik proyek: [@harrisariefkamis](https://github.com/harrisariefkamis).

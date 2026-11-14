# Email Job Assistant

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)

Prototipe triase email dengan Python dan Streamlit. Rekomendasi deployment: **Streamlit Community Cloud + Supabase Auth/Postgres + OAuth Gmail terpisah + AI opsional dengan consent eksplisit**.

> **Status:** UI login Supabase dan workspace demo tersedia di `streamlit_app.py`. Gmail OAuth dan AI belum terhubung end-to-end; panelnya tetap nonaktif. Login website bukan izin untuk membaca Gmail.

## Jalankan lokal

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy ke Streamlit Community Cloud

1. Hubungkan repository GitHub ke Streamlit Community Cloud.
2. Pilih branch `main` dan entrypoint `streamlit_app.py`.
3. Atur `SUPABASE_URL` dan `SUPABASE_ANON_KEY` di Streamlit app Secrets untuk mengaktifkan login. Jangan gunakan service-role key.
4. Deploy. Tanpa secrets, UI tetap dapat dibuka tetapi auth tidak tersedia.

Panduan setup dan checklist keamanan: [DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md).

## Arsitektur dan privasi

- Login website menggunakan Supabase Auth email/kata sandi; tidak ada password yang disimpan di kode aplikasi.
- Gmail harus disambungkan melalui OAuth Google terpisah dan read-only.
- AI tidak boleh memproses isi email tanpa persetujuan khusus.
- Vercel hanya untuk endpoint API terpisah; endpoint saat ini tidak mengakses Gmail, Supabase, atau OpenAI.
- Tidak ada pengiriman, penghapusan, pemindahan, atau unsubscribe email otomatis.

## Pengujian

```bash
python -m unittest discover -s tests
```

MIT License; lihat `LICENSE`. Pemilik proyek: [@harrisariefkamis](https://github.com/harrisariefkamis).

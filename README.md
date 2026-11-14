# Email Job Assistant

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)

Prototipe triase email dengan Python dan Streamlit. Rekomendasi deployment untuk prototipe yang bisa diakses adalah **Streamlit Community Cloud + Supabase Auth/Postgres + OAuth Gmail terpisah + AI opsional dengan persetujuan eksplisit**.

> **Status saat ini:** UI Streamlit berada di `streamlit_app.py`, dan bisa dijalankan lokal. Adapter Gmail read-only, Supabase repository/RLS schema, dan adapter OpenAI tersedia sebagai komponen, tetapi website belum menyediakan alur login email/kata sandi, OAuth Gmail end-to-end, koneksi UI ke inbox, atau proses produksi. Login website bukan izin untuk membaca Gmail. Jangan gunakan dengan inbox nyata sebelum mengikuti [rencana deployment dan keamanan](docs/DEPLOYMENT_PLAN.md).

## Arsitektur yang disarankan

1. **Website/UI:** Streamlit Community Cloud, entrypoint `streamlit_app.py`.
2. **Login website:** Supabase Auth untuk email/kata sandi, verifikasi email, reset password, dan sesi pengguna.
3. **Koneksi Gmail:** alur OAuth Google yang terpisah, dimulai read-only dan hanya setelah pengguna menekan “Hubungkan Gmail” serta menyetujui scope.
4. **Database:** Supabase Postgres dengan Row Level Security (RLS), data hanya dapat diakses oleh pemiliknya.
5. **AI:** opsional; jelaskan data yang dikirim ke provider dan minta persetujuan sebelum memproses isi email.
6. **Vercel:** gunakan nanti bila backend/API dipisahkan dari Streamlit. Endpoint Vercel yang ada hanya untuk triase teks dan tidak menghubungkan Gmail, Supabase, atau OpenAI.

## Jalankan UI lokal

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\Activate.ps1
pip install -e .
streamlit run streamlit_app.py
```

## Deploy prototipe UI

1. Push repo ke GitHub.
2. Masuk ke Streamlit Community Cloud dan hubungkan GitHub.
3. Buat app dari repo ini, pilih branch `main`, dan set **Main file path** ke `streamlit_app.py`.
4. Masukkan secrets melalui pengaturan Streamlit Cloud, bukan ke Git. Deploy dan uji URL yang disediakan.
5. Ini hanya menerbitkan UI demo saat ini; fitur login, Gmail, dan AI belum terhubung end-to-end.

Lihat [langkah deployment lengkap](docs/DEPLOYMENT_PLAN.md) untuk penyiapan Supabase, Google OAuth, dan tahapan aktivasi yang aman.

## Integrasi Gmail, Supabase, dan AI

Komponen server-side berada di `src/email_assistant`. Implementasikan autentikasi dan session handling terlebih dahulu. Gunakan Supabase JWT pengguna dengan RLS (jangan service-role key pada request pengguna), Gmail OAuth read-only, dan AI hanya setelah consent terpisah. Detail ada di [Panduan Integrasi](docs/INTEGRATION_GUIDE.md).

## Pengujian

```bash
python -m unittest discover -s tests
```

## Batasan dan keamanan

- Klasifikasi adalah petunjuk berbasis aturan, bukan verifikasi keaslian email/lowongan.
- Tidak ada Gmail write action; tidak ada pengiriman, penghapusan, pemindahan, atau unsubscribe otomatis.
- Jangan simpan secret, access token, refresh token, kata sandi, atau isi email ke Git/log.
- Sebelum akses Gmail nyata: lengkapi OAuth callback/session, persetujuan terpisah, penyimpanan token yang aman, RLS test, rate limiting, dan review keamanan.

## Lisensi dan kontributor

MIT; lihat `LICENSE`. Pemilik proyek: [@harrisariefkamis](https://github.com/harrisariefkamis).

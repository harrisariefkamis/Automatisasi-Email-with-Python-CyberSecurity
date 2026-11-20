# Rencana Deployment: Streamlit + Supabase + Gmail OAuth

## Keputusan arsitektur

Untuk prototipe website, gunakan **Streamlit Community Cloud untuk UI**, **Supabase Auth dan Postgres/RLS untuk akun/data**, **Google OAuth Gmail sebagai izin terpisah**, dan **AI opsional setelah consent eksplisit**. Gunakan Vercel hanya bila API backend dipisahkan kemudian; Vercel Functions bukan host Streamlit persisten.

### Pemisahan izin

- Login email/kata sandi membuat akun website melalui Supabase Auth.
- Tombol “Hubungkan Gmail” nantinya memulai Google OAuth terpisah dengan scope Gmail baca-saja.
- Consent AI terpisah; beri tahu pengguna bahwa email pilihan akan dikirim ke provider AI sebelum meminta persetujuan.
- Jangan menganggap salah satu izin sebagai izin untuk yang lain.

## Tahap A: deploy UI demo

1. Push repo ke GitHub.
2. Masuk ke Streamlit Community Cloud dan hubungkan GitHub.
3. Buat app dari repo ini, branch `main`, file utama `streamlit_app.py`.
4. Untuk login, tambahkan Supabase URL dan public anon key ke bagian Secrets aplikasi. Jangan gunakan service-role key.

Contoh secrets TOML (isi hanya di pengaturan Streamlit, jangan commit):

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your-public-anon-key"
```

UI mendukung signup, login, reset password, tabs workspace, dan triase teks lokal. Jika secrets Supabase belum ada, tombol auth nonaktif. Panel Gmail dan AI masih nonaktif karena alur OAuth/token per pengguna belum dibuat.

## Tahap B: Gmail OAuth terpisah

Sebelum mengaktifkan tombol “Hubungkan Gmail”:
1. Buat OAuth client di Google Cloud Console dan daftarkan redirect URI yang persis.
2. Implementasikan authorization-code flow server-side dengan state anti-CSRF, redirect allowlist, validasi callback, user binding, revoke/disconnect, dan penanganan token kedaluwarsa.
3. Minta hanya `https://www.googleapis.com/auth/gmail.readonly` untuk MVP.
4. Simpan refresh token terenkripsi server-side per user; jangan simpan di `.env`, URL, browser, atau Git. Secrets platform untuk credential aplikasi bukan tempat menyimpan token pribadi semua pengguna.
5. Panggil `GmailReadOnlyClient` dengan kredensial dari sesi tepercaya. Batasi pesan/body dan jangan fetch attachment atau buka URL otomatis.
6. Normalisasikan email ke `EmailMessage` dan sambungkan ke `triage_message()`.

## Tahap C: Supabase Postgres/RLS

1. Jalankan `supabase/migrations/0001_emails.sql`.
2. Gunakan JWT pengguna agar RLS menegakkan `auth.uid() = user_id`. Jangan gunakan service-role key pada request pengguna.
3. Simpan metadata minimal; simpan body hanya bila diperlukan dan dengan persetujuan terpisah.
4. Uji isolasi RLS dengan dua user, termasuk percobaan memalsukan `user_id`.
5. Tetapkan retention, penghapusan, backup dan incident response sebelum data nyata disimpan.

## Tahap D: AI opsional

1. Simpan `OPENAI_API_KEY` hanya di secrets platform server-side.
2. Jelaskan provider, data yang dikirim, tujuan dan retensi; dapatkan consent AI khusus sebelum memanggil adapter.
3. Minimalkan/redaksi PII, batasi input, validasi schema, timeout/kuota, dan fallback ke triase rule-based.
4. Perlakukan body sebagai data tidak tepercaya. Model tidak boleh punya tools Gmail/database atau menjalankan tindakan.

## Tahap E: tindakan email

Untuk MVP, pertahankan read-only. Jangan aktifkan send/delete/move/label/unsubscribe. Tindakan masa depan memerlukan preview, konfirmasi per tindakan, otorisasi server, approval satu kali yang dipersistenkan, audit terlindungi, idempotency, batas batch, dan undo.

## Vercel

`api/triage.py` adalah endpoint triase teks stateless, bukan website Streamlit. Vercel dapat dipakai bila backend dipisah menjadi API. Streamlit UI tetap berada di Streamlit Community Cloud atau hosting yang mendukung proses Streamlit persisten.

## Checklist sebelum inbox nyata

- [ ] Supabase Auth signup/login/reset password berjalan dan diuji.
- [ ] RLS mencegah akses silang antar pengguna.
- [ ] Gmail OAuth state/CSRF, redirect, token storage, revoke, dan scope read-only ditinjau.
- [ ] Consent Gmail, persistence, dan AI terpisah dan dapat dicabut.
- [ ] Secrets tidak muncul di source, client, URL, log, atau state yang tidak aman.
- [ ] Uji prompt injection, payload malformed/oversize, provider failure, dan akses lintas akun.
- [ ] Rate limit, logging redacted, privacy/retention policy, dan proses penghapusan tersedia.
- [ ] Gmail write action tidak tersedia sebelum review keamanan dan approval flow lengkap.

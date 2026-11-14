# Rencana Deployment: Streamlit + Supabase + Gmail OAuth

## Keputusan arsitektur

Untuk prototipe website yang dapat diakses, gunakan **Streamlit Community Cloud untuk UI**, **Supabase Auth dan Postgres/RLS untuk akun/data**, **Google OAuth Gmail sebagai izin terpisah**, dan **AI opsional setelah consent eksplisit**. Gunakan Vercel hanya bila API backend dipisahkan kemudian; Vercel Python Functions bukan host Streamlit persisten.

### Pemisahan izin

- Login email/kata sandi membuat akun website melalui Supabase Auth.
- Tombol “Hubungkan Gmail” memulai Google OAuth terpisah dengan Gmail scope minimum read-only.
- Consent AI terpisah dari consent Gmail: pengguna diberi tahu bahwa teks email yang dipilih akan dikirim ke provider AI sebelum menyetujui.
- Jangan menganggap salah satu izin sebagai izin untuk yang lain.

## Tahap A — deploy demo Streamlit yang ada

1. Pastikan perubahan ada di branch GitHub yang akan dipakai.
2. Buka Streamlit Community Cloud dan hubungkan akun GitHub.
3. Buat aplikasi dari repository ini, branch `main`, file utama `streamlit_app.py`.
4. Deploy tanpa secrets Gmail/OpenAI terlebih dahulu. Uji UI triase lokal/demo dari URL.
5. Konfigurasi `requirements.txt` dipakai untuk instalasi dependency.

Tahap ini **tidak** mengaktifkan login, Gmail, atau AI. Jangan berikan akses inbox sebelum tahap-tahap berikut diselesaikan.

## Tahap B — Supabase Auth email/kata sandi

1. Buat project Supabase dan atur email confirmation, password reset, redirect allowlist, serta kebijakan password sesuai kebutuhan.
2. Tambahkan UI signup/login/logout/reset password ke Streamlit menggunakan Supabase Auth; jangan membuat tabel password sendiri atau menyimpan password di aplikasi.
3. Simpan Supabase URL dan public anon key dalam secrets server-side. Service-role key tidak boleh masuk ke browser, Streamlit session state, repo, atau jalur request pengguna.
4. Verifikasi setiap request/data operation dengan Supabase user JWT. Terapkan dan uji RLS untuk memastikan pengguna A tidak dapat membaca atau mengubah data pengguna B.
5. Atur sesi dan logout dengan jelas. Hindari menyimpan access token di URL atau menampilkan token pada UI/log.

## Tahap C — koneksi Gmail terpisah

1. Buat OAuth client di Google Cloud Console dan daftarkan redirect URI yang persis sesuai host/flow yang diimplementasikan.
2. Implementasikan server-side OAuth Authorization Code flow dengan state anti-CSRF, redirect allowlist, validasi callback, identitas pengguna, revoke/disconnect, dan penanganan token kedaluwarsa.
3. Minta hanya `https://www.googleapis.com/auth/gmail.readonly` untuk MVP. Jelaskan ke pengguna data apa yang akan dibaca dan kapan.
4. Tampilkan tombol “Hubungkan Gmail” setelah login website; jangan menyatukan login website dan consent Gmail.
5. Simpan refresh token hanya dalam penyimpanan server-side yang terenkripsi dan dipetakan ke user ID; tidak ke `.env`, URL, cookie JavaScript, atau Git. Streamlit Community Cloud secrets hanya menyimpan konfigurasi aplikasi, bukan token individual semua pengguna.
6. Panggil `GmailReadOnlyClient` di server dengan kredensial milik user yang sudah terautentikasi. Normalisasikan hasil ke `EmailMessage`, batasi jumlah/ukuran, jangan fetch lampiran atau membuka URL otomatis.
7. Hubungkan ke `triage_message()`/`core.triage_email()`. Tampilkan sumber dan hasil sebagai saran untuk ditinjau.

**Penting untuk produksi:** token per pengguna perlu penyimpanan aman, kontrol akses, enkripsi, rotasi, dan proses revoke. Jika Streamlit Community Cloud dan pola sesi tidak memadai untuk kebutuhan ini, pindahkan OAuth/token service ke backend terpisah (misalnya FastAPI di host server persisten) dan lindungi dengan autentikasi server-to-server.

## Tahap D — Supabase Postgres/RLS

1. Jalankan migration `supabase/migrations/0001_emails.sql` di Supabase.
2. Pastikan aplikasi memakai user JWT supaya RLS menerapkan `auth.uid() = user_id`. Jangan mengganti user JWT dengan service-role key.
3. Simpan metadata minimal. Body email tidak perlu dipersistenkan kecuali produk memerlukannya dan pengguna menyetujuinya.
4. Uji RLS memakai setidaknya dua user, termasuk query yang memalsukan `user_id`.
5. Tetapkan retention, export/delete user data, backup dan incident process sebelum menyimpan data nyata.

## Tahap E — AI opsional

1. Tambahkan `OPENAI_API_KEY` hanya melalui secrets manager platform, server-side.
2. Jelaskan provider, data yang dikirim, tujuan, dan retensi; dapatkan consent AI khusus sebelum memanggil `OpenAIJobAssistant`.
3. Minimalkan/redaksi PII, batasi input, gunakan output schema yang divalidasi, timeout/kuota, dan fallback ke rule-based triage.
4. Perlakukan body email sebagai input tidak tepercaya dan prompt-injection-capable. Model tidak boleh memiliki tools Gmail/database atau melakukan tindakan.
5. Jangan kirim semua inbox secara batch tanpa pilihan pengguna yang jelas.

## Tahap F — tindakan email

Untuk prototipe, pertahankan hanya read-only. Jangan aktifkan send/delete/move/label/unsubscribe. Jika kelak dibutuhkan, desain ulang dengan preview tindakan, konfirmasi eksplisit per tindakan, verifikasi authorization server-side, approval sekali pakai yang tersimpan di server, audit log terlindungi, idempotency, batas batch, dan undo/rollback.

## Vercel

Repo memiliki `api/triage.py` untuk endpoint serverless stateless, bukan website Streamlit. Vercel dapat dipertimbangkan jika backend dipisah menjadi API. Streamlit UI tetap deploy di Streamlit Community Cloud atau hosting yang mendukung proses Streamlit persisten. Jangan menganggap endpoint triage yang ada menyediakan login atau akses Gmail.

## Checklist sebelum menghubungkan inbox nyata

- [ ] Login/signup/reset password berjalan lewat Supabase Auth; password tidak disimpan aplikasi.
- [ ] RLS diuji untuk mencegah akses silang antar pengguna.
- [ ] OAuth Gmail state/CSRF, redirect, token storage, revoke, dan scope read-only ditinjau.
- [ ] Consent Gmail, persistence, dan AI terpisah, jelas, dan dapat dicabut.
- [ ] Secrets tidak muncul di source, client, URL, logs, atau session state yang tidak aman.
- [ ] Uji prompt injection, payload malformed/oversize, kegagalan provider, dan akses lintas akun.
- [ ] Rate limit, logging redacted, privacy/retention policy, dan proses penghapusan tersedia.
- [ ] Tidak ada Gmail write action aktif sebelum review keamanan dan approval flow lengkap.

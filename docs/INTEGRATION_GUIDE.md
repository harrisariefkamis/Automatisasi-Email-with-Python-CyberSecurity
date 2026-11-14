# Panduan Integrasi Email dan AI

Dokumen ini adalah rencana implementasi untuk menghubungkan package `src/email_assistant` dengan penyedia email dan AI secara bertahap. **Fitur-fitur yang dijelaskan belum terpasang atau aktif.** Demo sekarang hanya memproses teks yang dimasukkan pengguna.

## Rancangan alur

```text
UI / API
  -> application service (use case)
  -> email provider adapter (OAuth, awalnya read-only)
  -> normalisasi email -> rules/core triage
  -> optional AI adapter untuk ringkasan/ekstraksi terstruktur
  -> hasil dan sumber disimpan dengan kebijakan privasi
  -> UI menampilkan hasil dan meminta persetujuan untuk tindakan
```

Jangan memberi model AI akses langsung ke API email. Isi email adalah input tidak tepercaya dan dapat berisi prompt injection; gunakan AI hanya untuk menghasilkan saran/data terstruktur yang divalidasi oleh kode.

## Tahap 1 — tetapkan kebutuhan dan batas keamanan

1. Tentukan penyedia yang akan didukung (misalnya Gmail saja untuk MVP), data apa yang benar-benar diperlukan, serta kebijakan retensi dan penghapusan.
2. Mulai dengan **read-only**. Jangan mengimplementasikan kirim, hapus, pindah, label, atau unsubscribe pada tahap awal.
3. Tulis threat model ringkas: OAuth token, isi email sensitif, tautan berbahaya, prompt injection, log yang tidak sengaja memuat PII, dan akses lintas pengguna.
4. Tentukan consent UX. Pengguna harus tahu data email apa yang dibaca dan apakah isi dikirim ke layanan AI eksternal.

## Tahap 2 — implementasikan konfigurasi dengan aman

`.env.example` hanya daftar nama variabel. Kode saat ini belum membaca `.env`. Setelah memilih implementasi konfigurasi:

1. Tambahkan dependency konfigurasi bila perlu (misalnya `pydantic-settings` atau loader dotenv), lalu buat `src/email_assistant/config.py` untuk membaca environment dan memvalidasi nilai.
2. Fail fast jika mode/provider tertentu aktif tetapi konfigurasinya tidak lengkap. Jangan mencetak nilai rahasia ke log atau error.
3. Simpan `.env` lokal (sudah dikecualikan oleh `.gitignore`); gunakan secret manager untuk deployment. Jangan pernah menyimpan refresh/access token di `.env` atau Git.
4. Tambahkan pengujian konfigurasi dengan nilai dummy dan pastikan error tidak membocorkan secret.
5. Pertahankan `ACTIONS_ENABLED=false`; flag itu bukan pengganti consent, otorisasi server, dan pemeriksaan kebijakan.

Variabel template mencakup mode aplikasi, logging, URL database, provider email, OAuth client ID/secret, callback/scopes, provider/model AI, API key AI, dan flag tindakan. Nama variabel baru hanya berpengaruh setelah dibaca oleh kode.

## Tahap 3 — integrasi email read-only

1. Buat project OAuth di konsol resmi provider, daftarkan redirect URI lokal/deployment yang tepat, dan simpan client secret di secret manager. Jangan meminta password email pengguna.
2. Minta scope Gmail sekecil mungkin untuk use case awal—template memakai `gmail.readonly`. Periksa persyaratan verifikasi/consent provider sebelum distribusi publik.
3. Implementasikan `integrations/email_provider.py` sebagai interface provider dan `gmail_client.py` sebagai adapter konkret. Adapter harus menangani pagination, rate limit, timeout, retry terbatas, dan error tanpa mencatat isi email.
4. Buat alur OAuth state/CSRF yang tervalidasi. Simpan token secara terenkripsi dan terikat pada akun pengguna; sediakan revoke/disconnect.
5. Buat `services/sync_service.py` untuk mengambil hanya field yang diperlukan, membatasi ukuran/jumlah pesan, dan menormalkan HTML menjadi teks dengan aman. Jangan membuka URL yang terkandung di pesan secara otomatis.
6. Tambahkan unit test dengan provider mock dan integration test terpisah memakai akun uji. Uji kasus token kedaluwarsa, rate limit, email malformed, dan tidak ada akses lintas akun.
7. Pastikan UI jelas menyatakan bahwa sinkronisasi membaca pesan. Jangan mulai polling inbox tanpa tindakan/consent yang jelas.

## Tahap 4 — hubungkan ke triase yang sudah ada

1. Pertahankan `core.triage_email()` sebagai fungsi domain yang menerima objek email normal, bukan objek SDK Gmail.
2. Adapter mengubah pesan provider menjadi bentuk internal minimal, contohnya `from`, `subject`, `body`, dan header yang relevan.
3. `classify_service.py` memanggil fungsi triase dan mengembalikan hasil terstruktur; jangan campur kode provider/UI dengan aturan domain.
4. Tambahkan tes untuk format email multi-part, HTML, header hilang, karakter Unicode, teks kosong, dan ukuran maksimum.
5. Tampilkan alasan klasifikasi dan label sebagai saran. Tetap sediakan cara pengguna mengoreksi hasil.

## Tahap 5 — tambahkan AI sebagai fitur opsional

1. Definisikan kebutuhan spesifik (contohnya ringkasan lowongan dan ekstraksi jabatan/lokasi/kualifikasi), sebelum memilih provider/model.
2. Implementasikan `integrations/ai_client.py` di balik interface yang dapat di-mock. `AI_API_KEY` hanya dibaca server dari secret store/environment; jangan kirim ke browser atau Streamlit client state.
3. Kirim data seminimal mungkin. Redaksi alamat email, nomor telepon, dan PII lain bila tidak diperlukan; minta consent sebelum mengirim isi email ke provider eksternal.
4. Anggap teks email sebagai data, bukan instruksi. Instruksi sistem harus memerintahkan model untuk tidak mengikuti perintah yang tertanam dalam email dan tidak melakukan tindakan eksternal.
5. Validasi output terhadap schema/allowlist, batasi panjang input/output, timeout, biaya, dan jumlah retry. Jika provider gagal, tetap tampilkan triase rule-based.
6. Catat metadata operasional seperlunya, bukan isi email, prompt lengkap, token, atau kredensial. Dokumentasikan retensi dan provider yang menerima data.
7. Uji dengan prompt injection, output invalid, konten berbahaya, PII, dan respons provider yang gagal. Evaluasi kualitas pada data uji yang aman dan berizin.

## Tahap 6 — storage, audit, dan UI

- Definisikan `models/email.py`, `job.py`, dan `audit_log.py` hanya untuk atribut yang dibutuhkan; hindari menyimpan body email secara permanen jika tidak perlu.
- Gunakan `storage/database.py` dan `repositories.py` untuk isolasi database, migration, kontrol akses per pengguna, serta retensi/penghapusan.
- UI harus membedakan hasil rule-based dan AI, menunjukkan ketidakpastian, dan memungkinkan pengguna menghapus data atau mencabut koneksi.
- Jangan meletakkan token, secret, body email, atau prompt sensitif di URL, browser logs, telemetry, atau exception.

## Tahap 7 — persetujuan tindakan (hanya setelah read-only matang)

Jika nantinya ada label/pindah/hapus/unsubscribe:

1. Pisahkan rekomendasi dari eksekusi. AI hanya boleh mengusulkan tindakan dari daftar yang diperbolehkan.
2. Tampilkan target dan konsekuensi secara spesifik; minta konfirmasi eksplisit tepat sebelum eksekusi.
3. Verifikasi identitas/otorisasi pengguna di server, cek ulang pesan dan policy, gunakan idempotency, dan batasi batch.
4. Mulai dengan tindakan yang dapat dibatalkan (misalnya label) dan buat dry-run. Jangan otomatis menghapus email atau unsubscribe.
5. Catat audit log tanpa menyimpan konten sensitif yang tidak diperlukan; sediakan undo bila provider mendukungnya.
6. Uji bahwa tindakan tidak pernah dijalankan ketika flag mati, konfirmasi tidak ada, policy gagal, atau input AI malformed.

## Pemetaan package saat ini ke pekerjaan

| Path | Peran yang direncanakan | Status |
|---|---|---|
| `core.py` | Triase aturan dan petunjuk analisis | Sudah aktif untuk demo teks |
| `chat.py` | Chat lokal berbasis aturan | Sudah aktif, bukan AI |
| `cli.py` | CLI JSON | Sudah aktif |
| `api/` | Routes dan schemas | Placeholder |
| `integrations/` | Email provider dan AI client | Placeholder |
| `services/` | Use-case/sinkronisasi/triase | Placeholder |
| `agents/` | Orkestrasi terbatas | Placeholder; tidak perlu dibuat otonom |
| `rules/` | Kebijakan klasifikasi dan tindakan | Placeholder |
| `models/` | Domain models | Placeholder |
| `storage/` | Repository dan database | Placeholder |
| `.env.example` | Dokumentasi konfigurasi potensial | Template saja, belum dibaca kode |

## Checklist sebelum mengaktifkan koneksi nyata

- [ ] OAuth, callback state, revoke, dan izin minimum telah diuji.
- [ ] Rahasia/token disimpan di tempat aman dan tidak muncul dalam log.
- [ ] Read-only adalah default; pengguna memberi consent yang jelas.
- [ ] Batas ukuran, pagination, timeout, rate limit, dan isolasi akun diuji.
- [ ] Tidak ada konten email yang dikirim ke AI tanpa disclosure/consent dan minimisasi data.
- [ ] AI tidak dapat memanggil provider email atau mengeksekusi tindakan.
- [ ] Hasil AI divalidasi; fallback rule-based tersedia.
- [ ] Tindakan tulis mati secara default dan membutuhkan approval yang dapat diaudit.
- [ ] Kebijakan privasi, retensi, penghapusan, deployment, dan incident response didokumentasikan.

# Asisten Triase Email Lowongan

Aplikasi demo lokal berbasis Python untuk membantu meninjau email dan mengenali kemungkinan email lowongan kerja, langganan, atau spam. Hasilnya berupa saran untuk ditinjau secara manual—bukan keputusan otomatis.

> **Privasi dan keamanan:** Versi saat ini tidak terhubung ke akun atau inbox email. Aplikasi hanya menganalisis teks yang Anda masukkan, dan tidak mengirim, menghapus, memblokir, atau melakukan unsubscribe terhadap email.

## Fitur saat ini

- Mengelompokkan email ke kategori `job`, `subscription_review`, `spam_review`, atau `general_review` menggunakan aturan dan kata kunci sederhana.
- Menampilkan label, alasan, dan tingkat keyakinan sebagai petunjuk triase.
- Memberikan petunjuk tinjauan lowongan, termasuk kata kunci yang cocok dan URL aplikasi jika ditemukan.
- Menyediakan antarmuka demo dengan Streamlit serta antarmuka command line yang menghasilkan JSON.
- Menyertakan chat demo berbasis aturan lokal; chat ini bukan model AI dan tidak memakai layanan AI eksternal.

## Struktur proyek saat ini

Berikut struktur yang benar-benar tersedia di repositori saat ini:

```text
.
├── app.py                       # Antarmuka web demo menggunakan Streamlit
├── pyproject.toml               # Konfigurasi proyek, dependensi, dan perintah CLI
├── src/
│   └── email_assistant/
│       ├── __init__.py          # Inisialisasi package
│       ├── chat.py              # Respons chat demo berbasis aturan lokal
│       ├── cli.py               # Antarmuka command line untuk input JSON
│       └── core.py              # Logika triase dan analisis email
└── tests/
    └── test_core.py             # Pengujian untuk logika triase email
```

## Rencana struktur pengembangan

Struktur berikut adalah rancangan untuk pengembangan bertahap, **bukan daftar file yang sudah tersedia**. Integrasi email, AI, database, dan tindakan otomatis belum diimplementasikan.

```text
email-job-assistant/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── chat_routes.py          # Endpoint chatbox AI
│   ├── integrations/
│   │   ├── email_provider.py
│   │   ├── gmail_client.py
│   │   └── ai_client.py            # Koneksi ke model AI
│   ├── services/
│   │   ├── sync_service.py         # Sinkronisasi inbox, sent, drafts, trash, label
│   │   ├── classify_service.py
│   │   ├── job_analysis_service.py # Analisis dan ringkasan lowongan
│   │   ├── chat_service.py         # Konteks dan jawaban chatbox AI
│   │   ├── label_service.py
│   │   ├── spam_service.py
│   │   ├── subscription_service.py # Deteksi dan usulan unsubscribe
│   │   ├── cleanup_service.py      # Aturan pemindahan email ke Trash
│   │   ├── draft_service.py
│   │   └── action_service.py       # Tindakan yang sudah disetujui pengguna
│   ├── agents/
│   │   ├── email_agent.py          # Orkestrasi dengan batasan tindakan
│   │   ├── job_agent.py            # Analisis lowongan dengan keluaran terstruktur
│   │   └── prompts.py
│   ├── rules/
│   │   ├── classification.py
│   │   ├── cleanup.py              # Umur email, pengirim, label, pengecualian
│   │   └── actions.py              # Izin dan konfirmasi tindakan
│   ├── models/
│   │   ├── email.py
│   │   ├── job.py
│   │   ├── subscription.py
│   │   ├── chat_message.py
│   │   └── audit_log.py
│   └── storage/
│       ├── database.py
│       └── repositories.py
├── frontend/
│   ├── pages/
│   │   ├── inbox.py
│   │   ├── jobs.py                 # Daftar dan analisis lowongan
│   │   └── settings.py             # Aturan cleanup dan persetujuan
│   └── components/
│       ├── ai_chatbox.py
│       ├── job_summary_card.py
│       └── cleanup_review.py
├── tests/
│   ├── test_classification.py
│   ├── test_job_analysis.py
│   ├── test_unsubscribe.py
│   ├── test_cleanup_rules.py
│   └── test_action_approval.py
├── .env.example
├── pyproject.toml
└── README.md
```

## Persyaratan

- Python 3.11 atau lebih baru
- `pip`

## Instalasi

Klon repositori, lalu jalankan dari direktori proyek:

```bash
python -m venv .venv
```

Aktifkan virtual environment:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Pasang aplikasi dan dependensinya:

```bash
python -m pip install --upgrade pip
pip install -e .
```

## Menjalankan aplikasi web

```bash
streamlit run app.py
```

Buka alamat lokal yang ditampilkan Streamlit di terminal, lalu masukkan pengirim, subjek, dan isi email untuk melihat hasil triase.

## Menggunakan command line

Buat file JSON, misalnya `email.json`:

```json
{
  "from": "recruiter@example.com",
  "subject": "Job opening: Python developer",
  "body": "We are hiring. Apply at https://example.org/jobs",
  "headers": {}
}
```

Jalankan perintah berikut:

```bash
email-assistant email.json
```

Output akan berisi hasil triase dalam format JSON. Field `headers` bersifat opsional; jika tersedia, aplikasi dapat memeriksa header `List-Unsubscribe` sebagai salah satu petunjuk langganan.

## Menjalankan pengujian

```bash
python -m unittest discover -s tests
```

## Kekurangan proyek saat ini

- **Masih berupa demo lokal:** belum ada API backend, autentikasi pengguna, database, atau sinkronisasi dengan penyedia email.
- **Klasifikasi berbasis kata kunci:** dapat salah mengategorikan email, tidak memahami konteks, dan belum diuji dengan dataset yang representatif.
- **Skor keyakinan sederhana:** nilai yang ditampilkan berasal dari aturan tetap, bukan probabilitas terkalibrasi.
- **Analisis lowongan terbatas:** hanya memberi petunjuk dari teks dan URL; tidak memverifikasi perusahaan, pengirim, tautan, atau keabsahan lowongan.
- **Chat bukan AI:** respons ditentukan oleh aturan lokal dan tidak melakukan analisis percakapan yang mendalam.
- **Cakupan pengujian dasar:** pengujian saat ini mencakup logika inti triase, belum mencakup antarmuka, integrasi eksternal, keamanan, maupun alur persetujuan tindakan.
- **Belum ada panduan operasional lengkap:** belum tersedia konfigurasi deployment, pemantauan, kebijakan retensi data, atau dokumentasi privasi yang rinci.

## Yang perlu ditambahkan ke repositori

Prioritaskan pengembangan secara bertahap agar fondasi aman sebelum menghubungkan akun email:

1. **Perluas pengujian dan kualitas kode:** tambah pengujian untuk kasus tepi dan kesalahan input, lalu siapkan lint/type-check dan workflow CI.
2. **Tetapkan konfigurasi dan rahasia:** buat `.env.example` tanpa kredensial asli, validasi konfigurasi, dan jangan pernah commit token, kata sandi, atau data email.
3. **Rancang model dan penyimpanan:** tentukan skema email, hasil analisis, persetujuan, serta audit log; dokumentasikan retensi dan penghapusan data.
4. **Pisahkan lapisan aplikasi:** jika proyek berkembang, pisahkan API, layanan, integrasi, frontend, dan penyimpanan dengan batas tanggung jawab yang jelas.
5. **Tambahkan integrasi email secara bertahap:** mulai dengan mode baca-saja, OAuth dengan izin minimum, dan data uji/mock sebelum akses akun sungguhan.
6. **Tambahkan AI hanya bila diperlukan:** buat adapter provider, validasi keluaran terstruktur, batas biaya/waktu, dan kebijakan agar data sensitif tidak dikirim tanpa persetujuan.
7. **Bangun persetujuan tindakan:** preview tindakan, konfirmasi eksplisit per tindakan, pengecualian, dan audit log. Jangan menghapus, memindahkan, mengirim, atau unsubscribe secara otomatis.
8. **Dokumentasikan penggunaan dan deployment:** tambahkan panduan konfigurasi, batasan, penanganan error, backup/pemulihan, serta prosedur pelaporan masalah keamanan.

## Batasan dan keamanan

- Klasifikasi menggunakan pencocokan kata kunci sederhana, sehingga hasilnya dapat keliru atau melewatkan konteks tertentu.
- Analisis bukan verifikasi keamanan atau keaslian email. Periksa pengirim dan tautan secara mandiri sebelum mengambil tindakan.
- Versi saat ini tidak terhubung ke inbox dan tidak melakukan tindakan pada email.
- Jika integrasi tindakan ditambahkan kelak, tindakan harus tetap nonaktif secara default dan hanya dijalankan setelah pengguna meninjau serta menyetujuinya secara eksplisit.

## Teknologi

- Python 3.11+
- Streamlit
- `unittest` untuk pengujian

## Lisensi

Belum ada lisensi yang ditentukan. Tambahkan file lisensi sebelum menggunakan atau mendistribusikan proyek ini jika diperlukan.

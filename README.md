# Asisten Triase Email Lowongan

Demo lokal berbasis Python untuk membantu meninjau email lowongan kerja, langganan, dan spam. Aplikasi menyediakan antarmuka Streamlit dan CLI. Hasil klasifikasi adalah petunjuk berbasis aturan yang perlu diperiksa manusia.

> **Status:** prototipe lokal. Belum terhubung ke inbox, database, atau layanan AI. Demo hanya menganalisis teks yang dimasukkan pengguna dan tidak mengirim, menghapus, memindahkan, memblokir, atau melakukan unsubscribe terhadap email.

## Yang tersedia

- Triase berbasis kata kunci untuk lowongan, langganan, spam, dan email umum.
- Petunjuk analisis lowongan, termasuk kata kunci yang cocok dan URL yang terdeteksi.
- UI lokal Streamlit, CLI JSON, dan chat demo berbasis aturan.
- Pengujian unit untuk perilaku utama triase.

## Teknologi

Python 3.11+, Streamlit, setuptools, dan `unittest`.

## Mulai cepat

```bash
python -m venv .venv
```

Aktifkan environment:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Pasang proyek dan jalankan aplikasi:

```bash
python -m pip install --upgrade pip
pip install -e .
streamlit run app.py
```

Streamlit akan menampilkan alamat lokal di terminal. Masukkan pengirim, subjek, dan isi email untuk melihat hasil triase.

## CLI

Buat file JSON, misalnya `email.json`:

```json
{
  "from": "recruiter@example.com",
  "subject": "Job opening: Python developer",
  "body": "We are hiring. Apply at https://example.org/jobs",
  "headers": {}
}
```

Jalankan:

```bash
email-assistant email.json
```

CLI mencetak hasil triase dalam JSON. `headers` opsional; header `List-Unsubscribe` dapat menjadi petunjuk langganan.

## Pengujian

```bash
python -m unittest discover -s tests
```

## Struktur repositori

```text
.
├── app.py
├── pyproject.toml
├── .env.example                  # Template untuk konfigurasi masa depan; belum dibaca aplikasi
├── src/email_assistant/
│   ├── api/                      # Kerangka untuk lapisan API
│   ├── agents/                   # Kerangka orkestrasi; belum ada agent AI
│   ├── integrations/             # Kerangka adapter; belum terhubung ke provider
│   ├── models/                   # Kerangka model domain
│   ├── rules/                    # Kerangka aturan dan kebijakan
│   ├── services/                 # Kerangka layanan aplikasi
│   ├── storage/                  # Kerangka penyimpanan; belum memakai database
│   ├── chat.py                   # Chat demo berbasis aturan
│   ├── cli.py                    # CLI input JSON
│   └── core.py                   # Logika triase saat ini
└── tests/
    └── test_core.py
```

Folder `api`, `agents`, `integrations`, `models`, `rules`, `services`, dan `storage` adalah kerangka package untuk membantu pengembangan bertahap; belum berisi fitur integrasi produksi. UI saat ini berada di `app.py`, belum dipecah menjadi frontend terpisah.

## Konfigurasi environment

`.env.example` mendokumentasikan opsi konfigurasi yang mungkin diperlukan kelak. Aplikasi saat ini **belum memuat file `.env` maupun membaca variabel tersebut**. Salin menjadi `.env` hanya saat implementasi konfigurasi tersedia, dan jangan commit nilai rahasia. Jangan masukkan kredensial nyata ke contoh atau issue.

## Kekurangan dan langkah pengembangan

- **Deteksi sederhana:** pencocokan kata kunci berpotensi salah dan belum dievaluasi pada dataset yang beragam. Tambahkan kasus uji, data evaluasi yang aman, dan dokumentasikan false positive/negative.
- **Skor belum terkalibrasi:** confidence berasal dari aturan tetap, bukan probabilitas terukur.
- **Tidak ada integrasi email:** belum tersedia OAuth, sinkronisasi, penyimpanan, autentikasi pengguna, maupun pengelolaan token. Jika ditambahkan, mulai dengan mode baca-saja dan izin minimum.
- **Analisis lowongan tidak memverifikasi keaslian:** pengguna tetap harus memeriksa pengirim, perusahaan, domain, tautan, dan klaim secara mandiri.
- **Chat bukan AI:** respons lokal berbasis aturan, tanpa model atau layanan AI.
- **Belum siap produksi:** belum ada CI, logging operasional, deployment, kebijakan retensi data, atau dokumentasi threat/privacy yang lengkap.

Urutan yang disarankan: perluas test dan CI; implementasikan konfigurasi tervalidasi tanpa membocorkan rahasia; definisikan model dan penyimpanan; tambahkan provider email baca-saja dengan OAuth; kemudian rancang AI opsional dengan perlindungan data. Setiap tindakan yang mengubah email harus nonaktif secara default, ditampilkan sebagai preview, mendapat persetujuan eksplisit pengguna, dan dicatat dalam audit log. Jangan mengaktifkan delete, move, send, atau unsubscribe otomatis.

## Batasan

Klasifikasi maupun petunjuk URL bukan pemeriksaan keamanan atau verifikasi lowongan. Periksa semua informasi secara mandiri sebelum bertindak. Kandidat pembersihan langganan hanyalah sinyal untuk ditinjau—demo tidak menghapus atau unsubscribe email.

## Lisensi

Repositori ini belum menetapkan lisensi. Tambahkan file lisensi sebelum menetapkan hak penggunaan dan distribusi proyek.

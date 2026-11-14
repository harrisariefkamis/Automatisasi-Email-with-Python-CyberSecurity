# Asisten Triase Email Lowongan

Aplikasi demo lokal berbasis Python untuk membantu meninjau email dan mengenali kemungkinan email lowongan kerja, langganan, atau spam. Hasilnya berupa saran untuk ditinjau secara manual—bukan keputusan otomatis.

> **Privasi dan keamanan:** Aplikasi ini tidak terhubung ke akun atau inbox email. Aplikasi hanya menganalisis teks yang Anda masukkan, dan tidak mengirim, menghapus, memblokir, atau melakukan unsubscribe terhadap email.

## Fitur

- Mengelompokkan email ke kategori `job`, `subscription_review`, `spam_review`, atau `general_review` menggunakan aturan dan kata kunci sederhana.
- Menampilkan label, alasan, dan tingkat keyakinan sebagai petunjuk triase.
- Memberikan petunjuk tinjauan lowongan, termasuk kata kunci yang cocok dan URL aplikasi jika ditemukan.
- Menyediakan antarmuka demo dengan Streamlit serta antarmuka command line yang menghasilkan JSON.
- Menyertakan chat demo berbasis aturan lokal; chat ini bukan model AI dan tidak memakai layanan AI eksternal.

## Struktur Proyek

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

## Batasan

- Klasifikasi menggunakan pencocokan kata kunci sederhana, sehingga hasilnya dapat keliru atau melewatkan konteks tertentu.
- Skor keyakinan hanyalah petunjuk dari aturan lokal, bukan probabilitas terkalibrasi.
- Analisis lowongan tidak memverifikasi perusahaan, pengirim, tautan, maupun keabsahan lowongan. Periksa semuanya secara mandiri sebelum mengambil tindakan.
- Kandidat pembersihan langganan hanya rekomendasi peninjauan; aplikasi tidak menghapus email atau melakukan unsubscribe.
- Chat demo memberikan respons berbasis aturan, bukan kecerdasan buatan.

## Teknologi

- Python 3.11+
- Streamlit
- `unittest` untuk pengujian

## Lisensi

Belum ada lisensi yang ditentukan. Tambahkan file lisensi sebelum menggunakan atau mendistribusikan proyek ini jika diperlukan.

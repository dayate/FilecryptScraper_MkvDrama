# ⛨ FilecryptScraper - MKVDRAMA

<div align="center">
   <img width="500px" src="https://i.imgur.com/mveaeCj.jpeg">

   <br>
   <span><i>Scraper Download URL untuk <strong>filecrypt.co</strong> dari situs mkvdrama.me</i></span>
   <br>
</div>

---

> 👋 Program ini berfungsi untuk melakukan scraping Download URL Movies atau Series dari situs **MkvDrama.me** ..Hanya mendukung URL **filecrypt.co** dari situs **mkvdrama.me** :

## 💻 Installation & Setup

### Installation
```
git clone https://github.com/dayate/FilecryptScraper_MkvDrama.git
cd FilecryptScraper_MKVDrama
pip install -r requirements.txt
```

### Setup (Cara Mudah)
1. Download Extensions Adblock Sesuai Selera
2. Extrak Extensions
3. Buat Folder Extension di dalam direktori FilecryptScraper_MKVDrama/
4. Copy Hasil Extrak ke folder Extensions Tersebut
5. Jalankan script setup otomatis:
```
python setup_env.py
```
6. Ikuti petunjuk untuk mengatur path ekstensi dan konfigurasi lainnya

### Setup (Manual)
1. Download Extensions Adblock Sesuai Selera
2. Extrak Extensions
3. Buat Folder Extension di dalam direktori FilecryptScraper_MKVDrama/
4. Copy Hasil Extrak ke folder Extensions Tersebut
5. Salin file `env.example` menjadi `.env`
6. Edit file `.env` sesuai dengan konfigurasi Anda, terutama bagian `EXTENSIONS_PATHS` untuk mengarah ke folder Extensions yang telah dibuat

### Konfigurasi
Semua konfigurasi aplikasi sekarang dikelola melalui file `.env`. Berikut beberapa konfigurasi penting:

#### Konfigurasi Browser
```
# Path ke direktori profil browser
BROWSER_USER_DATA_DIR=./profile

# Mode headless browser (True/False)
BROWSER_HEADLESS=False

# Argumen browser tambahan
BROWSER_ARGS=--disable-component-update,--no-sandbox,--disable-dev-shm-usage
```

#### Konfigurasi Extensions
```
# Path ke ekstensi browser (ganti dengan path yang sesuai)
# PENTING: Gunakan double backslash (\\) untuk path Windows
EXTENSIONS_PATHS=C:\\Users\\username\\FilecryptScraper_MkvDrama\\Extensions\\uBlock
```

#### Konfigurasi Scraper
```
# Aktifkan pemrosesan batch (True/False)
SCRAPER_BATCH_PROCESSING=True

# Jumlah maksimal batch untuk scraping
SCRAPER_MAX_BATCH_SIZE=8
```

Untuk konfigurasi lengkap, silakan lihat file `env.example`.

### Running
```
python main.py
```

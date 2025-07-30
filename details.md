## Struktur Project
```
📂 FilecryptScraper_MkvDrama
├── 📁 config
│   ├── 📄 __init__.py
│   └── 📄 settings.py
├── 📁 core
│   ├── 📄 __init__.py
│   ├── 📄 browser.py
│   ├── 📄 database.py
│   ├── 📄 file_handler.py
│   ├── 📄 logger.py
│   ├── 📄 scraper.py
│   ├── 📄 sqlite_handler.py
│   └── 📄 utils.py
├── 📁 models
│   ├── 📄 __init__.py
│   └── 📄 data_models.py
├── 📁 Extensions
│   ├── 📁 Adguard
│   └── 📁 uBlock
├── 📁 profile
├── 📁 results
├── 📁 logs
├── 📄 config.yaml
├── 📄 main.py
└── 📄 setup_profile.py
```

## Isi File
1. config.yaml
```
# Konfigurasi Browser
browser:
  user_data_dir: "./profile"
  headless: false
  args:
    - "--disable-component-update"
    - "--no-sandbox"
    - "--disable-dev-shm-usage"
    - "--disable-webgl"
    - "--disable-blink-features=AutomationControlled"
    - "--disable-infobars"
  ignore_default_args:
    - "--enable-automation"

# Konfigurasi Extensions
# PENTING: Sesuaikan path ini dengan lokasi ekstensi di sistem Anda
extensions:
  paths:
    - "C:\\Users\\txxfxxk\\Project\\FilecryptScraper_MkvDrama\\Extensions\\Adguard"

# Konfigurasi Logging
logging:
  log_dir: "logs"
  level: "INFO"
  format: "%(asctime)s - %(levelname)-4s - %(message)s"
  datefmt: "%Y-%m-%d %H:%M:%S"

# Konfigurasi Timeouts (dalam milidetik atau detik)
timeouts:
  selector_wait: 10000
  popup: 5000
  page_load: 30000
  password_check: 5
  captcha_check: 5
  batch_delay: 1
  captcha: 300
  password: 300

# Konfigurasi Provider
providers:
  send_aliases:
    - "send.cm"
    - "sendit.cloud"
    - "send.co"
    - "send.now"
    - "send.com"
    - "send.cw"

# Konfigurasi Pixeldrain
pixeldrain:
  bypass_urls:
    - "https://pd.cybar.xyz/CODE-FILE"

# Konfigurasi Scraper
scraper:
  batch_processing: true
  max_batch_size: 8

# User Agents
user_agents:
  - "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
  - "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0"

```
2. config/settings.py
```
# config/settings.py

import yaml
from pydantic import BaseModel, Field
from typing import List, Literal
import os

# --- Model Pydantic untuk Struktur Konfigurasi ---
# Kita tetap menggunakan Pydantic untuk validasi tipe data dan struktur,
# namun menggunakan BaseModel standar karena data dimuat dari file, bukan .env.


class BrowserSettings(BaseModel):
    user_data_dir: str = os.path.abspath("./profile")
    headless: bool = False
    args: List[str] = []
    ignore_default_args: List[str] = []


class ExtensionsSettings(BaseModel):
    paths: List[str] = []


class LoggingSettings(BaseModel):
    log_dir: str = "logs"
    level: Literal["INFO", "DEBUG", "WARNING", "ERROR"] = "INFO"
    format: str = "%(asctime)s - %(levelname)-4s - %(message)s"
    datefmt: str = "%Y-%m-%d %H:%M:%S"


class TimeoutSettings(BaseModel):
    selector_wait: int = 10000
    popup: int = 5000
    page_load: int = 30000
    password_check: int = 5
    captcha_check: int = 5
    batch_delay: int = 1
    captcha: int = 300
    password: int = 300


class ProviderSettings(BaseModel):
    send_aliases: List[str] = []


class PixeldrainSettings(BaseModel):
    bypass_urls: List[str] = []


class ScraperSettings(BaseModel):
    batch_processing: bool = True
    max_batch_size: int = 8


class AppSettings(BaseModel):
    """Model utama yang menggabungkan semua pengaturan."""

    browser: BrowserSettings
    extensions: ExtensionsSettings
    logging: LoggingSettings
    timeouts: TimeoutSettings
    providers: ProviderSettings
    pixeldrain: PixeldrainSettings
    scraper: ScraperSettings
    user_agents: List[str] = []


def load_config_from_yaml(path: str = "config.yaml") -> AppSettings:
    """
    Memuat konfigurasi dari file YAML dan mengembalikannya sebagai instance AppSettings.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
        # Inisialisasi model Pydantic dengan data dari dictionary YAML
        return AppSettings(**config_data)
    except FileNotFoundError:
        raise SystemExit(
            f"ERROR: File konfigurasi '{path}' tidak ditemukan. Pastikan file tersebut ada di root proyek."
        )
    except Exception as e:
        raise SystemExit(
            f"ERROR: Gagal memuat atau mem-parsing file konfigurasi '{path}': {e}"
        )


# --- Instance Konfigurasi Global ---
# Ini adalah satu-satunya instance yang akan diimpor oleh modul lain.
# Perubahan pada config.yaml akan secara otomatis tercermin saat program dimulai ulang.
DEFAULT_CONFIG = load_config_from_yaml()


# Untuk debugging, jika diperlukan
if __name__ == "__main__":
    import json

    # Gunakan .model_dump_json() untuk Pydantic v2
    print(DEFAULT_CONFIG.model_dump_json(indent=2))

```
3. config/__init__.py
```
"""
Package untuk konfigurasi aplikasi
"""

# Ubah impor dari env_config ke settings
from .settings import DEFAULT_CONFIG

__all__ = ["DEFAULT_CONFIG"]

```
4. core/browser.py
```
"""
Modul untuk menangani operasi browser menggunakan Playwright
"""

from playwright.sync_api import sync_playwright
import logging
from typing import Optional
from config import DEFAULT_CONFIG
import os


class BrowserManager:
    """
    Kelas untuk mengelola browser dan konteksnya
    """

    def __init__(self, window_size: tuple[int, int] = None):
        self.config = DEFAULT_CONFIG.browser
        self.extensions = DEFAULT_CONFIG.extensions
        self.context = None
        self.playwright = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.launch_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_browser()
        if self.playwright:
            self.playwright.stop()

    def launch_browser(self):
        try:
            # --- MULAI BLOK KODE BARU ---
            # Logika untuk mendapatkan path ekstensi, sama seperti di setup_profile.py
            extension_folders = ["./Extensions/uBlock", "./Extensions/Adguard"]
            extension_paths = [
                os.path.abspath(folder)
                for folder in extension_folders
                if os.path.exists(os.path.abspath(folder))
            ]
            extensions_to_load_str = ",".join(extension_paths)
            # Gabungkan argumen dari config dengan argumen ekstensi
            all_args = self.config.args.copy()  # Salin argumen dasar
            if extension_paths:
                all_args.append(f"--disable-extensions-except={extensions_to_load_str}")
                all_args.append(f"--load-extension={extensions_to_load_str}")
            # --- SELESAI BLOK KODE BARU ---

            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.config.user_data_dir,
                headless=self.config.headless,
                viewport={"width": 500, "height": 650},
                args=all_args,
                ignore_default_args=self.config.ignore_default_args,
            )
            return self.context
        except Exception as e:
            logging.error(f"[ERROR] Gagal membuka browser: {str(e)}")
            raise

    def close_browser(self):
        if self.context:
            try:
                self.context.close()
            except Exception as e:
                logging.error(f"[ERROR] Gagal menutup browser: {str(e)}")

    def close_about_blank_tabs(self):
        main_pages = []
        for page in self.context.pages:
            if page.url == "about:blank":
                try:
                    if not page.is_closed():
                        page.close()
                except Exception as e:
                    logging.debug(f"[BROWSER] Gagal menutup tab: {e}")
            else:
                main_pages.append(page)
        return main_pages


```

5. core/database.py
```
"""
Modul untuk menangani penyimpanan data ke SQLite dan export ke Excel
"""

import sqlite3
import logging
import os
from typing import List
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment
from openpyxl.worksheet.worksheet import Worksheet
from models.data_models import ScrapedData


class DatabaseHandler:
    """Kelas untuk menangani penyimpanan dan pengambilan data dari SQLite"""

    DB_PATH = os.path.join("results", "scraped_data.db")

    @staticmethod
    def _init_db():
        """Inisialisasi database SQLite"""
        os.makedirs("results", exist_ok=True)
        conn = sqlite3.connect(DatabaseHandler.DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scraped_data (
                title TEXT,
                provider TEXT,
                size TEXT,
                status TEXT,
                download_url TEXT,
                bypass_url TEXT,
                target_code TEXT,
                PRIMARY KEY (title, provider, target_code)
            )
            """
        )
        conn.commit()
        conn.close()

    @staticmethod
    def save_to_sqlite(data: List[ScrapedData]) -> int:
        """Menyimpan data ke SQLite dan mengembalikan jumlah item baru"""
        DatabaseHandler._init_db()
        conn = sqlite3.connect(DatabaseHandler.DB_PATH)
        cursor = conn.cursor()
        new_items = 0

        for item in data:
            cursor.execute(
                """
                INSERT OR IGNORE INTO scraped_data
                (title, provider, size, status, download_url, bypass_url, target_code)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.title,
                    item.provider,
                    item.size,
                    item.status,
                    item.download_url,
                    item.bypass_url,
                    item.target_code,
                ),
            )
            if cursor.rowcount > 0:
                new_items += 1

        conn.commit()
        conn.close()
        if new_items > 0:
            logging.info(f"📥⠀Disimpan {new_items} item ke database")
        return new_items

    @staticmethod
    def is_data_exists(title: str, provider: str, target_code: str) -> bool:
        conn = sqlite3.connect(DatabaseHandler.DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 1 FROM scraped_data
            WHERE title = ? AND provider = ? AND target_code = ?
            """,
            (title, provider, target_code),
        )
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    @staticmethod
    def get_data_by_title_provider(
        title: str, provider: str, target_code: str
    ) -> ScrapedData | None:
        conn = sqlite3.connect(DatabaseHandler.DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT title, provider, size, status, download_url, bypass_url, target_code
            FROM scraped_data
            WHERE title = ? AND provider = ? AND target_code = ?
            """,
            (title, provider, target_code),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return ScrapedData(
                title=row[0],
                provider=row[1],
                size=row[2],
                status=row[3],
                download_url=row[4],
                bypass_url=row[5],
                target_code=row[6],
                container_title="N/A",
            )
        return None

    @staticmethod
    def get_all_data() -> List[ScrapedData]:
        conn = sqlite3.connect(DatabaseHandler.DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT title, provider, size, status, download_url, bypass_url, target_code
            FROM scraped_data
            """
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            ScrapedData(
                title=row[0],
                provider=row[1],
                size=row[2],
                status=row[3],
                download_url=row[4],
                bypass_url=row[5],
                target_code=row[6],
                container_title="N/A",
            )
            for row in rows
        ]

    @staticmethod
    def get_data_by_target_code(target_code: str) -> List[ScrapedData]:
        conn = sqlite3.connect(DatabaseHandler.DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT title, provider, size, status, download_url, bypass_url, target_code
            FROM scraped_data
            WHERE target_code = ?
            """,
            (target_code,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            ScrapedData(
                title=row[0],
                provider=row[1],
                size=row[2],
                status=row[3],
                download_url=row[4],
                bypass_url=row[5],
                target_code=row[6],
                container_title="N/A",
            )
            for row in rows
        ]

    @staticmethod
    def _is_sheet_empty(sheet: Worksheet) -> bool:
        return sheet.max_row <= 1

    @staticmethod
    def export_to_excel(data: List[ScrapedData], target_code: str):
        """Export data ke file Excel RESULT_DATABASE.xlsx"""
        if not data and not target_code:
            return

        os.makedirs("results", exist_ok=True)
        filename = os.path.join("results", "RESULT_DATABASE.xlsx")
        relevant_data = DatabaseHandler.get_data_by_target_code(target_code)
        combined_data = relevant_data[:]
        input_keys = {
            (
                item.title.lower().strip(),
                item.provider.lower().strip(),
                item.target_code.lower().strip(),
            )
            for item in data
        }

        for item in data:
            item_key = (
                item.title.lower().strip(),
                item.provider.lower().strip(),
                item.target_code.lower().strip(),
            )
            if item_key not in {
                (
                    d.title.lower().strip(),
                    d.provider.lower().strip(),
                    d.target_code.lower().strip(),
                )
                for d in relevant_data
            }:
                combined_data.append(item)

        if not combined_data:
            return

        try:
            if os.path.exists(filename):
                wb = load_workbook(filename)
                for sheet_name in wb.sheetnames[:]:
                    sheet = wb[sheet_name]
                    if (
                        DatabaseHandler._is_sheet_empty(sheet)
                        or sheet_name.lower() == "sheet"
                    ):
                        wb.remove(sheet)
            else:
                wb = Workbook()
                wb.remove(wb.active)

            all_sheet_name = "ALL_PROVIDER_RESULTS"
            if all_sheet_name not in wb.sheetnames:
                all_sheet = wb.create_sheet(all_sheet_name, 0)
                all_sheet.append(
                    [
                        "No",
                        "Title",
                        "Provider",
                        "Size",
                        "Status",
                        "Download URL",
                        "Bypass URL",
                        "_target_code",
                    ]
                )
            else:
                all_sheet = wb[all_sheet_name]

            existing_all_entries = set()
            for row in all_sheet.iter_rows(min_row=2, values_only=True):
                if row[1] and row[2] and row[7]:
                    existing_all_entries.add(
                        (
                            str(row[1]).lower().strip(),
                            str(row[2]).lower().strip(),
                            str(row[7]).lower().strip(),
                        )
                    )

            new_all_items = 0
            for item in combined_data:
                item_key = (
                    item.title.lower().strip(),
                    item.provider.lower().strip(),
                    item.target_code.lower().strip(),
                )
                if item_key not in existing_all_entries:
                    all_sheet.append(
                        [
                            all_sheet.max_row,
                            item.title,
                            item.provider,
                            item.size,
                            item.status,
                            item.download_url,
                            item.bypass_url,
                            item.target_code,
                        ]
                    )
                    existing_all_entries.add(item_key)
                    new_all_items += 1

            for idx, row in enumerate(all_sheet.iter_rows(min_row=2), 1):
                row[0].value = idx

            if DatabaseHandler._is_sheet_empty(all_sheet):
                wb.remove(all_sheet)

            providers = {item.provider for item in combined_data}
            for provider in providers:
                provider_items = [
                    item for item in combined_data if item.provider == provider
                ]
                provider_new_items = False
                existing_provider_entries = set()
                provider_sheet_name = provider[:31]
                if provider_sheet_name in wb.sheetnames:
                    provider_sheet = wb[provider_sheet_name]
                    for row in provider_sheet.iter_rows(min_row=2, values_only=True):
                        if row[1] and row[2] and row[7]:
                            existing_provider_entries.add(
                                (
                                    str(row[1]).lower().strip(),
                                    str(row[2]).lower().strip(),
                                    str(row[7]).lower().strip(),
                                )
                            )

                for item in provider_items:
                    item_key = (
                        item.title.lower().strip(),
                        item.provider.lower().strip(),
                        item.target_code.lower().strip(),
                    )
                    if item_key not in existing_provider_entries:
                        provider_new_items = True
                        break

                if provider_new_items:
                    if provider_sheet_name not in wb.sheetnames:
                        provider_sheet = wb.create_sheet(provider_sheet_name)
                        provider_sheet.append(
                            [
                                "No",
                                "Title",
                                "Provider",
                                "Size",
                                "Status",
                                "Download URL",
                                "Bypass URL",
                                "_target_code",
                            ]
                        )
                    else:
                        provider_sheet = wb[provider_sheet_name]

                    for item in provider_items:
                        item_key = (
                            item.title.lower().strip(),
                            item.provider.lower().strip(),
                            item.target_code.lower().strip(),
                        )
                        if item_key not in existing_provider_entries:
                            provider_sheet.append(
                                [
                                    provider_sheet.max_row,
                                    item.title,
                                    item.provider,
                                    item.size,
                                    item.status,
                                    item.download_url,
                                    item.bypass_url,
                                    item.target_code,
                                ]
                            )
                            existing_provider_entries.add(item_key)

                    for idx, row in enumerate(provider_sheet.iter_rows(min_row=2), 1):
                        row[0].value = idx

                    if DatabaseHandler._is_sheet_empty(provider_sheet):
                        wb.remove(provider_sheet)

            has_data = False
            for sheet_name in wb.sheetnames[:]:
                sheet = wb[sheet_name]
                if not DatabaseHandler._is_sheet_empty(sheet):
                    has_data = True
                else:
                    wb.remove(sheet)

            if not has_data or not wb.sheetnames:
                return

            if "Sheet" in wb.sheetnames:
                wb.remove(wb["Sheet"])

            for sheet in wb.sheetnames:
                ws = wb[sheet]
                column_widths = {
                    "A": 5,
                    "B": 60,
                    "C": 15,
                    "D": 10,
                    "E": 15,
                    "F": 60,
                    "G": 60,
                    "H": 15,
                }
                for col, width in column_widths.items():
                    ws.column_dimensions[col].width = width
                for row in ws.iter_rows():
                    for cell in row:
                        cell.alignment = Alignment(wrap_text=True, vertical="top")

            wb.save(filename)

        except Exception as e:
            logging.error(f"[ERROR] Gagal menyimpan Excel: {str(e)}")

```

6. core/file_handler.py
```
"""
Modul untuk menangani penyimpanan file individual
"""

import os
import re
import logging
from typing import List
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment
from openpyxl.worksheet.worksheet import Worksheet
from models.data_models import ScrapedData
from core.database import DatabaseHandler


class FileHandler:
    """Kelas untuk menangani penyimpanan file individual"""

    @staticmethod
    def _sanitize_filename(title: str, target_code: str = None) -> str:
        """
        Membersihkan nama file dan menghindari karakter tidak valid.
        Mengembalikan target_code hanya jika title benar-benar tidak valid.
        """
        logging.debug(f"📁⠀ Sanitizing title: {title}, target_code: {target_code}")
        if not title or title.strip().lower() in ("n/a", "unknown", ""):
            logging.warning(
                f"📁⠀ Title tidak valid ({title}), menggunakan target_code: {target_code}"
            )
            return target_code if target_code else "Untitled"

        # Ganti karakter tidak valid, kecuali titik
        cleaned_title = re.sub(r'[\/\\:*?"<>|]', "", title.strip())
        # Ganti beberapa spasi dengan titik
        cleaned_title = re.sub(r"\s+", ".", cleaned_title)
        max_length = 200
        cleaned_title = cleaned_title[:max_length]

        if not cleaned_title:
            logging.warning(
                f"📁⠀ Title kosong setelah pembersihan, menggunakan target_code: {target_code}"
            )
            return target_code if target_code else "Untitled"

        logging.debug(f"📁⠀ Sanitized title: {cleaned_title}")
        return cleaned_title

    @staticmethod
    def _is_sheet_empty(sheet: Worksheet) -> bool:
        return sheet.max_row <= 1

    @staticmethod
    def save_individual_files(
        data: List[ScrapedData], target_code: str, container_title: str = None
    ):
        """Menyimpan file individual berdasarkan container_title"""
        if not data or not target_code:
            logging.warning("📁⠀ Tidak ada data atau target_code untuk disimpan")
            return

        os.makedirs("results", exist_ok=True)
        relevant_data = DatabaseHandler.get_data_by_target_code(target_code)
        combined_data = relevant_data[:]
        input_keys = {
            (
                item.title.lower().strip(),
                item.provider.lower().strip(),
                item.target_code.lower().strip(),
            )
            for item in data
        }

        # Gunakan container_title dari parameter jika ada, jika tidak cari dari data
        selected_title = container_title
        if not selected_title:
            for item in data:
                if (
                    item.container_title
                    and item.container_title.strip().lower()
                    not in ("n/a", "unknown", "")
                ):
                    selected_title = item.container_title
                    break
            if not selected_title:
                for item in combined_data:
                    if (
                        item.container_title
                        and item.container_title.strip().lower()
                        not in ("n/a", "unknown", "")
                    ):
                        selected_title = item.container_title
                        break
            if not selected_title:
                logging.warning(
                    f"📁⠀ Tidak ada container_title valid untuk target_code {target_code}, menggunakan target_code"
                )
                selected_title = target_code

        # Tambahkan data baru ke combined_data
        for item in data:
            item_key = (
                item.title.lower().strip(),
                item.provider.lower().strip(),
                item.target_code.lower().strip(),
            )
            if item_key not in {
                (
                    d.title.lower().strip(),
                    d.provider.lower().strip(),
                    d.target_code.lower().strip(),
                )
                for d in relevant_data
            }:
                item.container_title = selected_title
                combined_data.append(item)

        if not combined_data:
            logging.warning(
                f"📁⠀ Tidak ada data untuk disimpan untuk target_code: {target_code}"
            )
            return

        filename = os.path.join(
            "results",
            f"{FileHandler._sanitize_filename(selected_title, target_code)}.xlsx",
        )
        logging.info(f"📁 Menyimpan file ke: {filename}")

        try:
            if os.path.exists(filename):
                wb = load_workbook(filename)
                for sheet_name in wb.sheetnames[:]:
                    sheet = wb[sheet_name]
                    if (
                        FileHandler._is_sheet_empty(sheet)
                        or sheet_name.lower() == "sheet"
                    ):
                        wb.remove(sheet)
            else:
                wb = Workbook()
                wb.remove(wb.active)

            all_sheet_name = "ALL_PROVIDER_RESULTS"
            if all_sheet_name not in wb.sheetnames:
                all_sheet = wb.create_sheet(all_sheet_name, 0)
                all_sheet.append(
                    [
                        "No",
                        "Title",
                        "Provider",
                        "Size",
                        "Status",
                        "Download URL",
                        "Bypass URL",
                        "_target_code",
                    ]
                )
            else:
                all_sheet = wb[all_sheet_name]

            existing_all_entries = set()
            for row in all_sheet.iter_rows(min_row=2, values_only=True):
                if row[1] and row[2] and row[7]:
                    existing_all_entries.add(
                        (
                            str(row[1]).lower().strip(),
                            str(row[2]).lower().strip(),
                            str(row[7]).lower().strip(),
                        )
                    )

            new_all_items = 0
            for item in combined_data:
                item_key = (
                    item.title.lower().strip(),
                    item.provider.lower().strip(),
                    item.target_code.lower().strip(),
                )
                if item_key not in existing_all_entries:
                    all_sheet.append(
                        [
                            all_sheet.max_row,
                            item.title,
                            item.provider,
                            item.size,
                            item.status,
                            item.download_url,
                            item.bypass_url,
                            item.target_code,
                        ]
                    )
                    existing_all_entries.add(item_key)
                    new_all_items += 1

            for idx, row in enumerate(all_sheet.iter_rows(min_row=2), 1):
                row[0].value = idx

            if FileHandler._is_sheet_empty(all_sheet):
                wb.remove(all_sheet)

            providers = {item.provider for item in combined_data}
            for provider in providers:
                provider_items = [
                    item for item in combined_data if item.provider == provider
                ]
                provider_new_items = False
                existing_provider_entries = set()
                provider_sheet_name = provider[:31]
                if provider_sheet_name in wb.sheetnames:
                    provider_sheet = wb[provider_sheet_name]
                    for row in provider_sheet.iter_rows(min_row=2, values_only=True):
                        if row[1] and row[2] and row[7]:
                            existing_provider_entries.add(
                                (
                                    str(row[1]).lower().strip(),
                                    str(row[2]).lower().strip(),
                                    str(row[7]).lower().strip(),
                                )
                            )

                for item in provider_items:
                    item_key = (
                        item.title.lower().strip(),
                        item.provider.lower().strip(),
                        item.target_code.lower().strip(),
                    )
                    if item_key not in existing_provider_entries:
                        provider_new_items = True
                        break

                if provider_new_items:
                    if provider_sheet_name not in wb.sheetnames:
                        provider_sheet = wb.create_sheet(provider_sheet_name)
                        provider_sheet.append(
                            [
                                "No",
                                "Title",
                                "Provider",
                                "Size",
                                "Status",
                                "Download URL",
                                "Bypass URL",
                                "_target_code",
                            ]
                        )
                    else:
                        provider_sheet = wb[provider_sheet_name]

                    for item in provider_items:
                        item_key = (
                            item.title.lower().strip(),
                            item.provider.lower().strip(),
                            item.target_code.lower().strip(),
                        )
                        if item_key not in existing_provider_entries:
                            provider_sheet.append(
                                [
                                    provider_sheet.max_row,
                                    item.title,
                                    item.provider,
                                    item.size,
                                    item.status,
                                    item.download_url,
                                    item.bypass_url,
                                    item.target_code,
                                ]
                            )
                            existing_provider_entries.add(item_key)

                    for idx, row in enumerate(provider_sheet.iter_rows(min_row=2), 1):
                        row[0].value = idx

                    if FileHandler._is_sheet_empty(provider_sheet):
                        wb.remove(provider_sheet)

            has_data = False
            for sheet_name in wb.sheetnames[:]:
                sheet = wb[sheet_name]
                if not FileHandler._is_sheet_empty(sheet):
                    has_data = True
                else:
                    wb.remove(sheet)

            if not has_data or not wb.sheetnames:
                logging.warning(f"📁⠀ Tidak ada data untuk disimpan ke {filename}")
                return

            if "Sheet" in wb.sheetnames:
                wb.remove(wb["Sheet"])

            for sheet in wb.sheetnames:
                ws = wb[sheet]
                column_widths = {
                    "A": 5,
                    "B": 60,
                    "C": 15,
                    "D": 10,
                    "E": 15,
                    "F": 60,
                    "G": 60,
                    "H": 15,
                }
                for col, width in column_widths.items():
                    ws.column_dimensions[col].width = width
                for row in ws.iter_rows():
                    for cell in row:
                        cell.alignment = Alignment(wrap_text=True, vertical="top")

            wb.save(filename)

        except Exception as e:
            logging.error(
                f"[ERROR] Gagal menyimpan file individual ke {filename}: {str(e)}"
            )

```

7. core/logger.py
```
"""
Modul untuk menangani logging aplikasi
"""

import os
import logging
import time
import sys
from datetime import datetime
from config import DEFAULT_CONFIG
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn


class BatchLogger:
    """
    Kelas untuk menangani logging batch dengan progress tracking
    """

    def __init__(
        self, total_items: int, actual_items: int, process_name: str = "PROCESS"
    ):
        self.total = total_items
        self.actual_items = actual_items
        self.process_name = process_name
        self.start_time = time.time()
        self.current = 0
        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
            transient=True,
        )
        self.task = None

    def log_progress(self, current: int):
        """
        Menampilkan progres real-time menggunakan rich progress bar
        """
        self.current = current
        if self.total == 0:
            return
        if self.task is None:
            self.progress.start()
            self.task = self.progress.add_task(
                f"[cyan]{self.process_name}[/cyan]", total=self.total
            )
        self.progress.update(self.task, completed=current)

    def log_complete(self, skipped_items: int = 0):
        """
        Mencatat penyelesaian proses ke konsol dan file log
        """
        total_time = int(time.time() - self.start_time)
        skipped_text = f" ({skipped_items} dilewati)" if skipped_items > 0 else ""
        if self.task is not None:
            self.progress.stop()
        logging.info(
            f"✅ Selesai: {self.actual_items} item dalam {total_time}s{skipped_text}"
        )


def setup_logging() -> str:
    """
    Setup logging configuration
    """
    log_config = DEFAULT_CONFIG.logging
    os.makedirs(log_config.log_dir, exist_ok=True)
    log_filename = datetime.now().strftime(f"{log_config.log_dir}/%Y-%m-%d.log")

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    file_formatter = logging.Formatter(
        fmt=log_config.format, datefmt=log_config.datefmt
    )

    console_formatter = logging.Formatter(fmt="%(message)s")

    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(log_config.level)
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_config.level)
    console_handler.setFormatter(console_formatter)

    logging.basicConfig(
        level=log_config.level,
        handlers=[file_handler, console_handler],
    )

    return log_filename

```
8. core/scraper.py
```
"""
Modul utama untuk scraping data dari FileCrypt
"""

import time
import logging
import re
from typing import List, Optional
from playwright.sync_api import Page
from models.data_models import ScrapedData
from core.database import DatabaseHandler
from config import DEFAULT_CONFIG
from .logger import BatchLogger


class FileCryptScraper:
    def __init__(self, page: Page):
        self.page = page
        self.timeouts = DEFAULT_CONFIG.timeouts
        self.providers = DEFAULT_CONFIG.providers
        self.pixeldrain = DEFAULT_CONFIG.pixeldrain
        self.user_agents = DEFAULT_CONFIG.user_agents
        self.scraper_config = DEFAULT_CONFIG.scraper
        self.database_handler = DatabaseHandler()
        self.container_title = "N/A"

    def detect_password(self) -> bool:
        try:
            return bool(self.page.query_selector("h2:has-text('Password required')"))
        except Exception as e:
            logging.error(f"[ERROR] Error deteksi password: {str(e)}")
            return False

    def handle_password(self) -> bool:
        if not self.detect_password():
            logging.info("🔓⠀URL tidak membutuhkan password")
            return True
        logging.info("🔐⠀Menunggu input password...")
        start_time = time.time()
        timeout = self.timeouts.password
        while self.detect_password():
            if time.time() - start_time > timeout:
                logging.error(f"[ERROR] Timeout password setelah {timeout} detik")
                return False
            time.sleep(self.timeouts.password_check)
        logging.info("🔓⠀Password berhasil ditangani")
        return True

    def detect_captcha(self) -> bool:
        try:
            return bool(self.page.query_selector("h2:has-text('Security prompt')"))
        except Exception as e:
            logging.error(f"[ERROR] Error deteksi captcha: {str(e)}")
            return False

    def handle_captcha(self) -> bool:
        if not self.detect_captcha():
            logging.info("🔓⠀CAPTCHA tidak terdeteksi")
            return True
        logging.info("🔐⠀Menunggu penyelesaian CAPTCHA...")
        start_time = time.time()
        timeout = self.timeouts.captcha
        while self.detect_captcha():
            if time.time() - start_time > timeout:
                logging.error(f"[ERROR] Timeout CAPTCHA setelah {timeout} detik")
                return False
            time.sleep(self.timeouts.captcha_check)
        logging.info("🔓⠀CAPTCHA berhasil diselesaikan")
        return True

    def get_available_providers(self) -> List[str]:
        try:
            self.page.wait_for_selector("tr.kwj3", timeout=self.timeouts.selector_wait)
            rows = self.page.query_selector_all("tr.kwj3")
            providers = set()
            for row in rows:
                provider_element = row.query_selector("td[title] a.external_link")
                if provider_element:
                    provider = provider_element.text_content().strip().lower()
                    if any(p in provider for p in self.providers.send_aliases):
                        provider = "send"
                    providers.add(provider.capitalize())
            return sorted(providers)
        except Exception as e:
            logging.error(f"[ERROR] Gagal mendapatkan provider: {str(e)}")
            return []

    def get_additional_info(self) -> tuple[str, str]:
        """
        Mengambil judul dan total ukuran dari halaman
        Mengembalikan (judul, total_size)
        """
        try:
            # Tunggu hingga elemen judul muncul
            self.page.wait_for_selector("h2", timeout=self.timeouts.selector_wait)
            title_element = self.page.query_selector("h2")
            title = title_element.text_content().strip() if title_element else "Unknown"
            self.container_title = (
                title
                if title and title.lower() not in ("n/a", "", "unknown")
                else "Unknown"
            )

            # Hitung total ukuran dari kolom ukuran di tabel
            total_size = 0.0
            size_unit = "GB"
            rows = self.page.query_selector_all("tr.kwj3")
            for row in rows:
                size_element = row.query_selector("td:nth-of-type(3)")
                if size_element:
                    size_text = size_element.text_content().strip()
                    match = re.match(
                        r"(\d+\.?\d*)\s*(GB|MB|KB)", size_text, re.IGNORECASE
                    )
                    if match:
                        size_value = float(match.group(1))
                        unit = match.group(2).upper()
                        if unit == "MB":
                            size_value /= 1024  # Konversi ke GB
                        elif unit == "KB":
                            size_value /= 1024 * 1024  # Konversi ke GB
                        total_size += size_value
            total_size = round(total_size, 2)
            total_size_str = f"{total_size} GB" if total_size > 0 else "N/A"

            return self.container_title, total_size_str
        except Exception as e:
            logging.debug(f"[MAIN] Gagal mengambil info tambahan: {str(e)}")
            self.container_title = "Unknown"
            return "Unknown", "N/A"

    def scrape_file_info(
        self,
        selected_provider: Optional[str] = None,
        all_providers: Optional[List[str]] = None,
    ) -> List[ScrapedData]:
        final_data = []
        try:
            self.page.wait_for_selector("tr.kwj3", timeout=self.timeouts.selector_wait)
            rows = self.page.query_selector_all("tr.kwj3")
            target_code = (
                self.page.url.split("/")[-1].replace(".html", "").strip()
                if self.page.url
                else "unknown"
            )
            total_rows = len(rows)
            process_logger = BatchLogger(
                total_items=total_rows * 2,
                actual_items=total_rows,
                process_name="SCRAPER",
            )
            all_items = []
            items_to_scrape = []
            skipped_items = 0
            progress_count = 0
            pixeldrain_bypass_index = 0  # Tambahkan indeks untuk round-robin

            # Fase 1: Proses baris
            for idx, row in enumerate(rows, 1):
                try:
                    provider_element = row.query_selector("td[title] a.external_link")
                    provider = (
                        provider_element.text_content().strip().lower()
                        if provider_element
                        else "N/A"
                    )
                    if any(p in provider for p in self.providers.send_aliases):
                        provider = "send"
                    provider = provider.capitalize()

                    if (
                        not selected_provider
                        or provider.lower() == selected_provider.lower()
                    ):
                        title = (
                            row.query_selector("td[title]").get_attribute("title")
                            if row.query_selector("td[title]")
                            else "N/A"
                        )

                        if self.database_handler.is_data_exists(
                            title, provider, target_code
                        ):
                            skipped_items += 1
                            existing_item = (
                                self.database_handler.get_data_by_title_provider(
                                    title, provider, target_code
                                )
                            )
                            if existing_item:
                                existing_item.container_title = self.container_title
                                all_items.append(existing_item)
                            continue

                        item = ScrapedData(
                            title=title,
                            provider=provider,
                            size=(
                                row.query_selector("td:nth-of-type(3)")
                                .text_content()
                                .strip()
                                if row.query_selector("td:nth-of-type(3)")
                                else "N/A"
                            ),
                            status=(
                                " ".join(
                                    row.query_selector("td.status i")
                                    .get_attribute("class")
                                    .split()
                                )
                                if row.query_selector("td.status i")
                                else "offline"
                            ),
                            download_url="N/A",
                            bypass_url="N/A",
                            target_code=target_code,
                            container_title=self.container_title,
                            download_button=row.query_selector("td button.download"),
                            row_element=row,
                        )
                        all_items.append(item)
                        items_to_scrape.append(item)

                    progress_count += 1
                    process_logger.log_progress(progress_count)
                except Exception as e:
                    logging.debug(f"[MAIN] Baris {idx} gagal: {str(e)}")
                    continue

            if not items_to_scrape:
                process_logger.log_complete(skipped_items)
                return all_items

            # Fase 2: Proses batch
            batch_size = self.scraper_config.max_batch_size
            total_batches = (len(items_to_scrape) + batch_size - 1) // batch_size
            for batch_start in range(0, len(items_to_scrape), batch_size):
                batch_end = min(batch_start + batch_size, len(items_to_scrape))
                current_batch = items_to_scrape[batch_start:batch_end]

                popups = []
                for item in current_batch:
                    try:
                        with self.page.expect_popup(
                            timeout=self.timeouts.popup
                        ) as popup_info:
                            if item.download_button:
                                item.download_button.click()
                            else:
                                logging.debug(
                                    f"[MAIN] Tidak ada tombol download untuk {item.title}"
                                )
                                item.download_url = "ERROR"
                                item.bypass_url = "ERROR"
                                continue
                        popups.append((item, popup_info.value))
                    except Exception as e:
                        logging.debug(
                            f"[MAIN] Gagal membuka popup untuk {item.title}: {str(e)}"
                        )
                        item.download_url = "ERROR"
                        item.bypass_url = "ERROR"

                for item, popup in popups:
                    try:
                        popup.wait_for_load_state(
                            "domcontentloaded", timeout=self.timeouts.page_load
                        )
                        item.download_url = popup.url

                        if "pixeldrain.com" in item.download_url.lower():
                            code = item.download_url.split("/")[-1]
                            # Gunakan URL bypass secara bergilir
                            selected_bypass = self.pixeldrain.bypass_urls[
                                pixeldrain_bypass_index
                                % len(self.pixeldrain.bypass_urls)
                            ]
                            item.bypass_url = selected_bypass.replace("CODE-FILE", code)
                            pixeldrain_bypass_index += 1  # Increment indeks

                        # Bersihkan atribut sementara segera setelah selesai digunakan
                        for attr in ["row_element", "download_button"]:
                            if hasattr(item, attr):
                                delattr(item, attr)

                        popup.close()
                    except Exception as e:
                        logging.debug(
                            f"[MAIN] Gagal memproses popup untuk {item.title}: {str(e)}"
                        )
                        item.download_url = "ERROR"
                        item.bypass_url = "ERROR"

                progress_count += len(current_batch)
                process_logger.log_progress(min(progress_count, total_rows * 2))
                time.sleep(self.timeouts.batch_delay)

            process_logger.log_complete(skipped_items)

            # Gabungkan data
            scraped_keys = {
                (item.title.lower().strip(), item.provider.lower().strip())
                for item in items_to_scrape
                if item.download_url != "ERROR"
            }

            for item in all_items:
                item_key = (item.title.lower().strip(), item.provider.lower().strip())
                if item_key in scraped_keys:
                    for scraped_item in items_to_scrape:
                        if (
                            scraped_item.title.lower().strip()
                            == item.title.lower().strip()
                            and scraped_item.provider.lower().strip()
                            == item.provider.lower().strip()
                            and scraped_item.download_url != "ERROR"
                        ):
                            scraped_item.container_title = self.container_title
                            final_data.append(scraped_item)
                            break
                else:
                    item.container_title = self.container_title
                    final_data.append(item)

            return final_data

        except Exception as e:
            logging.error(f"[ERROR] Gagal scrape di luar proses utama: {str(e)}")
            return final_data if final_data else []

```
9. core/sqlite_handler.py
```
import sqlite3
from typing import List, Optional, Dict, Any
from dataclasses import asdict
from models.data_models import ScrapedData
import logging
import os


class SQLiteHandler:
    def __init__(self, db_path: str = "results/filecrypt.db"):
        os.makedirs("results", exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database with proper schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Main table for all providers
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    size TEXT,
                    status TEXT,
                    download_url TEXT,
                    bypass_url TEXT,
                    target_code TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(title, provider, target_code)
                )
            """
            )

            # Index untuk pencarian cepat
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_files_target ON files(target_code)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_files_provider ON files(provider)"
            )

            conn.commit()

    def _get_connection(self):
        """Get a new database connection"""
        return sqlite3.connect(self.db_path)

    def save_data(self, data: List[ScrapedData]):
        """Save scraped data to SQLite"""
        if not data:
            return

        with self._get_connection() as conn:
            cursor = conn.cursor()

            for item in data:
                try:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO files (
                            title, provider, size, status,
                            download_url, bypass_url, target_code
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            item.title,
                            item.provider,
                            item.size,
                            item.status,
                            item.download_url,
                            item.bypass_url,
                            item.target_code,
                        ),
                    )
                except Exception as e:
                    logging.error(f"[SQLITE] Gagal menyimpan data: {str(e)}")
                    continue

            conn.commit()
            logging.info(f"[SQLITE] Disimpan {len(data)} item ke database")

    def get_all_data(self) -> List[Dict[str, Any]]:
        """Get all data from database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    title, provider, size, status,
                    download_url, bypass_url, target_code
                FROM files
                ORDER BY target_code, provider, title
            """
            )

            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def data_exists(self, title: str, provider: str, target_code: str) -> bool:
        """Check if data already exists"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 1 FROM files
                WHERE title = ? AND provider = ? AND target_code = ?
                LIMIT 1
            """,
                (title, provider, target_code),
            )
            return cursor.fetchone() is not None

```
10.  core/utils.py
```
"""
Modul untuk utility functions
"""

import re
import random
from typing import List, Dict
from config import DEFAULT_CONFIG


def clean_filename(title: str) -> str:
    """
    Membersihkan judul untuk dijadikan nama file

    Args:
        title (str): Judul yang akan dibersihkan

    Returns:
        str: Judul yang sudah dibersihkan
    """
    if not isinstance(title, str):
        return "unknown"
    title = re.sub(r'[\\/*?:"<>|]', "", title.strip())
    return title[:50]


def get_random_ua() -> str:
    """
    Mendapatkan random user agent dari config

    Returns:
        str: Random user agent string
    """
    return random.choice(DEFAULT_CONFIG.user_agents)


def normalize_series_title(title: str) -> str:
    """
    Normalisasi judul series untuk konsistensi penamaan file
    Contoh:
    Input: "LTNS.S01E01.1080p.WEB.x264"
    Output: "LTNS.S01"
    """
    patterns = [
        r"(.*?\.S\d{2})",  # Format S01
        r"(.*?\.Season.\d+)",  # Format Season 1
        r"(.*?\s\d{4})",  # Format 2023
    ]

    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            base = match.group(1)
            # Standarisasi format
            base = re.sub(r"\.Season.(\d+)", lambda m: f".S{m.group(1).zfill(2)}", base)
            return base

    return "Various"

```
11. models/data_models.py
```
"""
Model data untuk aplikasi FileCrypt Scraper
"""

from dataclasses import dataclass
from typing import Optional, Any, List, Dict


@dataclass
class ScrapedData:
    """
    Data yang di-scrape dari FileCrypt
    """

    title: str
    provider: str
    size: str
    status: str
    download_url: str
    bypass_url: str
    target_code: str
    container_title: str = "N/A"
    download_button: Optional[Any] = None
    row_element: Optional[Any] = None


@dataclass
class BatchLoggerConfig:
    """
    Konfigurasi untuk BatchLogger
    """

    total_items: int
    process_name: str = "PROCESS"
    update_interval: int = 5

```

12. main.py
```
"""
Program utama FileCrypt Scraper
"""

import os
import sys
import logging
import time
from tabulate import tabulate
import tkinter as tk
from tkinter import filedialog
import sqlite3
import re
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from core.browser import BrowserManager
from core.scraper import FileCryptScraper
from core.database import DatabaseHandler
from core.file_handler import FileHandler
from core.logger import setup_logging
from config import DEFAULT_CONFIG

# Inisialisasi rich console
console = Console()


def select_input_method() -> str:
    """Meminta pengguna memilih metode input URL atau cek database"""
    content = (
        "1. Masukkan satu URL langsung\n"
        "2. Pilih file berisi daftar URL (.txt)\n"
        "3. Cek database"
    )
    console.print(
        Panel(
            content,
            title="[bold blue]PILIH METODE[/bold blue]",
            border_style="cyan",
            expand=True,
        )
    )

    while True:
        try:
            choice = console.input("Masukkan nomor opsi (1-3): ").strip()
            if choice in ["1", "2", "3"]:
                return choice
            console.print(
                "⚠️ [yellow]Opsi tidak valid! Harap masukkan nomor 1, 2, atau 3.[/yellow]"
            )
        except Exception as e:
            logging.error(f"[ERROR] Error memilih metode input: {str(e)}")
            console.print(
                f"❌ [red]Terjadi error! Harap masukkan nomor 1, 2, atau 3.[/red]"
            )
        time.sleep(1)


def get_valid_url() -> str:
    """Meminta satu URL valid dari pengguna"""
    while True:
        try:
            url = console.input("Masukkan URL: ").strip()
            if url.startswith("https://www.filecrypt.cc/Container/") and url.endswith(
                ".html"
            ):
                return url
            console.print(
                "⚠️ [yellow]URL tidak valid! Harap masukkan URL FileCrypt yang benar.[/yellow]"
            )
        except Exception as e:
            logging.error(f"❌⠀ Error memasukkan URL: {str(e)}")
            console.print(
                f"❌⠀ [red]Terjadi error! Harap masukkan URL yang valid.[/red]"
            )
        time.sleep(1)


def get_urls_from_file() -> List[str]:
    """Membuka file explorer dan membaca URL dari file .txt"""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Pilih file .txt berisi URL", filetypes=[("Text files", "*.txt")]
    )
    root.destroy()

    if not file_path:
        logging.error("❌⠀ Tidak ada file yang dipilih")
        console.print("❌⠀ [red]Tidak ada file yang dipilih. Program berhenti.[/red]")
        sys.exit(1)

    valid_urls = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                url = line.strip()
                if url.startswith(
                    "https://www.filecrypt.cc/Container/"
                ) and url.endswith(".html"):
                    valid_urls.append(url)
                else:
                    logging.warning(f"[WARNING] URL tidak valid di file: {url}")
        if not valid_urls:
            logging.error("❌⠀ Tidak ada URL valid di file")
            console.print(
                "❌⠀ [red]Tidak ada URL valid di file. Program berhenti.[/red]"
            )
            sys.exit(1)
        return valid_urls
    except Exception as e:
        logging.error(f"❌⠀ Gagal membaca file: {str(e)}")
        console.print(f"❌⠀ [red]Terjadi error saat membaca file: {str(e)}[/red]")
        sys.exit(1)


def select_output_option() -> str:
    """Meminta pengguna memilih opsi pencetakan output"""
    console.print(
        Panel(
            "\n1. Cetak semua data di database \n2. Cetak file individual saja \n3. Cetak keduanya \n4. Simpan data ke database ",
            title="[bold blue]PILIH OPSI FILE OUTPUT[/bold blue]",
            border_style="cyan",
            expand=True,
        )
    )

    while True:
        try:
            choice = console.input("Masukkan nomor opsi (1-4): ").strip()
            if choice in ["1", "2", "3", "4"]:
                return choice
            console.print(
                "⚠️ [yellow]Opsi tidak valid! Harap masukkan nomor 1, 2, 3, atau 4.[/yellow]"
            )
        except Exception as e:
            logging.error(f"❌⠀ Error memilih opsi pencetakan: {str(e)}")
            console.print(
                f"❌⠀ [red]Terjadi error! Harap masukkan nomor 1, 2, 3, atau 4.[/red]"
            )
        time.sleep(1)


def process_single_url(url: str) -> tuple[List, str]:
    """Memproses scraping untuk satu URL, mengembalikan scraped_data dan container_title"""
    target_code = url.split("/")[-1].replace(".html", "")
    logging.info(f"⚙⠀ Memulai proses untuk target_code: {target_code}")

    with BrowserManager() as browser_manager:
        scraper = None
        try:
            for attempt in range(3):
                try:
                    scraper = FileCryptScraper(browser_manager.context.new_page())
                    break
                except Exception as e:
                    logging.warning(
                        f"[WARNING] Gagal membuka halaman baru, mencoba lagi ({attempt + 1}/3): {str(e)}"
                    )
                    time.sleep(2)
            else:
                raise RuntimeError("Gagal membuka halaman baru setelah 3 percobaan")

            for attempt in range(3):
                try:
                    scraper.page.goto(url, wait_until="load", timeout=15000)
                    break
                except Exception as e:
                    logging.warning(
                        f"[WARNING] Gagal memuat URL, mencoba lagi ({attempt + 1}/3): {str(e)}"
                    )
                    time.sleep(2)
            else:
                raise RuntimeError("Gagal memuat URL setelah 3 percobaan")

            browser_manager.close_about_blank_tabs()
            time.sleep(1)

            if not scraper.handle_password():
                raise RuntimeError("Gagal menangani password")
            if not scraper.handle_captcha():
                raise RuntimeError("Gagal menangani CAPTCHA")

            title, total_size = scraper.get_additional_info()
            container_title = (
                title
                if title and title.strip().lower() not in ("n/a", "unknown", "")
                else target_code
            )

            online_count = sum(
                1
                for row in scraper.page.query_selector_all("tr.kwj3")
                if row.query_selector("td.status i")
                and "online" in row.query_selector("td.status i").get_attribute("class")
            )
            total_count = len(scraper.page.query_selector_all("tr.kwj3"))
            print_info(
                {
                    "Judul": title,
                    "Status URL": f"{online_count}/{total_count} Online",
                    "Total Size": total_size,
                    "Target Code": target_code,
                }
            )

            providers = scraper.get_available_providers()
            selected_provider = select_provider(providers)

            logging.info(f"⚙⠀ Memulai proses scraping untuk target_code: {target_code}")
            logging.info(f"⚙⠀ Total item di halaman: {total_count}")
            scraped_data = scraper.scrape_file_info(
                selected_provider=selected_provider,
                all_providers=providers if not selected_provider else None,
            )
            return scraped_data, container_title
        except Exception as e:
            logging.error(f"❌⠀ Gagal memproses URL {url}: {str(e)}")
            return [], target_code
        finally:
            if scraper and scraper.page:
                try:
                    scraper.page.close()
                except Exception as e:
                    logging.warning(f"[WARNING] Gagal menutup halaman: {str(e)}")
            try:
                for page in browser_manager.context.pages:
                    if not page.is_closed():
                        page.close()
            except Exception as e:
                logging.warning(f"[WARNING] Gagal menutup halaman sisa: {str(e)}")


def connect_db(db_name: str) -> Optional[sqlite3.Connection]:
    """Fungsi untuk koneksi ke database"""
    try:
        conn = sqlite3.connect(db_name)
        return conn
    except sqlite3.Error as e:
        console.print(f"❌⠀ [red]Error koneksi database: {e}[/red]")
        logging.error(f"❌⠀ Error koneksi database: {str(e)}")
        return None


def modify_title(title: str) -> str:
    """Fungsi untuk memodifikasi title sesuai pola yang diinginkan"""
    if not title:
        return title

    patterns_to_remove = [
        r"\[MkvDrama\.Org\]",
        r"\[MkvDrama\.me\]",
        r"\.mkv\b",
        r"\.x264\b",
        r"\.1080p\b",
        r"\.720p\b",
        r"\b.E01\b",
    ]
    cleaned_title = title
    for pattern in patterns_to_remove:
        cleaned_title = re.sub(pattern, "", cleaned_title, flags=re.IGNORECASE)

    match = re.match(r"^(.*?S01)(?:E\d{2})?\.?([A-Z]+)?", cleaned_title.strip())
    if match:
        base_title = match.group(1)
        provider = match.group(2) or ""
        return f"{base_title}{'.' + provider if provider else ''}"

    return cleaned_title.strip()


def sanitize_filename(filename: str) -> str:
    """Mengganti karakter tidak valid untuk nama file, tapi pertahankan titik"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "")
    return filename


def is_sheet_empty(sheet: openpyxl.worksheet.worksheet.Worksheet) -> bool:
    return sheet.max_row <= 1


def save_to_excel(data: List[tuple], filename: str):
    """Fungsi untuk menyimpan data ke file Excel dengan struktur seperti save_individual_files"""
    try:
        os.makedirs("results", exist_ok=True)
        filename = os.path.join("results", f"{sanitize_filename(filename)}.xlsx")

        if os.path.exists(filename):
            wb = openpyxl.load_workbook(filename)
            for sheet_name in wb.sheetnames[:]:
                sheet = wb[sheet_name]
                if is_sheet_empty(sheet) or sheet_name.lower() == "sheet":
                    wb.remove(sheet)
        else:
            wb = openpyxl.Workbook()
            wb.remove(wb.active)

        all_sheet_name = "ALL_PROVIDER_RESULTS"
        if all_sheet_name not in wb.sheetnames:
            all_sheet = wb.create_sheet(all_sheet_name, 0)
            all_sheet.append(
                [
                    "No",
                    "Title",
                    "Provider",
                    "Size",
                    "Status",
                    "Download URL",
                    "Bypass URL",
                    "_target_code",
                ]
            )
        else:
            all_sheet = wb[all_sheet_name]

        existing_all_entries = set()
        for row in all_sheet.iter_rows(min_row=2, values_only=True):
            if row[1] and row[2] and row[7]:
                existing_all_entries.add(
                    (
                        str(row[1]).lower().strip(),
                        str(row[2]).lower().strip(),
                        str(row[7]).lower().strip(),
                    )
                )

        new_all_items = 0
        for item in data:
            item_key = (
                str(item[0]).lower().strip(),
                str(item[1]).lower().strip(),
                str(item[6]).lower().strip(),
            )
            if item_key not in existing_all_entries:
                all_sheet.append(
                    [
                        all_sheet.max_row,
                        item[0],
                        item[1],
                        item[2],
                        item[3],
                        item[4],
                        item[5],
                        item[6],
                    ]
                )
                existing_all_entries.add(item_key)
                new_all_items += 1

        for idx, row in enumerate(all_sheet.iter_rows(min_row=2), 1):
            row[0].value = idx

        if is_sheet_empty(all_sheet):
            wb.remove(all_sheet)

        providers = {item[1] for item in data if item[1]}
        for provider in providers:
            provider_items = [item for item in data if item[1] == provider]
            provider_sheet_name = provider[:31]
            existing_provider_entries = set()

            if provider_sheet_name in wb.sheetnames:
                provider_sheet = wb[provider_sheet_name]
                for row in provider_sheet.iter_rows(min_row=2, values_only=True):
                    if row[1] and row[2] and row[7]:
                        existing_provider_entries.add(
                            (
                                str(row[1]).lower().strip(),
                                str(row[2]).lower().strip(),
                                str(row[7]).lower().strip(),
                            )
                        )

            provider_new_items = False
            for item in provider_items:
                item_key = (
                    str(item[0]).lower().strip(),
                    str(item[1]).lower().strip(),
                    str(item[6]).lower().strip(),
                )
                if item_key not in existing_provider_entries:
                    provider_new_items = True
                    break

            if provider_new_items:
                if provider_sheet_name not in wb.sheetnames:
                    provider_sheet = wb.create_sheet(provider_sheet_name)
                    provider_sheet.append(
                        [
                            "No",
                            "Title",
                            "Provider",
                            "Size",
                            "Status",
                            "Download URL",
                            "Bypass URL",
                            "_target_code",
                        ]
                    )
                else:
                    provider_sheet = wb[provider_sheet_name]

                for item in provider_items:
                    item_key = (
                        str(item[0]).lower().strip(),
                        str(item[1]).lower().strip(),
                        str(item[6]).lower().strip(),
                    )
                    if item_key not in existing_provider_entries:
                        provider_sheet.append(
                            [
                                provider_sheet.max_row,
                                item[0],
                                item[1],
                                item[2],
                                item[3],
                                item[4],
                                item[5],
                                item[6],
                            ]
                        )
                        existing_provider_entries.add(item_key)

                for idx, row in enumerate(provider_sheet.iter_rows(min_row=2), 1):
                    row[0].value = idx

                if is_sheet_empty(provider_sheet):
                    wb.remove(provider_sheet)

        has_data = False
        for sheet_name in wb.sheetnames[:]:
            sheet = wb[sheet_name]
            if not is_sheet_empty(sheet):
                has_data = True
            else:
                wb.remove(sheet)

        if not has_data or not wb.sheetnames:
            console.print("⚠️ [yellow]Tidak ada data untuk disimpan.[/yellow]")
            logging.info("[EXCEL] Tidak ada data untuk disimpan ke Excel")
            return

        if "Sheet" in wb.sheetnames:
            wb.remove(wb["Sheet"])

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            column_widths = {
                "A": 5,
                "B": 60,
                "C": 15,
                "D": 10,
                "E": 15,
                "F": 60,
                "G": 60,
                "H": 15,
            }
            for col, width in column_widths.items():
                ws.column_dimensions[col].width = width
            for row in ws.iter_rows():
                for cell in row:
                    cell.alignment = Alignment(wrap_text=True, vertical="top")

        wb.save(filename)
        console.print(f"✅ [white]Data disimpan ke {filename}[/white]")
        logging.info(f"[EXCEL] Data disimpan ke {filename}")

    except Exception as e:
        console.print(f"❌⠀ [red]Error menyimpan ke Excel: {e}[/red]")
        logging.error(f"❌⠀ Gagal menyimpan ke Excel: {str(e)}")


def save_all_data():
    """Fungsi untuk menyimpan semua data dari database ke RESULT_DATABASE.xlsx"""
    conn = connect_db("results/scraped_data.db")
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT title, provider, size, status, download_url, bypass_url, target_code
                FROM scraped_data
            """
            )
            rows = cursor.fetchall()

            if rows:
                save_to_excel(rows, "RESULT_DATABASE")
            else:
                console.print("⚠️ [yellow]Tidak ada data di database[/yellow]")
                logging.info("📥 Tidak ada data di database")

        except sqlite3.Error as e:
            console.print(f"❌⠀ [red]Error membaca data: {e}[/red]")
            logging.error(f"❌⠀ Error membaca data: {str(e)}")
        finally:
            conn.close()


def display_and_save_by_target_code(target_code: str, modified_title: str):
    """Fungsi untuk menyimpan data dengan target_code tertentu ke Excel"""
    conn = connect_db("results/scraped_data.db")
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT title, provider, size, status, download_url, bypass_url, target_code
                FROM scraped_data
                WHERE target_code = ?
            """,
                (target_code,),
            )
            rows = cursor.fetchall()

            if rows:
                save_to_excel(rows, modified_title)
            else:
                console.print(
                    f"⚠️ [yellow]Tidak ada data dengan target_code: {target_code}[/yellow]"
                )
                logging.info(f"📥 Tidak ada data dengan target_code: {target_code}")

        except sqlite3.Error as e:
            console.print(f"❌⠀ [red]Error membaca data: {e}[/red]")
            logging.error(f"❌⠀ Error membaca data: {str(e)}")
        finally:
            conn.close()


def display_data():
    """Fungsi untuk menampilkan daftar data dalam tabel dan memilih target_code atau semua data"""
    db_name = "results/scraped_data.db"
    conn = connect_db(db_name)

    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT MIN(title), target_code
                FROM scraped_data
                GROUP BY target_code
                """
            )
            rows = cursor.fetchall()

            if not rows:
                console.print("⚠️ [yellow]Tidak ada data di database.[/yellow]")
                logging.info("📥 Tidak ada data di database")
                return

            table = Table(
                title=Text(f"Data dari {db_name}", style="bold blue"),
                show_header=True,
                header_style="bold cyan",
            )
            table.add_column("No", style="cyan", justify="center")
            table.add_column("Title", style="green")
            table.add_column("Target Code", style="magenta")

            selections = []
            for idx, row in enumerate(rows, 1):
                title, target_code = row
                modified_title = modify_title(title)
                table.add_row(str(idx), modified_title, target_code)
                selections.append((modified_title, target_code))

            console.print(table)
            console.print("\n0. Simpan semua data ke RESULT_DATABASE.xlsx")
            console.print("m. Kembali ke menu utama")

            try:
                choice = console.input("\nMasukkan nomor untuk cetak data: ").strip()
                if choice == "0":
                    save_all_data()
                elif choice == "m":
                    logging.debug("Pengguna memilih kembali ke menu utama")
                    main()
                else:
                    choice = int(choice)
                    if 1 <= choice <= len(selections):
                        selected_title, selected_target_code = selections[choice - 1]
                        display_and_save_by_target_code(
                            selected_target_code, selected_title
                        )
                    else:
                        console.print("⚠️ [yellow]Pilihan tidak valid![/yellow]")
                        logging.warning("[INPUT] Pilihan tidak valid")
            except ValueError:
                console.print("⚠️ [yellow]Masukkan angka yang valid![/yellow]")
                logging.warning("[INPUT] Input bukan angka")

        except sqlite3.Error as e:
            console.print(f"❌⠀ [red]Error membaca data: {e}[/red]")
            logging.error(f"❌⠀ Error membaca data: {str(e)}")
        finally:
            conn.close()


def main():
    """Fungsi utama untuk menjalankan scraper"""
    log_file = setup_logging()
    DatabaseHandler._init_db()

    try:
        input_method = select_input_method()
        urls = []

        if input_method == "1":
            urls = [get_valid_url()]
        elif input_method == "2":
            urls = get_urls_from_file()
        elif input_method == "3":
            display_data()
            return

        processed_target_codes = []
        container_titles = {}
        for idx, url in enumerate(urls, 1):
            logging.debug(f"⚙⠀ Memproses URL {idx}/{len(urls)}: {url}")
            console.print(f"🚀 [white]Memproses URL {idx}/{len(urls)}: {url}[/white]")
            scraped_data, container_title = process_single_url(url)

            if scraped_data:
                new_items = DatabaseHandler.save_to_sqlite(scraped_data)
                console.print(
                    f"✅ [white]Berhasil menyimpan {new_items} item baru[/white]"
                )
                if new_items == 0:
                    console.print("⚠️ [yellow]Tidak ada item baru[/yellow]")
                    logging.debug(f"⚙⠀ Tidak ada item baru")
                target_code = url.split("/")[-1].replace(".html", "")
                processed_target_codes.append(target_code)
                container_titles[target_code] = container_title
            else:
                console.print("⚠️ [yellow]Tidak ada data yang di-scrape[/yellow]")
                logging.info(f"⚙⠀ Tidak ada data yang di-scrape")
                console.print(
                    f"⚠️ [yellow]Tidak ada data yang berhasil di-scrape[/yellow]"
                )

            time.sleep(3)

        if urls:
            if processed_target_codes:
                output_option = select_output_option()
                if output_option == "1":
                    all_data = DatabaseHandler.get_all_data()
                    if all_data:
                        DatabaseHandler.export_to_excel(
                            all_data, processed_target_codes[0]
                        )
                        console.print(
                            f"✅ [white]Berhasil menyimpan file database di results\\RESULT_DATABASE.xlsx[/white]"
                        )
                        logging.debug(
                            f"📁⠀Berhasil menyimpan file database di results\\RESULT_DATABASE.xlsx"
                        )
                    else:
                        console.print("⚠️ [yellow]Tidak ada data di database[/yellow]")
                        logging.info("📁⠀Tidak ada data di database")
                elif output_option == "2":
                    for target_code in processed_target_codes:
                        scraped_data = DatabaseHandler.get_data_by_target_code(
                            target_code
                        )
                        if scraped_data:
                            container_title = container_titles.get(
                                target_code, target_code
                            )
                            FileHandler.save_individual_files(
                                scraped_data, target_code, container_title
                            )
                            console.print(
                                f"✅ [white]Berhasil menyimpan file individual di results\\{FileHandler._sanitize_filename(container_title, target_code)}.xlsx[/white]"
                            )
                            logging.debug(
                                f"📁⠀Berhasil menyimpan file individual di results\\{FileHandler._sanitize_filename(container_title, target_code)}.xlsx"
                            )
                elif output_option == "3":
                    all_data = DatabaseHandler.get_all_data()
                    if all_data:
                        DatabaseHandler.export_to_excel(
                            all_data, processed_target_codes[0]
                        )
                        console.print(
                            f"✅ [white]Berhasil menyimpan file database di results\\RESULT_DATABASE.xlsx[/white]"
                        )
                        logging.debug(
                            f"📁⠀Berhasil menyimpan file database di results\\RESULT_DATABASE.xlsx"
                        )
                    for target_code in processed_target_codes:
                        scraped_data = DatabaseHandler.get_data_by_target_code(
                            target_code
                        )
                        if scraped_data:
                            container_title = container_titles.get(
                                target_code, target_code
                            )
                            FileHandler.save_individual_files(
                                scraped_data, target_code, container_title
                            )
                            console.print(
                                f"✅ [white]Berhasil menyimpan file individual di results\\{FileHandler._sanitize_filename(container_title, target_code)}.xlsx[/white]"
                            )
                            logging.debug(
                                f"📁⠀Berhasil menyimpan file individual di results\\{FileHandler._sanitize_filename(container_title, target_code)}.xlsx"
                            )
                elif output_option == "4":
                    console.print(
                        "✅ [white]Data berhasil tersimpan di DATABASE[/white]"
                    )
                    logging.debug("⚙⠀ Data berhasil tersimpan di DATABASE")
            else:
                console.print(
                    "⚠️ [yellow]Tidak ada data yang berhasil di-scrape dari URL manapun[/yellow]"
                )
                logging.debug(
                    "⚙⠀ Tidak ada data yang berhasil di-scrape dari URL manapun"
                )
                console.print(
                    "⚠️ [yellow]Tidak ada data yang berhasil di-scrape dari URL manapun.[/yellow]"
                )

        console.print(
            "🎉 [white]Scraping selesai. Output telah diproses. Program selesai.[/white]"
        )
        logging.debug("⚙⠀ Scraping selesai. Output telah diproses. Program selesai.")

    except Exception as e:
        console.print(f"❌⠀ [red]Terjadi kesalahan: {str(e)}[/red]")
        logging.error(f"❌⠀ Terjadi kesalahan: {str(e)}")
        sys.exit(1)


def print_info(info: Dict[str, str]):
    """Menampilkan informasi URL dengan rich"""
    content = "\n".join(
        f"[cyan]{key:<15}[/cyan] : [white]{value}[/white]"
        for key, value in info.items()
    )
    console.print(
        Panel(
            content,
            title="[bold blue]INFORMASI URL[/bold blue]",
            border_style="cyan",
            expand=True,
        )
    )


def select_provider(providers: List[str]) -> Optional[str]:
    if not providers:
        console.print("⚠️ [yellow]Tidak ada provider yang tersedia.[/yellow]")
        return None

    content = "\n".join(
        f"[white]{i}. {provider}[/white]" for i, provider in enumerate(providers, 1)
    )
    console.print(
        Panel(
            content,
            title="[bold blue]PROVIDER YANG TERSEDIA[/bold blue]",
            border_style="cyan",
            expand=True,
        )
    )

    try:
        provider_input = console.input(
            "Masukkan nomor provider (0 untuk semua): "
        ).strip()
        if provider_input == "0":
            return None
        elif provider_input.isdigit():
            provider_num = int(provider_input)
            if 1 <= provider_num <= len(providers):
                return providers[provider_num - 1]
        console.print(
            "⚠️ [yellow]Nomor tidak valid! Akan mengambil semua provider.[/yellow]"
        )
        time.sleep(2)
        return None
    except Exception as e:
        console.print(f"❌⠀ [red]Error memilih provider: {str(e)}[/red]")
        logging.error(f"❌⠀ Error memilih provider: {str(e)}")
        console.print(
            "⚠️ [yellow]Terjadi error! Akan mengambil semua provider.[/yellow]"
        )
        time.sleep(2)
        return None


if __name__ == "__main__":
    try:
        for ext in DEFAULT_CONFIG.extensions.paths:
            if not os.path.exists(os.path.join(ext, "manifest.json")):
                raise FileNotFoundError(f"❌⠀ Ekstensi tidak valid di: {ext}")

        console.print(
            Panel(
                Text("FILECRYPT SCRAPER", style="bold blue", justify="center"),
                title="",
                border_style="cyan",
                expand=True,
            )
        )

        main()
        console.print(
            Panel(
                Text("FILECRYPT SELESAI", style="bold green", justify="center"),
                title="",
                border_style="cyan",
                expand=True,
            )
        )
    except Exception as e:
        console.print(f"❌⠀ [red]Error: {str(e)}[/red]")
        logging.error(f"❌⠀ Error: {str(e)}")
        sys.exit(1)

```


## Perintah
Sebagai seorang developer python profesional dan berpengalaman, lakukan breakdown dan analisa terhadap project tersebut. Berikan saran perbaikan dan pengembangan agar project memiliki penulisan kode yang rapi, simple dan tetap terstruktur agar dapat mempermudah untuk dilakukan pengelolaan dan pengembangan kedepannya. Pastikan tidak terjadi pengulangan/redundan terkait penulisan kode.


---
Sebelum melanjutkan perubahan ke "memusatkan logika Excel ke file_handler.py" saya ingin melakukan perubahan logika/alur jalannya program. Alur yang saya inginkan adalah sebagai berikut:
1. Alur sebelumnya adalah kurang lebih sebagai berikut:
   + program dijalankan
   + program mencoba membuka url yang diberikan
   + membuka browser secara gui(headless=False) secara langsung
   + mengakses url
   + melakukan cek terhadap password dan captcha
   + melakukan scraping info dasar
2. Alur yang saya inginkan adalah sebagai berikut:
   + program dijalankan
   + program mencoba membuka url yang diberikan
   + membuka browser secara headless
   + mengakses url
   + melakukan cek terhadap password dan captcha
   + jika password dan captcha ada
     + tutup browser headless
     + buka kembali url yang diberikan dengan browser secara gui (headless=false)
   + jika password dan captcha tidak ada
     + lanjutkan program sesuai dengan alur yang sudah ada

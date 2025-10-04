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
    valid_urls: List[str] = []


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

"""
Modul untuk mengelola konfigurasi dari file .env

Modul ini menangani:
1. Memuat variabel lingkungan dari file .env
2. Menyediakan fungsi helper untuk parsing nilai
3. Mengekspor konfigurasi dalam format yang konsisten
"""

import os
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _parse_list(value: str, separator: str = ",") -> List[str]:
    """Parse a comma-separated string into a list."""
    if not value:
        return []
    return [item.strip() for item in value.split(separator)]


def _parse_bool(value: str) -> bool:
    """Parse a string to boolean."""
    return value.lower() in ("true", "1", "yes", "y", "t")


def _parse_int(value: str, default: int = 0) -> int:
    """Parse a string to integer with default value."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def get_config() -> Dict[str, Any]:
    """
    Mendapatkan konfigurasi dari variabel lingkungan.

    Returns:
        Dict[str, Any]: Konfigurasi aplikasi dalam bentuk dictionary
    """
    config = {
        "browser": {
            "user_data_dir": os.getenv("BROWSER_USER_DATA_DIR", "./profile"),
            "headless": _parse_bool(os.getenv("BROWSER_HEADLESS", "False")),
            "args": _parse_list(
                os.getenv(
                    "BROWSER_ARGS",
                    "--disable-component-update,--no-sandbox,--disable-dev-shm-usage,--disable-webgl,--disable-blink-features=AutomationControlled,--disable-infobars",
                )
            ),
            "ignore_default_args": _parse_list(
                os.getenv("BROWSER_IGNORE_DEFAULT_ARGS", "--enable-automation,--disable-extensions")
            ),
        },
        "extensions": {
            "paths": _parse_list(
                os.getenv(
                    "EXTENSIONS_PATHS",
                    ""
                )
            ),
        },
        "logging": {
            "log_dir": os.getenv("LOG_DIR", "logs"),
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "format": os.getenv("LOG_FORMAT", "%(asctime)s - %(levelname)-4s - %(message)s"),
            "datefmt": os.getenv("LOG_DATEFMT", "%Y-%m-%d %H:%M:%S"),
        },
        "timeouts": {
            "selector_wait": _parse_int(os.getenv("TIMEOUT_SELECTOR_WAIT", "10000")),
            "popup": _parse_int(os.getenv("TIMEOUT_POPUP", "5000")),
            "page_load": _parse_int(os.getenv("TIMEOUT_PAGE_LOAD", "30000")),
            "password_check": _parse_int(os.getenv("TIMEOUT_PASSWORD_CHECK", "5")),
            "captcha_check": _parse_int(os.getenv("TIMEOUT_CAPTCHA_CHECK", "5")),
            "batch_delay": _parse_int(os.getenv("TIMEOUT_BATCH_DELAY", "1")),
            "captcha": _parse_int(os.getenv("TIMEOUT_CAPTCHA", "300")),
            "password": _parse_int(os.getenv("TIMEOUT_PASSWORD", "300")),
        },
        "providers": {
            "send_aliases": _parse_list(
                os.getenv(
                    "SEND_ALIASES",
                    "send.cm,sendit.cloud,send.co,send.now,send.com,send.cw",
                )
            ),
        },
        "pixeldrain": {
            "bypass_urls": _parse_list(
                os.getenv(
                    "PIXELDRAIN_BYPASS_URLS",
                    "https://cdn.pd1.workers.dev/api/file/CODE-FILE,https://cdn.pd7.workers.dev/api/file/CODE-FILE,https://cdn.pd8.workers.dev/api/file/CODE-FILE,https://cdn.pd10.workers.dev/api/file/CODE-FILE",
                )
            ),
        },
        "user_agents": _parse_list(
            os.getenv(
                "USER_AGENTS",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36,Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
            )
        ),
        "scraper": {
            "batch_processing": _parse_bool(os.getenv("SCRAPER_BATCH_PROCESSING", "True")),
            "max_batch_size": _parse_int(os.getenv("SCRAPER_MAX_BATCH_SIZE", "8")),
        },
    }

    # Validasi konfigurasi penting
    _validate_config(config)

    return config


def _validate_config(config: Dict[str, Any]) -> None:
    """
    Memvalidasi konfigurasi penting dan memberikan peringatan jika ada masalah.

    Args:
        config (Dict[str, Any]): Konfigurasi yang akan divalidasi
    """
    # Validasi path ekstensi
    if not config["extensions"]["paths"]:
        logging.warning(
            "PERINGATAN: EXTENSIONS_PATHS tidak dikonfigurasi di .env. "
            "Adblock mungkin tidak akan berfungsi."
        )

    # Validasi user agents
    if not config["user_agents"]:
        logging.warning(
            "PERINGATAN: USER_AGENTS tidak dikonfigurasi di .env. "
            "Menggunakan user agent default."
        )


# Ekspor konfigurasi sebagai DEFAULT_CONFIG untuk kompatibilitas dengan kode yang ada
DEFAULT_CONFIG = get_config()


def get_env_value(key: str, default: Optional[str] = None) -> str:
    """
    Mendapatkan nilai dari variabel lingkungan.

    Args:
        key (str): Nama variabel lingkungan
        default (Optional[str]): Nilai default jika variabel tidak ditemukan

    Returns:
        str: Nilai variabel lingkungan atau default
    """
    return os.getenv(key, default)


if __name__ == "__main__":
    # Untuk debugging
    import json
    print(json.dumps(DEFAULT_CONFIG, indent=2))

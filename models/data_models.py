"""
Model data untuk aplikasi FileCrypt Scraper
"""

from dataclasses import dataclass
from typing import Optional, Any, List, Dict


@dataclass
class BrowserConfig:
    """
    Konfigurasi untuk browser
    """

    user_data_dir: str
    headless: bool
    args: List[str]
    ignore_default_args: List[str]


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


@dataclass
class ScraperConfig:
    batch_processing: bool = True
    max_batch_size: int = 10  # Batas maksimal batch

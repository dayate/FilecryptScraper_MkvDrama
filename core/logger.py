"""
Modul untuk menangani logging aplikasi
"""

import os
import logging
import time
import sys
from datetime import datetime
from config.constants import DEFAULT_CONFIG


class BatchLogger:
    """
    Kelas untuk menangani logging batch dengan progress tracking
    """

    def __init__(
        self, total_items: int, actual_items: int, process_name: str = "PROCESS"
    ):
        """
        Inisialisasi BatchLogger
        """
        self.total = total_items  # Total langkah untuk progres
        self.actual_items = actual_items  # Jumlah item sebenarnya
        self.process_name = process_name
        self.start_time = time.time()
        self.current = 0

    def log_progress(self, current: int):
        """
        Menampilkan progres real-time di konsol dalam satu baris, tanpa mencatat ke file
        """
        self.current = current
        if self.total == 0:
            return
        percent = int((current / self.total) * 100)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"{timestamp} - INFO - [{self.process_name}] Progres: {percent}% ({current}/{self.total})"
        sys.stdout.write(f"\r{msg}")
        sys.stdout.flush()

    def log_complete(self, skipped_items: int = 0):
        """
        Mencatat penyelesaian proses ke konsol dan file log di baris baru
        """
        total_time = int(time.time() - self.start_time)
        skipped_text = f" ({skipped_items} dilewati)" if skipped_items > 0 else ""
        # Bersihkan baris progres dan tambahkan baris baru
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()
        logging.info(
            f"[{self.process_name}] Selesai: {self.actual_items} item dalam {total_time}s{skipped_text}"
        )


def setup_logging() -> str:
    """
    Setup logging configuration
    """
    log_config = DEFAULT_CONFIG["logging"]
    os.makedirs(log_config["log_dir"], exist_ok=True)
    log_filename = datetime.now().strftime(f"{log_config['log_dir']}/%Y-%m-%d.log")

    # Reset handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=log_config["level"],
        format=log_config["format"],
        datefmt=log_config["datefmt"],
        handlers=[
            logging.FileHandler(log_filename, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    return log_filename

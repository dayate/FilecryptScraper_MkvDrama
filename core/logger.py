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

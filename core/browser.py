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

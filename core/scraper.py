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

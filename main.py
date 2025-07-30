# main.py
"""
Program utama FileCrypt Scraper - Bertindak sebagai orkestrator aplikasi.
"""

import logging
import os
import re
import sqlite3
import sys
import time
from typing import List

from config import DEFAULT_CONFIG
from core import cli  # <-- Impor modul CLI yang baru
from core.browser import BrowserManager
from core.database import DatabaseHandler
from core.file_handler import FileHandler
from core.logger import setup_logging
from core.scraper import FileCryptScraper


def process_single_url(url: str) -> tuple[List, str]:
    """
    Memproses scraping untuk satu URL, mengembalikan scraped_data dan container_title.
    Fungsi ini fokus pada logika scraping, bukan UI.
    """
    target_code = url.split("/")[-1].replace(".html", "")
    logging.info(f"⚙️⠀ Memulai proses untuk target_code: {target_code}")

    with BrowserManager() as browser_manager:
        scraper = None
        try:
            # Mencoba membuat halaman baru hingga 3 kali
            for attempt in range(3):
                try:
                    scraper = FileCryptScraper(browser_manager.context.new_page())
                    break
                except Exception as e:
                    logging.warning(
                        f"⚠️ [WARNING] Gagal membuka halaman baru, mencoba lagi ({attempt + 1}/3): {e}"
                    )
                    time.sleep(2)
            else:
                raise RuntimeError("Gagal membuka halaman baru setelah 3 percobaan")

            # Mencoba memuat URL hingga 3 kali
            for attempt in range(3):
                try:
                    scraper.page.goto(url, wait_until="load", timeout=15000)
                    break
                except Exception as e:
                    logging.warning(
                        f"⚠️ [WARNING] Gagal memuat URL, mencoba lagi ({attempt + 1}/3): {e}"
                    )
                    time.sleep(2)
            else:
                raise RuntimeError("Gagal memuat URL setelah 3 percobaan")

            browser_manager.close_about_blank_tabs()
            time.sleep(1)

            if not scraper.handle_password() or not scraper.handle_captcha():
                raise RuntimeError(
                    "Gagal melewati proteksi halaman (password/captcha)."
                )

            title, total_size = scraper.get_additional_info()
            container_title = (
                title
                if title and title.strip().lower() not in ("n/a", "unknown", "")
                else target_code
            )

            # Logika untuk mendapatkan status online/total
            online_count = sum(
                1
                for row in scraper.page.query_selector_all("tr.kwj3")
                if "online" in row.query_selector("td.status i").get_attribute("class")
            )
            total_count = len(scraper.page.query_selector_all("tr.kwj3"))

            # Panggil fungsi CLI untuk menampilkan info
            cli.print_url_info(
                {
                    "Judul": title,
                    "Status URL": f"{online_count}/{total_count} Online",
                    "Total Size": total_size,
                    "Target Code": target_code,
                }
            )

            providers = scraper.get_available_providers()
            # Panggil fungsi CLI untuk memilih provider
            selected_provider = cli.select_provider(providers)

            logging.info(f"⚙️⠀ Memulai proses scraping untuk target_code: {target_code}")
            scraped_data = scraper.scrape_file_info(
                selected_provider=selected_provider,
                all_providers=providers if not selected_provider else None,
            )
            return scraped_data, container_title

        except Exception as e:
            logging.error(f"❌⠀ Gagal memproses URL {url}: {e}")
            return [], target_code
        finally:
            if scraper and scraper.page and not scraper.page.is_closed():
                try:
                    scraper.page.close()
                except Exception as e:
                    logging.warning(f"[WARNING] Gagal menutup halaman: {e}")


def modify_title(title: str) -> str:
    """Fungsi untuk memodifikasi title sesuai pola yang diinginkan (logika bisnis)."""
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


def run_database_view():
    """Menjalankan alur kerja untuk melihat dan mengekspor data dari database."""
    db_path = DatabaseHandler.DB_PATH
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT MIN(title), target_code FROM scraped_data GROUP BY target_code"
        )
        raw_rows = cursor.fetchall()

        if not raw_rows:
            cli.print_message("Tidak ada data di database.", "yellow")
            return

        selections = [
            (modify_title(title), target_code) for title, target_code in raw_rows
        ]

        cli.display_database_summary(selections, db_path)
        choice = cli.prompt_database_action()

        if choice == "0":
            all_data = DatabaseHandler.get_all_data()
            if all_data:
                DatabaseHandler.export_to_excel(
                    all_data, "all"
                )  # Memanggil dari DatabaseHandler
                cli.print_message(
                    "Berhasil menyimpan semua data ke 'results/RESULT_DATABASE.xlsx'",
                    "green",
                )
        elif choice == "m":
            return
        elif choice.isdigit() and 1 <= int(choice) <= len(selections):
            selected_title, selected_target_code = selections[int(choice) - 1]
            data_to_save = DatabaseHandler.get_data_by_target_code(selected_target_code)
            if data_to_save:
                # Menggunakan FileHandler untuk penyimpanan file individual
                FileHandler.save_individual_files(
                    data_to_save, selected_target_code, selected_title
                )
        else:
            cli.print_message("Pilihan tidak valid!", "yellow")

    except sqlite3.Error as e:
        cli.print_message(f"Error membaca data dari DB: {e}", "red")
    finally:
        if "conn" in locals() and conn:
            conn.close()


def main():
    """Fungsi utama yang mengorkestrasi alur kerja aplikasi."""
    log_file = setup_logging()
    DatabaseHandler._init_db()

    cli.display_header("FILECRYPT SCRAPER")

    try:
        input_method = cli.select_input_method()
        urls = []
        if input_method == "1":
            urls.append(cli.get_valid_url())
        elif input_method == "2":
            urls_from_file = cli.get_urls_from_file()
            if not urls_from_file:
                return
            urls = urls_from_file
        elif input_method == "3":
            run_database_view()
            return

        processed_target_codes = []
        container_titles = {}
        if urls:
            for idx, url in enumerate(urls, 1):
                cli.print_message(f"🚀 Memproses URL {idx}/{len(urls)}: {url}")
                scraped_data, container_title = process_single_url(url)
                if scraped_data:
                    new_items = DatabaseHandler.save_to_sqlite(scraped_data)
                    cli.print_message(
                        f"✅ Berhasil menyimpan {new_items} item baru ke database.",
                        "green",
                    )
                    if new_items == 0:
                        cli.print_message(
                            "⚠️ Tidak ada item baru yang ditambahkan (data mungkin sudah ada).",
                            "yellow",
                        )

                    target_code = url.split("/")[-1].replace(".html", "")
                    processed_target_codes.append(target_code)
                    container_titles[target_code] = container_title
                else:
                    cli.print_message(
                        f"⚠️ Tidak ada data yang berhasil di-scrape dari {url}", "yellow"
                    )
                time.sleep(3)

        if processed_target_codes:
            output_option = cli.select_output_option()
            if output_option in ["1", "3"]:  # Cetak semua data
                all_data = DatabaseHandler.get_all_data()
                if all_data:
                    DatabaseHandler.export_to_excel(all_data, "all")
                    cli.print_message(
                        "✅ Berhasil menyimpan file database di 'results/RESULT_DATABASE.xlsx'",
                        "green",
                    )
            if output_option in ["2", "3"]:  # Cetak file individual
                for target_code in processed_target_codes:
                    data = DatabaseHandler.get_data_by_target_code(target_code)
                    if data:
                        title = container_titles.get(target_code, target_code)
                        FileHandler.save_individual_files(data, target_code, title)
            if output_option == "4":
                cli.print_message(
                    "✅ Data sudah tersimpan di database. Tidak ada file Excel yang dibuat.",
                    "green",
                )

    except Exception as e:
        logging.error(
            f"❌ Terjadi kesalahan tidak terduga di 'main': {e}", exc_info=True
        )
        cli.print_message(f"❌ Terjadi kesalahan fatal: {e}", "red")
        sys.exit(1)

    cli.display_header("PROSES SELESAI", "bold green")


if __name__ == "__main__":
    try:
        # Validasi path ekstensi di awal
        for ext_path in DEFAULT_CONFIG.extensions.paths:
            if not os.path.exists(os.path.join(ext_path, "manifest.json")):
                logging.critical(
                    f"❌ Ekstensi tidak ditemukan atau tidak valid di: {ext_path}"
                )
                sys.exit(1)
        main()
    except (KeyboardInterrupt, SystemExit) as e:
        if isinstance(e, SystemExit) and e.code != 0:
            logging.warning("Program dihentikan dengan status error.")
        else:
            logging.info("Program dihentikan oleh pengguna.")
    except Exception as e:
        # Menangkap kesalahan fatal sebelum loop utama dimulai
        logging.critical(f"❌ Gagal memulai aplikasi: {e}", exc_info=True)
        sys.exit(1)

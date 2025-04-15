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
from core.browser import BrowserManager
from core.scraper import FileCryptScraper
from core.database import DatabaseHandler
from core.file_handler import FileHandler
from core.logger import setup_logging
from config.constants import DEFAULT_CONFIG


def select_input_method() -> str:
    """Meminta pengguna memilih metode input URL atau cek database"""
    print("\n 1. Masukkan satu URL langsung")
    print(" 2. Pilih file berisi daftar URL (.txt)")
    print(" 3. Cek database")

    while True:
        try:
            choice = input("Masukkan nomor opsi (1-3): ").strip()
            if choice in ["1", "2", "3"]:
                return choice
            print("Opsi tidak valid! Harap masukkan nomor 1, 2, atau 3.")
        except Exception as e:
            logging.error(f"[ERROR] Error memilih metode input: {str(e)}")
            print("Terjadi error! Harap masukkan nomor 1, 2, atau 3.")
        time.sleep(1)


def get_valid_url() -> str:
    """Meminta satu URL valid dari pengguna"""
    while True:
        try:
            url = input("Masukkan URL: ").strip()
            if url.startswith("https://filecrypt.co/Container/") and url.endswith(".html"):
                return url
            print("URL tidak valid! Harap masukkan URL FileCrypt yang benar.")
        except Exception as e:
            logging.error(f"[ERROR] Error memasukkan URL: {str(e)}")
            print("Terjadi error! Harap masukkan URL yang valid.")
        time.sleep(1)


def get_urls_from_file() -> List[str]:
    """Membuka file explorer dan membaca URL dari file .txt"""
    root = tk.Tk()
    root.withdraw()  # Sembunyikan jendela utama tkinter
    file_path = filedialog.askopenfilename(
        title="Pilih file .txt berisi URL",
        filetypes=[("Text files", "*.txt")]
    )
    root.destroy()

    if not file_path:
        logging.error("[ERROR] Tidak ada file yang dipilih")
        print("Tidak ada file yang dipilih. Program berhenti.")
        sys.exit(1)

    valid_urls = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                url = line.strip()
                if url.startswith("https://filecrypt.co/Container/") and url.endswith(".html"):
                    valid_urls.append(url)
                else:
                    logging.warning(f"[WARNING] URL tidak valid di file: {url}")
        if not valid_urls:
            logging.error("[ERROR] Tidak ada URL valid di file")
            print("Tidak ada URL valid di file. Program berhenti.")
            sys.exit(1)
        return valid_urls
    except Exception as e:
        logging.error(f"[ERROR] Gagal membaca file: {str(e)}")
        print(f"Terjadi error saat membaca file: {str(e)}")
        sys.exit(1)


def select_output_option() -> str:
    """Meminta pengguna memilih opsi pencetakan output"""
    print("\n" + "=" * 100)
    print(" PILIH OPSI FILE OUTPUT ".center(100, "x"))
    print("=" * 100)
    print(" 1. Cetak semua data di database")
    print(" 2. Cetak file individual saja")
    print(" 3. Cetak keduanya")
    print(" 4. Simpan data ke database")

    while True:
        try:
            choice = input("Masukkan nomor opsi (1-4): ").strip()
            if choice in ["1", "2", "3", "4"]:
                return choice
            print("Opsi tidak valid! Harap masukkan nomor 1, 2, 3, atau 4.")
        except Exception as e:
            logging.error(f"[ERROR] Error memilih opsi pencetakan: {str(e)}")
            print("Terjadi error! Harap masukkan nomor 1, 2, 3, atau 4.")
        time.sleep(1)


def process_single_url(url: str) -> tuple[List, str]:
    """Memproses scraping untuk satu URL, mengembalikan scraped_data dan container_title"""
    target_code = url.split("/")[-1].replace(".html", "")
    logging.info(f"[MAIN] Memulai proses untuk target_code: {target_code}")

    with BrowserManager() as browser_manager:
        scraper = None
        try:
            # Buat halaman baru dengan retry
            for attempt in range(3):
                try:
                    scraper = FileCryptScraper(browser_manager.context.new_page())
                    break
                except Exception as e:
                    logging.warning(f"[WARNING] Gagal membuka halaman baru, mencoba lagi ({attempt + 1}/3): {str(e)}")
                    time.sleep(2)
            else:
                raise RuntimeError("Gagal membuka halaman baru setelah 3 percobaan")

            # Muat halaman dengan retry
            for attempt in range(3):
                try:
                    scraper.page.goto(url, wait_until="load", timeout=15000)
                    break
                except Exception as e:
                    logging.warning(f"[WARNING] Gagal memuat URL, mencoba lagi ({attempt + 1}/3): {str(e)}")
                    time.sleep(2)
            else:
                raise RuntimeError("Gagal memuat URL setelah 3 percobaan")

            browser_manager.close_about_blank_tabs()
            time.sleep(1)

            # Tangani keamanan
            if not scraper.handle_password():
                raise RuntimeError("Gagal menangani password")
            if not scraper.handle_captcha():
                raise RuntimeError("Gagal menangani CAPTCHA")

            # Ambil info
            title, total_size = scraper.get_additional_info()
            container_title = title if title and title.strip().lower() not in ("n/a", "unknown", "") else target_code
            # logging.info(f"[MAIN] Container title untuk target_code {target_code}: {container_title}")

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

            logging.info(f"[MAIN] Memulai proses scraping untuk target_code: {target_code}")
            logging.info(f"[MAIN] Total item di halaman: {total_count}")
            scraped_data = scraper.scrape_file_info(
                selected_provider=selected_provider,
                all_providers=providers if not selected_provider else None,
            )
            return scraped_data, container_title
        except Exception as e:
            logging.error(f"[ERROR] Gagal memproses URL {url}: {str(e)}")
            return [], target_code
        finally:
            if scraper and scraper.page:
                try:
                    scraper.page.close()
                except Exception as e:
                    logging.warning(f"[WARNING] Gagal menutup halaman: {str(e)}")
            # Tutup semua halaman yang tersisa
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
        print(f"Error koneksi database: {e}")
        logging.error(f"[ERROR] Error koneksi database: {str(e)}")
        return None


def modify_title(title: str) -> str:
    """Fungsi untuk memodifikasi title sesuai pola yang diinginkan"""
    if not title:
        return title

    # Langkah 1: Bersihkan teks yang tidak diinginkan
    patterns_to_remove = [
        r"\[MkvDrama\.Org\]",  # [MkvDrama.Org]
        r"\[MkvDrama\.me\]",   # [MkvDrama.me]
        r"\.mkv\b",            # .mkv
        r"\.x264\b",           # .x264
        r"\.1080p\b",          # .1080p
        r"\.720p\b",           # .720p
        r"\b.E01\b",            # E01 (standalone, case-sensitive)
    ]
    cleaned_title = title
    for pattern in patterns_to_remove:
        cleaned_title = re.sub(pattern, "", cleaned_title, flags=re.IGNORECASE)

    # Langkah 2: Terapkan regex untuk menangkap hingga S01 dan provider
    match = re.match(r"^(.*?S01)(?:E\d{2})?\.?([A-Z]+)?", cleaned_title.strip())
    if match:
        base_title = match.group(1)  # Ambil hingga S01
        provider = match.group(2) or ""  # Ambil provider jika ada
        return f"{base_title}{'.' + provider if provider else ''}"

    # Kembalikan title yang sudah dibersihkan jika tidak ada pola S01
    return cleaned_title.strip()

def sanitize_filename(filename: str) -> str:
    """Mengganti karakter tidak valid untuk nama file, tapi pertahankan titik"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "")
    return filename


def is_sheet_empty(sheet: openpyxl.worksheet.worksheet.Worksheet) -> bool:
    """Cek apakah sheet kosong (hanya header atau kurang)"""
    return sheet.max_row <= 1


def save_to_excel(data: List[tuple], filename: str):
    """Fungsi untuk menyimpan data ke file Excel dengan struktur seperti save_individual_files"""
    try:
        # Buat folder results
        os.makedirs("results", exist_ok=True)
        filename = os.path.join("results", f"{sanitize_filename(filename)}.xlsx")

        # Buka atau buat workbook
        if os.path.exists(filename):
            wb = openpyxl.load_workbook(filename)
            for sheet_name in wb.sheetnames[:]:
                sheet = wb[sheet_name]
                if is_sheet_empty(sheet) or sheet_name.lower() == "sheet":
                    wb.remove(sheet)
        else:
            wb = openpyxl.Workbook()
            wb.remove(wb.active)

        # Sheet ALL_PROVIDER_RESULTS
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

        # Cek entri yang sudah ada di ALL_PROVIDER_RESULTS
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

        # Tambahkan data baru ke ALL_PROVIDER_RESULTS
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
                        item[0],  # title
                        item[1],  # provider
                        item[2],  # size
                        item[3],  # status
                        item[4],  # download_url
                        item[5],  # bypass_url
                        item[6],  # target_code
                    ]
                )
                existing_all_entries.add(item_key)
                new_all_items += 1

        # Update nomor urut
        for idx, row in enumerate(all_sheet.iter_rows(min_row=2), 1):
            row[0].value = idx

        # Hapus sheet ALL_PROVIDER_RESULTS jika kosong
        if is_sheet_empty(all_sheet):
            wb.remove(all_sheet)

        # Sheet per provider
        providers = {item[1] for item in data if item[1]}  # Ambil provider unik
        for provider in providers:
            provider_items = [item for item in data if item[1] == provider]
            provider_sheet_name = provider[:31]  # Maksimal 31 karakter
            existing_provider_entries = set()

            # Cek entri yang sudah ada di sheet provider
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

            # Tambahkan data baru ke sheet provider
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

                # Update nomor urut
                for idx, row in enumerate(provider_sheet.iter_rows(min_row=2), 1):
                    row[0].value = idx

                # Hapus sheet provider jika kosong
                if is_sheet_empty(provider_sheet):
                    wb.remove(provider_sheet)

        # Hapus sheet default atau kosong
        has_data = False
        for sheet_name in wb.sheetnames[:]:
            sheet = wb[sheet_name]
            if not is_sheet_empty(sheet):
                has_data = True
            else:
                wb.remove(sheet)

        if not has_data or not wb.sheetnames:
            print("Tidak ada data untuk disimpan.")
            logging.info("[EXCEL] Tidak ada data untuk disimpan ke Excel")
            return

        if "Sheet" in wb.sheetnames:
            wb.remove(wb["Sheet"])

        # Atur lebar kolom dan alignment
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            column_widths = {
                "A": 5,  # No
                "B": 60,  # Title
                "C": 15,  # Provider
                "D": 10,  # Size
                "E": 15,  # Status
                "F": 60,  # Download URL
                "G": 60,  # Bypass URL
                "H": 15,  # _target_code
            }
            for col, width in column_widths.items():
                ws.column_dimensions[col].width = width
            for row in ws.iter_rows():
                for cell in row:
                    cell.alignment = Alignment(wrap_text=True, vertical="top")

        # Simpan file
        wb.save(filename)
        logging.info(f"[EXCEL] Data disimpan ke {filename}")

    except Exception as e:
        print(f"Error menyimpan ke Excel: {e}")
        logging.error(f"[ERROR] Gagal menyimpan ke Excel: {str(e)}")


def save_all_data():
    """Fungsi untuk menyimpan semua data dari database ke RESULT_DATABASE.xlsx"""
    conn = connect_db("results/scraped_data.db")
    if conn:
        try:
            cursor = conn.cursor()
            # Query untuk mengambil semua data
            cursor.execute(
                """
                SELECT title, provider, size, status, download_url, bypass_url, target_code
                FROM scraped_data
            """
            )
            rows = cursor.fetchall()

            if rows:
                # Simpan semua data ke RESULT_DATABASE.xlsx
                save_to_excel(rows, "RESULT_DATABASE")
            else:
                logging.info("[DB] Tidak ada data di database")

        except sqlite3.Error as e:
            logging.error(f"[ERROR] Error membaca data: {str(e)}")
        finally:
            conn.close()


def display_and_save_by_target_code(target_code: str, modified_title: str):
    """Fungsi untuk menyimpan data dengan target_code tertentu ke Excel"""
    conn = connect_db("results/scraped_data.db")
    if conn:
        try:
            cursor = conn.cursor()
            # Query untuk mengambil semua kolom berdasarkan target_code
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
                # Simpan ke Excel tanpa tampilkan di konsol
                save_to_excel(rows, modified_title)
            else:
                logging.info(f"[DB] Tidak ada data dengan target_code: {target_code}")

        except sqlite3.Error as e:
            logging.error(f"[ERROR] Error membaca data: {str(e)}")
        finally:
            conn.close()


def display_data():
    """Fungsi untuk menampilkan daftar data dalam tabel dan memilih target_code atau semua data"""
    db_name = "results/scraped_data.db"
    conn = connect_db(db_name)

    if conn:
        try:
            cursor = conn.cursor()
            # Query untuk mengambil satu title per target_code
            cursor.execute(
                """
                SELECT MIN(title), target_code
                FROM scraped_data
                GROUP BY target_code
                """
            )
            rows = cursor.fetchall()

            if not rows:
                print("Tidak ada data di database.")
                logging.info("[DB] Tidak ada data di database")
                return

            # Siapkan data untuk tabel
            table_data = []
            selections = []
            for idx, row in enumerate(rows, 1):
                title, target_code = row
                modified_title = modify_title(title)
                table_data.append([idx, modified_title, target_code])
                selections.append((modified_title, target_code))

            # Tampilkan tabel menggunakan tabulate
            print("\n" + "=" * 100)
            print(f"Data dari {db_name}".center(100, "x"))
            print("=" * 100)
            print(tabulate(
                table_data,
                headers=["No", "Title", "Target Code"],
                tablefmt="grid",
                stralign="left",
                numalign="center"
            ))
            print("\n0. Simpan semua data ke RESULT_DATABASE.xlsx")

            # Meminta input pilihan dari pengguna
            try:
                choice = input("\nMasukkan nomor untuk cetak data: ").strip()
                if choice == "0":
                    save_all_data()
                else:
                    choice = int(choice)
                    if 1 <= choice <= len(selections):
                        selected_title, selected_target_code = selections[choice - 1]
                        display_and_save_by_target_code(
                            selected_target_code, selected_title
                        )
                    else:
                        print("Pilihan tidak valid!")
                        logging.warning("[INPUT] Pilihan tidak valid")
            except ValueError:
                print("Masukkan angka yang valid!")
                logging.warning("[INPUT] Input bukan angka")

        except sqlite3.Error as e:
            print(f"Error membaca data: {e}")
            logging.error(f"[ERROR] Error membaca data: {str(e)}")
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
            return  # Keluar setelah menangani cek database

        processed_target_codes = []
        container_titles = {}
        for idx, url in enumerate(urls, 1):
            logging.info(f"[MAIN] Memproses URL {idx}/{len(urls)}: {url}")
            scraped_data, container_title = process_single_url(url)

            if scraped_data:
                new_items = DatabaseHandler.save_to_sqlite(scraped_data)
                logging.info(f"[MAIN] Berhasil menyimpan {new_items} item baru")
                if new_items == 0:
                    logging.info(f"[MAIN] Tidak ada item baru")
                target_code = url.split("/")[-1].replace(".html", "")
                processed_target_codes.append(target_code)
                container_titles[target_code] = container_title
            else:
                logging.info(f"[MAIN] Tidak ada data yang di-scrape")
                print(f"Tidak ada data yang berhasil di-scrape")

            # Penundaan untuk stabilitas
            time.sleep(3)

        if urls:
            if processed_target_codes:
                output_option = select_output_option()
                if output_option == "1":
                    all_data = DatabaseHandler.get_all_data()
                    if all_data:
                        DatabaseHandler.export_to_excel(all_data, processed_target_codes[0])
                        logging.info(
                            f"[FILE] Berhasil menyimpan file database di results\\RESULT_DATABASE.xlsx"
                        )
                    else:
                        logging.info("[FILE] Tidak ada data di database")
                elif output_option == "2":
                    for target_code in processed_target_codes:
                        scraped_data = DatabaseHandler.get_data_by_target_code(target_code)
                        if scraped_data:
                            container_title = container_titles.get(target_code, target_code)
                            FileHandler.save_individual_files(scraped_data, target_code, container_title)
                            logging.info(
                                f"[FILE] Berhasil menyimpan file individual di results\\{FileHandler._sanitize_filename(container_title, target_code)}.xlsx"
                            )
                elif output_option == "3":
                    all_data = DatabaseHandler.get_all_data()
                    if all_data:
                        DatabaseHandler.export_to_excel(all_data, processed_target_codes[0])
                        logging.info(
                            f"[FILE] Berhasil menyimpan file database di results\\RESULT_DATABASE.xlsx"
                        )
                    for target_code in processed_target_codes:
                        scraped_data = DatabaseHandler.get_data_by_target_code(target_code)
                        if scraped_data:
                            container_title = container_titles.get(target_code, target_code)
                            FileHandler.save_individual_files(scraped_data, target_code, container_title)
                            logging.info(
                                f"[FILE] Berhasil menyimpan file individual di results\\{FileHandler._sanitize_filename(container_title, target_code)}.xlsx"
                            )
                elif output_option == "4":
                    logging.info("[MAIN] Data berhasil tersimpan di DATABASE")
            else:
                logging.info("[MAIN] Tidak ada data yang berhasil di-scrape dari URL manapun")
                print("Tidak ada data yang berhasil di-scrape dari URL manapun.")

        logging.info(
            "[MAIN] Scraping selesai. Output telah diproses. Program selesai."
        )

    except Exception as e:
        logging.error(f"[ERROR] Terjadi kesalahan: {str(e)}")
        print(f"\nTerjadi kesalahan: {str(e)}")
        sys.exit(1)


def print_info(info: Dict[str, str]):
    print("\n" + "=" * 100)
    print(" INFORMASI URL ".center(100, "x"))
    print("=" * 100)
    for key, value in info.items():
        print(f" {key:<15} : {value}")


def select_provider(providers: List[str]) -> Optional[str]:
    if not providers:
        print("\nTidak ada provider yang tersedia.")
        return None

    print("\n" + "=" * 100)
    print(" PROVIDER YANG TERSEDIA ".center(100, "x"))
    print("=" * 100)
    for i, provider in enumerate(providers, 1):
        print(f" {i}. {provider}")

    try:
        provider_input = input("Masukkan nomor provider (0 untuk semua): ").strip()
        if provider_input == "0":
            return None
        elif provider_input.isdigit():
            provider_num = int(provider_input)
            if 1 <= provider_num <= len(providers):
                return providers[provider_num - 1]
        print("Nomor tidak valid! Akan mengambil semua provider.")
        time.sleep(2)
        return None
    except Exception as e:
        logging.error(f"[ERROR] Error memilih provider: {str(e)}")
        print("Terjadi error! Akan mengambil semua provider.")
        time.sleep(2)
        return None


if __name__ == "__main__":
    try:
        for ext in DEFAULT_CONFIG["extensions"]["paths"]:
            if not os.path.exists(os.path.join(ext, "manifest.json")):
                raise FileNotFoundError(f"[ERROR] Ekstensi tidak valid di: {ext}")

        print("=" * 100)
        print(" FILECRYPT SCRAPER ".center(100, "x"))
        print("=" * 100)

        main()
        print("=" * 100)
        print(" FILECRYPT SELESAI ".center(100, "x"))
        print("=" * 100)
    except Exception as e:
        logging.error(f"[ERROR] Error: {str(e)}")
        print(f"\nTerjadi kesalahan: {str(e)}")
        sys.exit(1)

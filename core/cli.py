# core/cli.py
"""
Modul untuk menangani semua interaksi Antarmuka Pengguna Baris Perintah (CLI).
"""
import tkinter as tk
from tkinter import filedialog
from typing import List, Dict, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Instance console terpusat untuk digunakan di seluruh modul CLI
console = Console()


def display_header(text: str, style: str = "bold blue"):
    """Menampilkan panel header yang rapi."""
    console.print(
        Panel(
            Text(text, style=style, justify="center"),
            border_style="cyan",
            expand=True,
        )
    )


def select_input_method() -> str:
    """Meminta pengguna memilih metode input URL atau cek database."""
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
        choice = console.input("Masukkan nomor opsi (1-3): ").strip()
        if choice in ["1", "2", "3"]:
            return choice
        console.print(
            "⚠️ [yellow]Opsi tidak valid! Harap masukkan nomor 1, 2, atau 3.[/yellow]"
        )


def get_valid_url() -> str:
    """Meminta satu URL valid dari pengguna."""
    while True:
        url = console.input("Masukkan URL: ").strip()
        if url.startswith("https://www.filecrypt.cc/Container/") and url.endswith(
            ".html"
        ):
            return url
        console.print(
            "⚠️ [yellow]URL tidak valid! Harap masukkan URL FileCrypt yang benar.[/yellow]"
        )


def get_urls_from_file() -> Optional[List[str]]:
    """Membuka file explorer dan membaca URL dari file .txt."""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Pilih file .txt berisi URL", filetypes=[("Text files", "*.txt")]
    )
    root.destroy()

    if not file_path:
        console.print("❌⠀ [red]Tidak ada file yang dipilih.[/red]")
        return None

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
                    console.print(
                        f"⚠️ [yellow]URL tidak valid di file diabaikan: {url}[/yellow]"
                    )
        if not valid_urls:
            console.print("❌⠀ [red]Tidak ada URL valid di dalam file.[/red]")
            return None
        return valid_urls
    except Exception as e:
        console.print(f"❌⠀ [red]Terjadi error saat membaca file: {str(e)}[/red]")
        return None


def select_output_option() -> str:
    """Meminta pengguna memilih opsi pencetakan output."""
    console.print(
        Panel(
            "\n1. Cetak semua data di database \n2. Cetak file individual saja \n3. Cetak keduanya \n4. Simpan data ke database ",
            title="[bold blue]PILIH OPSI FILE OUTPUT[/bold blue]",
            border_style="cyan",
            expand=True,
        )
    )
    while True:
        choice = console.input("Masukkan nomor opsi (1-4): ").strip()
        if choice in ["1", "2", "3", "4"]:
            return choice
        console.print(
            "⚠️ [yellow]Opsi tidak valid! Harap masukkan nomor 1, 2, 3, atau 4.[/yellow]"
        )


def print_url_info(info: Dict[str, str]):
    """Menampilkan informasi URL yang sedang diproses."""
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
    """Menampilkan daftar provider dan meminta pilihan pengguna."""
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

    provider_input = console.input("Masukkan nomor provider (0 untuk semua): ").strip()
    if provider_input == "0":
        return None
    if provider_input.isdigit():
        provider_num = int(provider_input)
        if 1 <= provider_num <= len(providers):
            return providers[provider_num - 1]

    console.print(
        "⚠️ [yellow]Nomor tidak valid! Akan mengambil semua provider.[/yellow]"
    )
    return None


def display_database_summary(rows: List[tuple], db_name: str):
    """Menampilkan tabel ringkasan data dari database."""
    if not rows:
        console.print("⚠️ [yellow]Tidak ada data di database.[/yellow]")
        return

    table = Table(
        title=Text(f"Data dari {db_name}", style="bold blue"),
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("No", style="cyan", justify="center")
    table.add_column("Title", style="green")
    table.add_column("Target Code", style="magenta")

    for idx, row in enumerate(rows, 1):
        title, target_code = row
        table.add_row(str(idx), title, target_code)

    console.print(table)


def prompt_database_action() -> str:
    """Meminta input dari pengguna setelah tabel database ditampilkan."""
    console.print("\n0. Simpan semua data ke RESULT_DATABASE.xlsx")
    console.print("m. Kembali ke menu utama")
    return console.input("\nMasukkan nomor untuk cetak data, 0, atau m: ").strip()


def print_message(message: str, style: str = "white"):
    """Fungsi generik untuk mencetak pesan ke konsol."""
    console.print(f"[{style}]{message}[/{style}]")

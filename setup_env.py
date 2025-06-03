#!/usr/bin/env python
"""
Script untuk menyiapkan file .env

Script ini akan:
1. Memeriksa apakah file .env sudah ada
2. Jika belum, menyalin env.example ke .env
3. Membantu pengguna mengisi nilai-nilai konfigurasi penting
"""

import os
import shutil
import sys
from pathlib import Path


def setup_env():
    """Setup file .env dari template env.example"""
    env_file = Path(".env")
    example_file = Path("env.example")

    # Periksa apakah file .env sudah ada
    if env_file.exists():
        print("File .env sudah ada.")
        overwrite = input("Apakah Anda ingin membuat ulang file .env? (y/N): ").lower()
        if overwrite != "y":
            print("Setup dibatalkan. File .env tidak diubah.")
            return

    # Periksa apakah file env.example ada
    if not example_file.exists():
        print("ERROR: File env.example tidak ditemukan!")
        return

    # Salin env.example ke .env
    shutil.copy2(example_file, env_file)
    print(f"File {example_file} disalin ke {env_file}")

    # Minta pengguna untuk mengisi nilai konfigurasi penting
    print("\n=== Konfigurasi Extensions ===")
    print("Masukkan path ke folder ekstensi browser (misalnya uBlock Origin).")
    print("Path harus menggunakan double backslash (\\\\) untuk Windows.")

    extensions_path = input("Path Extensions (kosongkan untuk default): ")

    # Baca isi file .env
    with open(env_file, "r", encoding="utf-8") as f:
        env_content = f.readlines()

    # Perbarui nilai EXTENSIONS_PATHS jika pengguna memberikan input
    if extensions_path:
        for i, line in enumerate(env_content):
            if line.startswith("EXTENSIONS_PATHS="):
                env_content[i] = f"EXTENSIONS_PATHS={extensions_path}\n"
                break

    # Tulis kembali file .env
    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(env_content)

    print("\nSetup .env selesai!")
    print("Anda dapat mengedit file .env secara manual untuk konfigurasi lebih lanjut.")


if __name__ == "__main__":
    setup_env()

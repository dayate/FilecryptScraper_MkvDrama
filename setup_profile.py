import os
import time
from playwright.sync_api import sync_playwright

# --- KONFIGURASI PATH ---
PROFILE_DIR = os.path.abspath("./profile")

# Buat daftar path absolut ke setiap direktori ekstensi yang ingin Anda muat
# Pastikan nama folder ini sesuai dengan yang ada di project Anda
extension_folders = ["./Extensions/uBlock", "./Extensions/Adguard"]
extension_paths = [
    os.path.abspath(folder)
    for folder in extension_folders
    if os.path.exists(os.path.abspath(folder))
]

# --- MULAI PROSES SETUP ---
print(f"📁 Menggunakan direktori profil di: {PROFILE_DIR}")

if not extension_paths:
    print(
        "❌ PERINGATAN: Tidak ada direktori ekstensi yang ditemukan. Pastikan path di 'extension_folders' sudah benar."
    )
else:
    print("📦 Ekstensi yang akan dimuat:")
    for path in extension_paths:
        print(f"   - {path}")

print("\n--- PANDUAN SETUP ---")
print("1. Jendela browser akan terbuka dengan ekstensi yang SUDAH TER-LOAD.")
print(
    "2. Anda bisa mengonfigurasi pengaturan ekstensi jika perlu (misal: update filter list)."
)
print("3. Setelah selesai, TUTUP JENDELA BROWSER secara manual.")
print("4. Profil beserta ekstensi akan tersimpan secara permanen.")


with sync_playwright() as p:
    try:
        # Gabungkan semua path ekstensi menjadi satu string dipisahkan koma
        extensions_to_load_str = ",".join(extension_paths)

        context = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            args=[
                f"--disable-extensions-except={extensions_to_load_str}",
                f"--load-extension={extensions_to_load_str}",
                "--disable-blink-features=AutomationControlled",
            ],
            ignore_default_args=["--enable-automation"],
        )
        print(
            "\n✅ Browser berhasil diluncurkan dengan ekstensi. Silakan lakukan setup..."
        )
        context.wait_for_event("close", timeout=0)
        print("\n👍 Jendela browser ditutup. Setup profil dan ekstensi selesai.")

    except Exception as e:
        print(f"\n❌ Terjadi error: {e}")

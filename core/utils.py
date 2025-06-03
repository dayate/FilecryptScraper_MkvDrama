"""
Modul untuk utility functions
"""

import re
import random
from typing import List, Dict
from config import DEFAULT_CONFIG


def clean_filename(title: str) -> str:
    """
    Membersihkan judul untuk dijadikan nama file

    Args:
        title (str): Judul yang akan dibersihkan

    Returns:
        str: Judul yang sudah dibersihkan
    """
    if not isinstance(title, str):
        return "unknown"
    title = re.sub(r'[\\/*?:"<>|]', "", title.strip())
    return title[:50]


def get_random_ua() -> str:
    """
    Mendapatkan random user agent dari config

    Returns:
        str: Random user agent string
    """
    return random.choice(DEFAULT_CONFIG["user_agents"])


def normalize_series_title(title: str) -> str:
    """
    Normalisasi judul series untuk konsistensi penamaan file
    Contoh:
    Input: "LTNS.S01E01.1080p.WEB.x264"
    Output: "LTNS.S01"
    """
    patterns = [
        r"(.*?\.S\d{2})",  # Format S01
        r"(.*?\.Season.\d+)",  # Format Season 1
        r"(.*?\s\d{4})",  # Format 2023
    ]

    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            base = match.group(1)
            # Standarisasi format
            base = re.sub(r"\.Season.(\d+)", lambda m: f".S{m.group(1).zfill(2)}", base)
            return base

    return "Various"

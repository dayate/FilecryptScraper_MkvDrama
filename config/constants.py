"""
Konstanta-konstanta yang digunakan di seluruh aplikasi
"""

DEFAULT_CONFIG = {
    "browser": {
        "user_data_dir": "./profile",
        "headless": False,
        "args": [
            "--disable-component-update",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-webgl",
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
        ],
        "ignore_default_args": [
            "--enable-automation",
            "--disable-extensions",
        ],
    },
    "extensions": {
        "paths": [
            "C:\\Users\\Taufik Hidayat\\Project\\AI\\Grok\\refactor_scraper\\Extensions\\uBlock",
            "C:\\Users\\Taufik Hidayat\\Project\\AI\\Grok\\refactor_scraper\\Extensions\\Adguard",
        ]
    },
    "logging": {
        "log_dir": "logs",
        "level": "INFO",
        "format": "%(asctime)s - %(levelname)-4s - %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    },
    "timeouts": {
        "selector_wait": 10000,
        "popup": 5000,
        "page_load": 10000,
        "password_check": 5,
        "captcha_check": 5,
        "batch_delay": 1,
        "captcha": 300,
        "password": 300,
    },
    "providers": {
        "send_aliases": [
            "send.cm",
            "sendit.cloud",
            "send.co",
            "send.now",
            "send.com",
            "send.cw",
        ]
    },
    "pixeldrain": {
        "bypass_urls": [
            "https://cdn.pd1.workers.dev/api/file/CODE-FILE",
            "https://cdn.pd6.workers.dev/api/file/CODE-FILE",
            "https://cdn.pd7.workers.dev/api/file/CODE-FILE",
            "https://cdn.pd8.workers.dev/api/file/CODE-FILE",
            "https://cdn.pd10.workers.dev/api/file/CODE-FILE",
            "https://cdn.pd3-gamedriveorg.workers.dev/api/file/CODE-FILE",
            "https://cdn.pd5-gamedriveorg.workers.dev/api/file/CODE-FILE",
            "https://cdn.pd9-gamedriveorg.workers.dev/api/file/CODE-FILE",
        ]
    },
    "user_agents": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
    ],
    "scraper": {"batch_processing": True, "max_batch_size": 8},
}

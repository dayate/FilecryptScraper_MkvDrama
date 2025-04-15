import sqlite3
from typing import List, Optional, Dict, Any
from dataclasses import asdict
from models.data_models import ScrapedData
import logging
import os


class SQLiteHandler:
    def __init__(self, db_path: str = "results/filecrypt.db"):
        os.makedirs("results", exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database with proper schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Main table for all providers
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    size TEXT,
                    status TEXT,
                    download_url TEXT,
                    bypass_url TEXT,
                    target_code TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(title, provider, target_code)
                )
            """
            )

            # Index untuk pencarian cepat
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_files_target ON files(target_code)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_files_provider ON files(provider)"
            )

            conn.commit()

    def _get_connection(self):
        """Get a new database connection"""
        return sqlite3.connect(self.db_path)

    def save_data(self, data: List[ScrapedData]):
        """Save scraped data to SQLite"""
        if not data:
            return

        with self._get_connection() as conn:
            cursor = conn.cursor()

            for item in data:
                try:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO files (
                            title, provider, size, status,
                            download_url, bypass_url, target_code
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            item.title,
                            item.provider,
                            item.size,
                            item.status,
                            item.download_url,
                            item.bypass_url,
                            item.target_code,
                        ),
                    )
                except Exception as e:
                    logging.error(f"[SQLITE] Gagal menyimpan data: {str(e)}")
                    continue

            conn.commit()
            logging.info(f"[SQLITE] Disimpan {len(data)} item ke database")

    def get_all_data(self) -> List[Dict[str, Any]]:
        """Get all data from database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    title, provider, size, status,
                    download_url, bypass_url, target_code
                FROM files
                ORDER BY target_code, provider, title
            """
            )

            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def data_exists(self, title: str, provider: str, target_code: str) -> bool:
        """Check if data already exists"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 1 FROM files
                WHERE title = ? AND provider = ? AND target_code = ?
                LIMIT 1
            """,
                (title, provider, target_code),
            )
            return cursor.fetchone() is not None

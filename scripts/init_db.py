from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "db" / "metadata.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repository_id INTEGER,
    repository_key TEXT NOT NULL,
    repository_name TEXT,
    project_id TEXT,
    project_title TEXT,
    source_url TEXT NOT NULL,
    direct_download_url TEXT,
    doi TEXT,
    license TEXT,
    year TEXT,
    description TEXT,
    uploader_name TEXT,
    uploader_email TEXT,
    author_names TEXT,
    owner_names TEXT,
    involved_people TEXT,
    keywords_original TEXT,
    local_dir TEXT NOT NULL,
    local_filename TEXT,
    file_type TEXT,
    download_status TEXT NOT NULL,
    failure_reason TEXT,
    downloaded_at TEXT NOT NULL,
    file_size_bytes INTEGER,
    checksum_sha256 TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS project_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    download_id INTEGER NOT NULL,
    role TEXT,
    filename TEXT,
    local_path TEXT,
    file_type TEXT,
    source_url TEXT,
    download_status TEXT,
    failure_reason TEXT,
    FOREIGN KEY(download_id) REFERENCES downloads(id)
);

CREATE TABLE IF NOT EXISTS repository_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repository_key TEXT NOT NULL,
    query_text TEXT NOT NULL,
    used_at TEXT NOT NULL,
    notes TEXT
);
"""


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)
        conn.commit()
    print(f"Initialized database at: {DB_PATH}")


if __name__ == "__main__":
    main()

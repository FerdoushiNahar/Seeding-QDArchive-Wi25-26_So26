from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import sqlite3
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "db" / "metadata.sqlite3"
DOWNLOADS_DIR = BASE_DIR / "data" / "downloads"
LOGS_DIR = BASE_DIR / "data" / "logs"
CONFIG_DIR = BASE_DIR / "config"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str, fallback: str = "item") -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or fallback


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_repositories() -> list[dict[str, Any]]:
    with (CONFIG_DIR / "repositories.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def load_queries() -> list[str]:
    path = CONFIG_DIR / "queries.txt"
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


@dataclass
class Candidate:
    repository_id: int
    repository_key: str
    repository_name: str
    source_url: str
    project_id: str
    project_title: str
    direct_download_url: str | None = None
    doi: str | None = None
    license: str | None = None
    year: str | None = None
    description: str | None = None
    uploader_name: str | None = None
    uploader_email: str | None = None
    author_names: list[str] = field(default_factory=list)
    owner_names: list[str] = field(default_factory=list)
    involved_people: list[str] = field(default_factory=list)
    keywords_original: str | None = None
    file_type: str | None = None
    associated_files: list[dict[str, Any]] = field(default_factory=list)
    notes: str | None = None


def get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)

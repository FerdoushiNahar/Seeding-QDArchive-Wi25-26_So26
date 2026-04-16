from __future__ import annotations

from pathlib import Path
import csv
from common import BASE_DIR, get_conn

OUT = BASE_DIR / "data" / "db" / "downloads_report.csv"


def main() -> None:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT repository_key, project_id, project_title, source_url, local_dir, local_filename, file_type, license, download_status, failure_reason, downloaded_at FROM downloads ORDER BY repository_key, id"
        ).fetchall()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "repository_key", "project_id", "project_title", "source_url", "local_dir",
            "local_filename", "file_type", "license", "download_status", "failure_reason", "downloaded_at"
        ])
        writer.writerows(rows)

    print(f"Exported CSV report to {OUT}")


if __name__ == "__main__":
    main()

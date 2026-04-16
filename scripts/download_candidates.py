from __future__ import annotations

from pathlib import Path
import requests
import sys
from .common import DOWNLOADS_DIR, get_conn, sha256_of_file, utc_now_iso

TIMEOUT = 60
HEADERS = {"User-Agent": "QDArchiveStudentProject/1.0"}


def download_file(url: str, target_path: Path) -> tuple[bool, str | None, int | None, str | None]:
    try:
        response = requests.get(url, timeout=TIMEOUT, stream=True, headers=HEADERS)
        if response.status_code != 200:
            return False, f"http_{response.status_code}", None, None

        target_path.parent.mkdir(parents=True, exist_ok=True)
        with target_path.open("wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        size = target_path.stat().st_size
        checksum = sha256_of_file(target_path)
        return True, None, size, checksum
    except requests.RequestException as e:
        return False, f"request_error: {e}", None, None
    except Exception as e:
        return False, f"unexpected_error: {e}", None, None


def choose_filename(default_stem: str, file_type: str | None) -> str:
    if file_type and file_type.startswith('.'):
        return f"{default_stem}{file_type}"
    return f"{default_stem}.bin"


def main() -> None:
    repo_filter = None
    if len(sys.argv) > 1:
        repo_filter = sys.argv[1]

    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, repository_key, project_id, project_title, direct_download_url, file_type, local_dir
            FROM downloads
            WHERE download_status = 'discovered'
            ORDER BY repository_key, id
            """
        ).fetchall()

        for row in rows:
            row_id, repository_key, project_id, project_title, direct_download_url, file_type, local_dir = row

            if repo_filter and repository_key != repo_filter:
                continue

            if not direct_download_url:
                conn.execute(
                    "UPDATE downloads SET download_status=?, failure_reason=?, downloaded_at=? WHERE id=?",
                    ("failed", "no_direct_download_url", utc_now_iso(), row_id)
                )
                continue

            filename = choose_filename("main", file_type)
            target = DOWNLOADS_DIR / local_dir / filename

            ok, reason, size, checksum = download_file(direct_download_url, target)
            if ok:
                conn.execute(
                    """
                    UPDATE downloads
                    SET download_status=?, failure_reason=?, downloaded_at=?, local_filename=?, file_size_bytes=?, checksum_sha256=?
                    WHERE id=?
                    """,
                    ("downloaded", None, utc_now_iso(), filename, size, checksum, row_id)
                )
            else:
                conn.execute(
                    "UPDATE downloads SET download_status=?, failure_reason=?, downloaded_at=? WHERE id=?",
                    ("failed", reason, utc_now_iso(), row_id)
                )
                continue

            project_files = conn.execute(
                "SELECT id, filename, file_type, source_url FROM project_files WHERE download_id=? AND download_status='discovered'",
                (row_id,),
            ).fetchall()
            for pf_id, pf_name, pf_type, pf_url in project_files:
                if not pf_url:
                    conn.execute(
                        "UPDATE project_files SET download_status=?, failure_reason=? WHERE id=?",
                        ("failed", "no_source_url", pf_id),
                    )
                    continue
                safe_name = pf_name or choose_filename(f"file-{pf_id}", pf_type)
                target = DOWNLOADS_DIR / local_dir / safe_name
                ok, reason, _size, _checksum = download_file(pf_url, target)
                conn.execute(
                    "UPDATE project_files SET local_path=?, download_status=?, failure_reason=? WHERE id=?",
                    (str(target), "downloaded" if ok else "failed", None if ok else reason, pf_id),
                )

        conn.commit()
    print("Download step finished.")


if __name__ == "__main__":
    main()

from __future__ import annotations

from common import get_conn


def main() -> None:
    with get_conn() as conn:
        counts = conn.execute(
            "SELECT repository_key, download_status, COUNT(*) FROM downloads GROUP BY repository_key, download_status ORDER BY repository_key, download_status"
        ).fetchall()

    if not counts:
        print("No rows in database yet.")
        return

    for repo_key, status, count in counts:
        print(f"{repo_key:10s} | {status:12s} | {count}")


if __name__ == "__main__":
    main()

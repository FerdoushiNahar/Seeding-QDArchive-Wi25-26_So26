from __future__ import annotations

from .common import DOWNLOADS_DIR, get_conn, sha256_of_file, utc_now_iso
from repo6_adapter import discover as discover_repo6
from repo18_adapter import discover as discover_repo18


def insert_candidate(conn, candidate):
    existing = conn.execute(
        "SELECT id FROM downloads WHERE repository_key=? AND source_url=?",
        (candidate.repository_key, candidate.source_url),
    ).fetchone()
    if existing:
        return existing[0]

    local_dir = f"{candidate.repository_key}/{candidate.project_id}"
    cur = conn.execute(
        """
        INSERT INTO downloads (
            repository_id, repository_key, repository_name,
            project_id, project_title, source_url, direct_download_url,
            doi, license, year, description, uploader_name, uploader_email,
            author_names, owner_names, involved_people, keywords_original,
            local_dir, local_filename, file_type,
            download_status, failure_reason, downloaded_at, file_size_bytes,
            checksum_sha256, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            candidate.repository_id,
            candidate.repository_key,
            candidate.repository_name,
            candidate.project_id,
            candidate.project_title,
            candidate.source_url,
            candidate.direct_download_url,
            candidate.doi,
            candidate.license,
            candidate.year,
            candidate.description,
            candidate.uploader_name,
            candidate.uploader_email,
            "; ".join(candidate.author_names) if candidate.author_names else None,
            "; ".join(candidate.owner_names) if candidate.owner_names else None,
            "; ".join(candidate.involved_people) if candidate.involved_people else None,
            candidate.keywords_original,
            local_dir,
            None,
            candidate.file_type,
            "discovered",
            None,
            utc_now_iso(),
            None,
            None,
            candidate.notes,
        )
    )
    download_id = cur.lastrowid

    for f in candidate.associated_files:
        conn.execute(
            """
            INSERT INTO project_files (
                download_id, role, filename, local_path, file_type, source_url, download_status, failure_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                download_id,
                f.get("role", "associated"),
                f.get("filename"),
                None,
                f.get("file_type"),
                f.get("source_url"),
                "discovered" if f.get("source_url") else "failed",
                None if f.get("source_url") else "restricted_or_missing_url",
            ),
        )

    return download_id


def main() -> None:
    repos = load_repositories()
    queries = load_queries()
    with get_conn() as conn:
        for repo in repos:
            for q in queries:
                exists = conn.execute(
                    "SELECT 1 FROM repository_queries WHERE repository_key=? AND query_text=?",
                    (repo["repo_key"], q),
                ).fetchone()
                if not exists:
                    conn.execute(
                        "INSERT INTO repository_queries (repository_key, query_text, used_at, notes) VALUES (?, ?, ?, ?)",
                        (repo["repo_key"], q, utc_now_iso(), "initial query set")
                    )

            if repo["repo_id"] == 6:
                candidates = discover_repo6(repo, queries)
            elif repo["repo_id"] == 18:
                candidates = discover_repo18(repo, queries)
            else:
                candidates = []

            for c in candidates:
                insert_candidate(conn, c)
        conn.commit()

    print("Candidate discovery finished.")


if __name__ == "__main__":
    main()

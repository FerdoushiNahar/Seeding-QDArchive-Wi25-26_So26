import sqlite3
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DB = ROOT / "data" / "db" / "metadata.sqlite3"
TARGET_DB = ROOT / "23129118-seeding.db"


def utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def normalize_download_status(status: str | None, reason: str | None = None) -> str:
    s = (status or "").strip().lower()
    r = (reason or "").strip().lower()

    if s == "downloaded":
        return "SUCCEEDED"

    if "login" in r or "restricted" in r or "forbidden" in r or "403" in r:
        return "FAILED_LOGIN_REQUIRED"

    if "too large" in r or "file too large" in r:
        return "FAILED_TOO_LARGE"

    return "FAILED_SERVER_UNRESPONSIVE"


def normalize_person_role(role: str | None) -> str:
    if not role:
        return "UNKNOWN"

    r = role.strip().upper()
    allowed = {"UPLOADER", "AUTHOR", "OWNER", "OTHER", "UNKNOWN"}
    if r in allowed:
        return r

    mapping = {
        "DEPOSITOR": "UPLOADER",
        "CONTACT": "OTHER",
        "CREATOR": "AUTHOR",
    }
    return mapping.get(r, "UNKNOWN")


def normalize_license(license_text: str | None) -> str:
    if not license_text:
        return "UNKNOWN"

    text = license_text.strip()

    replacements = {
        "CC BY 4.0 International": "CC BY 4.0",
        "CC-BY 4.0": "CC BY 4.0",
        "CC BY-SA 4.0 International": "CC BY-SA 4.0",
        "CC0 1.0 Universal": "CC0 1.0",
    }

    return replacements.get(text, text)


def infer_repo_info(repository_key: str | None) -> tuple[int, str, str]:
    if repository_key == "repo6":
        return 6, "https://dataverse.no/", "repo6"
    if repository_key == "repo18":
        return 18, "https://dataverse.harvard.edu/", "repo18"
    return 0, "", repository_key or ""


def create_target_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP TABLE IF EXISTS PROJECTS;
        DROP TABLE IF EXISTS FILES;
        DROP TABLE IF EXISTS KEYWORDS;
        DROP TABLE IF EXISTS PERSON_ROLE;
        DROP TABLE IF EXISTS LICENSES;

        CREATE TABLE PROJECTS (
            id INTEGER PRIMARY KEY,
            query_string TEXT,
            repository_id INTEGER NOT NULL,
            repository_url TEXT NOT NULL,
            project_url TEXT NOT NULL,
            version TEXT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            language TEXT,
            doi TEXT,
            upload_date TEXT,
            download_date TEXT NOT NULL,
            download_repository_folder TEXT NOT NULL,
            download_project_folder TEXT NOT NULL,
            download_version_folder TEXT,
            download_method TEXT NOT NULL
        );

        CREATE TABLE FILES (
            id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES PROJECTS(id)
        );

        CREATE TABLE KEYWORDS (
            id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            keyword TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES PROJECTS(id)
        );

        CREATE TABLE PERSON_ROLE (
            id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES PROJECTS(id)
        );

        CREATE TABLE LICENSES (
            id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            license TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES PROJECTS(id)
        );
        """
    )
    conn.commit()


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone()
    return row is not None


def main() -> None:
    if not SOURCE_DB.exists():
        raise FileNotFoundError(f"Source DB not found: {SOURCE_DB}")

    if TARGET_DB.exists():
        TARGET_DB.unlink()

    src = sqlite3.connect(SOURCE_DB)
    src.row_factory = sqlite3.Row

    dst = sqlite3.connect(TARGET_DB)
    create_target_schema(dst)

    if not table_exists(src, "downloads"):
        raise RuntimeError("Expected table 'downloads' not found in metadata.sqlite3")

    downloads = src.execute(
        """
        SELECT *
        FROM downloads
        """
    ).fetchall()

    for row in downloads:
        row = dict(row)

        project_id = row["id"]
        repository_key = row.get("repository_key")
        repository_id, repository_url, repo_folder = infer_repo_info(repository_key)

        project_url = row.get("source_url") or ""
        title = row.get("project_title") or f"project-{project_id}"
        description = row.get("description") or ""
        doi = row.get("doi")
        upload_date = row.get("upload_date")
        download_date = row.get("downloaded_at") or utc_now_iso()
        project_folder = row.get("local_dir") or f"project-{project_id}"
        file_type = (row.get("file_type") or "").lstrip(".")
        download_method = "API-CALL"

        dst.execute(
            """
            INSERT INTO PROJECTS (
                id, query_string, repository_id, repository_url, project_url, version,
                title, description, language, doi, upload_date, download_date,
                download_repository_folder, download_project_folder, download_version_folder,
                download_method
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                row.get("query_string"),
                repository_id,
                repository_url,
                project_url,
                row.get("version"),
                title,
                description,
                row.get("language"),
                doi,
                upload_date,
                download_date,
                repo_folder,
                project_folder,
                row.get("download_version_folder"),
                download_method,
            ),
        )

        main_status = normalize_download_status(
            row.get("download_status"),
            row.get("failure_reason"),
        )

        main_file_name = row.get("local_filename") or f"main.{file_type or 'bin'}"

        dst.execute(
            """
            INSERT INTO FILES (project_id, file_name, file_type, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                project_id,
                main_file_name,
                file_type or "unknown",
                main_status,
            ),
        )

        if table_exists(src, "project_files"):
            project_files = src.execute(
                """
                SELECT *
                FROM project_files
                WHERE download_id=?
                """,
                (project_id,),
            ).fetchall()

            for pf in project_files:
                pf = dict(pf)
                pf_type = (pf.get("file_type") or "").lstrip(".") or "unknown"
                pf_name = pf.get("filename") or f"file-{pf.get('id', 'x')}.{pf_type}"
                pf_status = normalize_download_status(
                    pf.get("download_status"),
                    pf.get("failure_reason"),
                )

                dst.execute(
                    """
                    INSERT INTO FILES (project_id, file_name, file_type, status)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        project_id,
                        pf_name,
                        pf_type,
                        pf_status,
                    ),
                )

        keywords_raw = row.get("keywords") or row.get("keyword") or ""
        if keywords_raw:
            for kw in str(keywords_raw).split("||"):
                kw = kw.strip()
                if kw:
                    dst.execute(
                        "INSERT INTO KEYWORDS (project_id, keyword) VALUES (?, ?)",
                        (project_id, kw),
                    )

        for person_field, role in [
            ("uploader_name", "UPLOADER"),
            ("author_name", "AUTHOR"),
            ("owner_name", "OWNER"),
        ]:
            value = row.get(person_field)
            if value:
                names = [x.strip() for x in str(value).split("||") if x.strip()]
                for name in names:
                    dst.execute(
                        "INSERT INTO PERSON_ROLE (project_id, name, role) VALUES (?, ?, ?)",
                        (project_id, name, normalize_person_role(role)),
                    )

        license_text = normalize_license(row.get("license"))
        if license_text:
            dst.execute(
                "INSERT INTO LICENSES (project_id, license) VALUES (?, ?)",
                (project_id, license_text),
            )

    dst.commit()
    src.close()
    dst.close()

    print(f"Created submission DB: {TARGET_DB}")


if __name__ == "__main__":
    main()
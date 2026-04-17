import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SOURCE_DB = ROOT / "data" / "db" / "metadata.sqlite3"
TARGET_DB = ROOT / "23129118-seeding.db"

def create_schema(conn):
    conn.executescript("""
    DROP TABLE IF EXISTS PROJECTS;
    DROP TABLE IF EXISTS FILES;
    DROP TABLE IF EXISTS KEYWORDS;
    DROP TABLE IF EXISTS PERSON_ROLE;
    DROP TABLE IF EXISTS LICENSES;

    CREATE TABLE PROJECTS (
        id INTEGER PRIMARY KEY,
        query_string TEXT,
        repository_id INTEGER,
        repository_url TEXT,
        project_url TEXT,
        version TEXT,
        title TEXT,
        description TEXT,
        language TEXT,
        doi TEXT,
        upload_date TEXT,
        download_date TEXT,
        download_repository_folder TEXT,
        download_project_folder TEXT,
        download_version_folder TEXT,
        download_method TEXT
    );

    CREATE TABLE FILES (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        file_name TEXT,
        file_type TEXT,
        status TEXT
    );

    CREATE TABLE KEYWORDS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        keyword TEXT
    );

    CREATE TABLE PERSON_ROLE (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        name TEXT,
        role TEXT
    );

    CREATE TABLE LICENSES (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        license TEXT
    );
    """)

def main():
    src = sqlite3.connect(SOURCE_DB)
    src.row_factory = sqlite3.Row

    if TARGET_DB.exists():
        TARGET_DB.unlink()

    dst = sqlite3.connect(TARGET_DB)
    create_schema(dst)

    rows = src.execute("SELECT * FROM downloads").fetchall()

    for r in rows:
        r = dict(r)

        project_id = r["id"]

        repo_id = 6 if r["repository_key"] == "repo6" else 18
        repo_url = "https://dataverse.no/" if repo_id == 6 else "https://dataverse.harvard.edu/"

        dst.execute("""
        INSERT INTO PROJECTS VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            project_id,
            r.get("query_string"),
            repo_id,
            repo_url,
            r.get("source_url"),
            None,
            r.get("project_title") or "no title",
            r.get("description") or "",
            None,
            r.get("doi"),
            None,
            r.get("downloaded_at"),
            r.get("repository_key"),
            r.get("local_dir"),
            None,
            "API-CALL"
        ))

        status = "SUCCEEDED" if r.get("download_status") == "downloaded" else "FAILED_SERVER_UNRESPONSIVE"

        dst.execute("""
        INSERT INTO FILES (project_id, file_name, file_type, status)
        VALUES (?,?,?,?)
        """, (
            project_id,
            r.get("local_filename") or "file",
            r.get("file_type") or "unknown",
            status
        ))

        if r.get("license"):
            dst.execute("""
            INSERT INTO LICENSES (project_id, license)
            VALUES (?,?)
            """, (project_id, r["license"]))

    dst.commit()
    src.close()
    dst.close()

    print("NEW DB CREATED SUCCESSFULLY")

if __name__ == "__main__":
    main()
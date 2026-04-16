from __future__ import annotations

from dataclasses import asdict
from typing import Any
from urllib.parse import quote

import requests

from common import Candidate, slugify

TIMEOUT = 45
USER_AGENT = "QDArchiveStudentProject/1.0"

QDA_EXTENSIONS = {
    ".qdpx", ".qdpx", ".qdproj", ".qda", ".atlproj", ".atlasti", ".maxqda", ".mx22", ".nvpx",
    ".nvp", ".nvpX", ".qda-project", ".mqd", ".qrk", ".f4", ".f4analyse"
}

TEXT_LIKE_EXTENSIONS = {
    ".txt", ".doc", ".docx", ".rtf", ".odt", ".pdf", ".md", ".csv", ".tsv", ".xlsx", ".xls",
    ".json", ".xml", ".html", ".htm"
}


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json, text/html;q=0.9, */*;q=0.8"})
    return s


def _get_json(session: requests.Session, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    r = session.get(url, params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def _extract_fields(dataset_json: dict[str, Any]) -> dict[str, Any]:
    version = dataset_json.get("data", {}).get("latestVersion", {})
    metadata_blocks = version.get("metadataBlocks", {})
    citation_fields = metadata_blocks.get("citation", {}).get("fields", [])

    def get_field_value(type_name: str):
        for field in citation_fields:
            if field.get("typeName") == type_name:
                return field.get("value")
        return None

    def get_author_names() -> list[str]:
        value = get_field_value("author") or []
        names: list[str] = []
        for entry in value:
            for sub in entry.get("authorName", {}).get("value", []):
                if isinstance(sub, str):
                    names.append(sub)
            v = entry.get("authorName", {}).get("value")
            if isinstance(v, str):
                names.append(v)
        return names

    def get_keywords() -> str | None:
        value = get_field_value("keyword") or []
        items: list[str] = []
        for entry in value:
            kw = entry.get("keywordValue", {}).get("value")
            if isinstance(kw, str) and kw.strip():
                items.append(kw.strip())
        return "; ".join(items) if items else None

    desc_value = get_field_value("dsDescription") or []
    descriptions: list[str] = []
    for entry in desc_value:
        val = entry.get("dsDescriptionValue", {}).get("value")
        if isinstance(val, str) and val.strip():
            descriptions.append(val.strip())

    title = get_field_value("title") or dataset_json.get("data", {}).get("latestVersion", {}).get("metadataBlocks", {}).get("citation", {}).get("displayName") or "untitled-dataset"
    subject = get_field_value("subject")
    contact = get_field_value("datasetContact")
    uploader_name = None
    uploader_email = None
    if isinstance(contact, list) and contact:
        first = contact[0]
        name = first.get("datasetContactName", {}).get("value")
        email = first.get("datasetContactEmail", {}).get("value")
        if isinstance(name, str):
            uploader_name = name
        if isinstance(email, str):
            uploader_email = email

    publication_date = version.get("releaseTime") or version.get("createTime")
    year = None
    if isinstance(publication_date, str) and len(publication_date) >= 4:
        year = publication_date[:4]

    return {
        "title": title,
        "authors": get_author_names(),
        "keywords_original": get_keywords(),
        "description": "\n\n".join(descriptions) if descriptions else None,
        "uploader_name": uploader_name,
        "uploader_email": uploader_email,
        "year": year,
        "subject": subject,
        "version": version,
    }


def _file_extension(name: str | None) -> str | None:
    if not name or "." not in name:
        return None
    return "." + name.rsplit(".", 1)[1].lower()


def _score_file(filename: str) -> tuple[int, int]:
    ext = _file_extension(filename) or ""
    if ext in QDA_EXTENSIONS:
        return (0, len(filename))
    if ext in TEXT_LIKE_EXTENSIONS:
        return (1, len(filename))
    return (2, len(filename))


def _extract_files(repo: dict[str, Any], dataset_json: dict[str, Any]) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    version = dataset_json.get("data", {}).get("latestVersion", {})
    files = version.get("files", []) or []
    extracted: list[dict[str, Any]] = []
    for f in files:
        data_file = f.get("dataFile", {})
        file_id = data_file.get("id")
        filename = data_file.get("filename") or f.get("label") or "file.bin"
        restricted = bool(data_file.get("restricted", False))
        file_url = None
        if file_id is not None and not restricted:
            file_url = f"{repo['base_url'].rstrip('/')}/api/access/datafile/{file_id}"
        extracted.append(
            {
                "role": "data",
                "filename": filename,
                "file_type": _file_extension(filename),
                "source_url": file_url,
                "restricted": restricted,
                "filesize": data_file.get("filesize"),
                "description": data_file.get("description"),
            }
        )

    if not extracted:
        return None, []

    sorted_files = sorted(extracted, key=lambda x: _score_file(x["filename"]))
    main_file = sorted_files[0]
    associated = [f for f in extracted if f is not main_file]
    return main_file, associated


def discover_dataverse(repo: dict[str, Any], queries: list[str]) -> list[Candidate]:
    session = _session()
    server = repo["base_url"].rstrip("/")
    search_url = f"{server}/api/search"
    subtree = repo.get("dataverse_subtree")

    out: list[Candidate] = []
    seen: set[str] = set()

    for query in queries:
        params: dict[str, Any] = {
            "q": query,
            "type": "dataset",
            "per_page": 100,
            "sort": "date",
            "order": "desc",
        }
        if subtree:
            params["subtree"] = subtree

        try:
            search_json = _get_json(session, search_url, params=params)
        except Exception as e:
            out.append(
                Candidate(
                    repository_id=repo["repo_id"],
                    repository_key=repo["repo_key"],
                    repository_name=repo["repo_name"],
                    source_url=f"{search_url}?q={quote(query)}",
                    project_id=f"search-error-{slugify(query)}",
                    project_title=f"Search error for query {query}",
                    direct_download_url=None,
                    description=None,
                    file_type=None,
                    notes=f"Search API error: {e}",
                )
            )
            continue

        items = search_json.get("data", {}).get("items", [])
        for item in items:
            persistent_id = item.get("global_id")
            source_url = item.get("url")
            if not persistent_id or not source_url or source_url in seen:
                continue
            seen.add(source_url)

            dataset_api_url = f"{server}/api/datasets/:persistentId/"
            try:
                dataset_json = _get_json(session, dataset_api_url, params={"persistentId": persistent_id})
            except Exception as e:
                out.append(
                    Candidate(
                        repository_id=repo["repo_id"],
                        repository_key=repo["repo_key"],
                        repository_name=repo["repo_name"],
                        source_url=source_url,
                        project_id=slugify(item.get("name") or persistent_id),
                        project_title=item.get("name") or persistent_id,
                        direct_download_url=None,
                        doi=persistent_id,
                        description=None,
                        file_type=None,
                        notes=f"Dataset metadata fetch error: {e}",
                    )
                )
                continue

            fields = _extract_fields(dataset_json)
            main_file, associated_files = _extract_files(repo, dataset_json)
            main_url = main_file["source_url"] if main_file else None
            main_type = main_file["file_type"] if main_file else None

            version = fields["version"]
            terms = version.get("termsOfUse") or version.get("license")
            if isinstance(terms, dict):
                license_text = terms.get("name") or terms.get("uri") or str(terms)
            elif isinstance(terms, str):
                license_text = terms
            else:
                license_text = None

            notes: list[str] = [f"matched_query={query}"]
            if main_file and main_file.get("restricted"):
                notes.append("main_file_restricted=true")
            if not main_file:
                notes.append("no_files_listed=true")

            out.append(
                Candidate(
                    repository_id=repo["repo_id"],
                    repository_key=repo["repo_key"],
                    repository_name=repo["repo_name"],
                    source_url=source_url,
                    project_id=slugify(item.get("name") or persistent_id),
                    project_title=fields["title"] or item.get("name") or persistent_id,
                    direct_download_url=main_url,
                    doi=persistent_id,
                    license=license_text,
                    year=fields["year"],
                    description=fields["description"],
                    uploader_name=fields["uploader_name"],
                    uploader_email=fields["uploader_email"],
                    author_names=fields["authors"],
                    owner_names=[repo["repo_name"]],
                    keywords_original=fields["keywords_original"],
                    file_type=main_type,
                    associated_files=associated_files,
                    notes="; ".join(notes),
                )
            )

    return out

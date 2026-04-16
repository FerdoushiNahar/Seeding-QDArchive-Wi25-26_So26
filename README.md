# QDArchive Project for Repo #6 and Repo #18

This project is already configured for your two repositories:

- Repo 6: DataverseNO (`https://dataverse.no`)
- Repo 18: Henry A. Murray Research Archive, via its Harvard Dataverse collection (`subtree=mra` on `https://dataverse.harvard.edu`)

## Why this setup works

Both repositories are built on Dataverse or point to Dataverse collections, so you can use the official Dataverse Search API, Native API, and Data Access API to discover datasets, fetch metadata, and download public files.

## What the scripts do

1. `init_db.py` creates the SQLite database.
2. `discover_candidates.py` runs your search queries against both repositories.
3. `download_candidates.py` downloads the main file and also tries associated files.
4. `export_report.py` exports the database table as CSV.
5. `check_progress.py` shows counts by repository and status.

## Folder structure

```text
qdarchive_repos_18_6/
├── config/
│   ├── repositories.json
│   └── queries.txt
├── data/
│   ├── db/
│   ├── downloads/
│   │   ├── repo6/
│   │   └── repo18/
│   └── logs/
├── scripts/
│   ├── common.py
│   ├── dataverse_adapter.py
│   ├── init_db.py
│   ├── repo6_adapter.py
│   ├── repo18_adapter.py
│   ├── discover_candidates.py
│   ├── download_candidates.py
│   ├── export_report.py
│   └── check_progress.py
└── report_template.md
```

## Run order

```bash
python scripts/init_db.py
python scripts/discover_candidates.py
python scripts/check_progress.py
python scripts/download_candidates.py
python scripts/export_report.py
```

## Notes for your report

- DataverseNO is a national research data repository running on Dataverse.
- Murray points to a Dataverse collection hosted on Harvard Dataverse.
- Some files may be public, restricted, or missing direct download URLs.
- Your database captures these failures instead of silently skipping them.

## What to do after the first run

1. Open the exported CSV.
2. Check which queries returned useful qualitative projects.
3. Refine `config/queries.txt`.
4. Re-run discovery on a fresh database if needed.

## Good repository-specific search ideas

For DataverseNO:
- `qdpx`
- `"qualitative"`
- `"interview"`
- `"focus group"`
- `"textual data"`

For Murray:
- `interview`
- `oral history`
- `qualitative`
- `case study`
- `life history`

## Important limitation

This project is designed for public datasets and public files. If a dataset or file is restricted, the scripts record that status and reason, which is useful for the assignment.
"# Seeding-QDArchive-Wi25-26_So26" 

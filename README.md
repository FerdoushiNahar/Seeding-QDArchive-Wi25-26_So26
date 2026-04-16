# QDArchive Seeding – Part 1: Data Acquisition

**Student:** Ferdoushi Nahar
**Project:** SQ26 – Seeding QDArchive
**Semester:** Wi25/26 / So26

---

## 📌 Project Goal

This project implements **Part 1 (Data Acquisition)** of the QDArchive Seeding project.

The goal is to:

* discover qualitative research datasets from assigned repositories
* download publicly available files
* store metadata in a structured SQLite database
* record failed downloads (restricted, missing, etc.)
* prepare data for later cleaning and analysis

---

## 📚 Assigned Repositories

### Repo 6

* **Name:** DataverseNO
* **URL:** https://dataverse.no/

### Repo 18

* **Name:** Henry A. Murray Research Archive (Harvard Dataverse)
* **URL:** https://dataverse.harvard.edu/
* **Collection:** `mra`

---

## ⚙️ What This Project Does

This project:

1. Searches repositories using predefined queries
2. Discovers qualitative datasets
3. Extracts metadata using APIs
4. Stores all metadata in SQLite
5. Downloads accessible files
6. Logs failures for restricted or missing files
7. Exports results to CSV

---

## 📁 Repository Structure

```
Seeding-QDArchive-Wi25-26_So26/
├── config/
│   ├── repositories.json
│   └── queries.txt
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
├── data/
│   └── db/
│       ├── metadata.sqlite3
│       └── downloads_report.csv
├── tests/
├── README.md
├── report_template.md
├── requirements.txt
└── .gitignore
```

---

## 💾 Local Downloaded Data (Not on GitHub)

Downloaded files are stored locally:

```
data/downloads/
├── repo6/
└── repo18/
```

⚠️ These files are **NOT included in GitHub** due to size limits.

---

## 🔗 Data Access Links (FAUbox)

### Repo 6 Data

https://faubox.rrze.uni-erlangen.de/getlink/fi9k9TXhHuSto5kuAwEthZ/

### Repo 18 Data

https://faubox.rrze.uni-erlangen.de/getlink/fiERrJmS6SePC8hwJMC6oK/

---

## 🧠 Metadata Stored

The SQLite database contains:

* source URL
* repository name
* project title
* DOI
* description
* license
* uploader / author information
* keywords
* file type
* local file path
* download status
* failure reason
* checksum
* timestamp

---

## ▶️ How to Run

### 1. Create virtual environment

**Windows:**

```
python -m venv .venv
.venv\Scripts\activate
```

---

### 2. Install dependencies

```
pip install -r requirements.txt
```

---

### 3. Initialize database

```
python scripts/init_db.py
```

---

### 4. Discover datasets

```
python scripts/discover_candidates.py
```

---

### 5. Check progress

```
python scripts/check_progress.py
```

---

### 6. Download files

```
python scripts/download_candidates.py
```

---

### 7. Export CSV report

```
python scripts/export_report.py
```

---

## 📊 Outputs

* SQLite database → `data/db/metadata.sqlite3`
* CSV report → `data/db/downloads_report.csv`

---

## ⚠️ Challenges Encountered

* restricted files requiring login
* missing or incomplete metadata
* inconsistent keyword formatting
* unclear roles (author vs uploader vs owner)
* multiple versions of datasets
* lack of QDA-specific filtering

All data is stored **as-is** without modification.

---

## 📝 Notes

* Failed downloads are recorded, not ignored
* Metadata is preserved in raw form
* Designed for further processing in Part 2

---

## 📦 Submission Contents

This repository includes:

* source code
* configuration files
* SQLite database
* CSV export
* README and documentation

Large data files are hosted externally via FAUbox links.

---

## 📜 License

This project is for academic use as part of the SQ26 course.
All downloaded data remains under its original license.

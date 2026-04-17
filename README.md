# QDArchive Seeding – Part 1: Data Acquisition

**Student:** Ferdoushi Nahar
**Matriculation Number:** 23129118
**Project:** SQ26 – Seeding QDArchive
**Semester:** Wi25/26 / So26

---

## 📌 Project Goal

This project implements **Part 1 (Data Acquisition)** of the QDArchive Seeding project.

The goal is to:

* Discover qualitative research datasets
* Download QDA-related files
* Store all metadata in a structured SQLite database

---

## 🗂️ Assigned Repositories

* **Repo 6:** DataverseNO
  https://dataverse.no/

* **Repo 18:** Henry A. Murray Research Archive (Harvard Dataverse)
  https://dataverse.harvard.edu/

---

## 📦 Final Submission Database

```
23129118-seeding.db
```

This database:

* Contains all extracted metadata
* Follows the required schema
* Passes the official validation script with:

  ```
  10 passed, 0 warnings, 0 errors
  ```

---

## 📁 Project Structure

```
Seeding-QDArchive-Wi25-26_So26/
├── 23129118-seeding.db        ← FINAL SUBMISSION FILE
├── config/
├── scripts/
├── data/
│   └── db/
│       └── downloads_report.csv
├── README.md
├── report_template.md
├── requirements.txt
└── .gitignore
```

---

## 📂 Data Files (FAUbox)

Due to large size, downloaded data is stored externally:

* **Repo 6 Data:**
  https://faubox.rrze.uni-erlangen.de/getlink/fi9k9TXhHuSto5kuAwEthZ/

* **Repo 18 Data:**
  https://faubox.rrze.uni-erlangen.de/getlink/fiERrJmS6SePC8hwJMC6oK/

---

## ⚙️ How to Run the Project

### 1. Setup

```bash
git clone https://github.com/FerdoushiNahar/Seeding-QDArchive-Wi25-26_So26
cd Seeding-QDArchive-Wi25-26_So26

python -m venv .venv
.venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

---

### 2. Run Pipeline

```bash
python scripts/discover_candidates.py
python scripts/download_candidates.py
```

---

### 3. Check Progress

```bash
python scripts/check_progress.py
```

---

### 4. Export Report

```bash
python scripts/export_report.py
```

---

## 🔍 Queries Used

* `qdpx`
* `mqda`
* `nvp`
* `interview study`
* `qualitative research`
* `qualitative data`

These queries were used to maximize discovery of qualitative datasets.

---

## 🧠 Data Acquisition Approach

Two strategies were used:

* **API-based querying (Dataverse)**
* **Search-based discovery using keywords**

---

## ⚠️ Data Challenges

### 1. Missing Metadata

Many datasets lack complete fields (description, language, etc.).

### 2. Keyword Inconsistency

Keywords are often:

* comma-separated
* inconsistent formats

Stored as-is (no cleaning in Part 1).

### 3. Restricted Files

Some files require login → marked as failed.

### 4. Role Ambiguity

Difficult to distinguish:

* author
* uploader
* owner

### 5. Multiple Licenses

Some datasets contain multiple licenses.

---

## 📊 Output

* SQLite database with required schema
* CSV report of downloads
* Structured dataset folders (in FAUbox)

---

## ✅ Validation

Validated using official script:

```bash
python check_submission.py 23129118-seeding.db
```

Result:

```
10 passed, 0 warnings, 0 errors
```


## 📄 License

This project is for academic purposes as part of SQ26 at FAU Erlangen-Nürnberg.

All dataset licenses are preserved as recorded in the database.

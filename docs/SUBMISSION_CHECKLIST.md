# Hackathon Submission Checklist (PS-019)

Use this checklist to ensure all hackathon evaluation criteria and repository assets are 100% complete before final submission.

---

## 1. Required Repository Contents

Ensure each of the following files and folders exists in your repository:

- [x] **Source Code (`src/`)**:
  - `src/detectors/`: `verhoeff.py`, `govt_id.py` (Aadhaar & PAN), `email.py`, `phone.py`, `dob.py`, `name.py`, `base.py`
  - `src/scanner/`: `csv_scanner.py`, `db_scanner.py`, `runner.py`
  - `src/rules/`: `engine.py` (YAML parser and weighting engine)
  - `src/metadata/`: `gap_analyzer.py` (RoPA linkage and gap severity)
  - `src/evaluation/`: `metrics.py` (Precision, Recall, F1, Confusion Matrix, Error Analysis)
  - `src/db/`: `reviewer_db.py` (Persistent SQLite reviewer notes database)
- [x] **User Interface (`app/` & `app.py`)**:
  - `app.py`: Root entry point (Hugging Face Spaces compatible)
  - `app/styles.py`: Glassmorphism dark cyber theme CSS
  - `app/components.py`: Branded SVG logo, KPI tiles, custom Plotly charts
- [x] **Synthetic Datasets (`data/`)**:
  - `customers_messy.csv` (120 rows, misleading names like `contact_token`, nulls)
  - `employees_hr.csv` (120 rows, HR records, emergency contacts)
  - `transactions_logs.csv` (120 rows, decoy tracking numbers, decoy dates)
  - `kyc_onboarding.csv` (120 rows, Aadhaar Verhoeff checksums, PAN cards)
  - `support_tickets.csv` (120 rows, customer support tickets, agent names)
  - `enterprise_vault.db` (Multi-table SQLite database: `user_profiles`, `billing_accounts`, `activity_telemetry`, `vendor_registry`)
  - `metadata.csv` (Declared processing purposes and retention schedules with deliberate gaps)
  - `labels.csv` (Hand-labelled ground truth across all 68 schema columns)
  - `rules.yaml` (Configurable multi-signal weights and regex patterns)
- [x] **Test Suite (`tests/`)**:
  - 10 unit test files (`test_verhoeff.py`, `test_govt_id.py`, `test_email.py`, `test_phone.py`, `test_dob.py`, `test_name.py`, `test_rules.py`, `test_metadata.py`, `test_scanner.py`, `test_evaluation.py`)
  - `pytest.ini` configured
- [x] **Documentation (`docs/`, root)**:
  - `README.md` (Hugging Face YAML header, Mermaid architecture, quickstart, demo links)
  - `pseudocode.md` (Formal scanning and confidence scoring pseudocode)
  - `report.md` (Full academic / technical report formatted for PDF export)
  - `docs/DEPLOYMENT.md` (Step-by-step Hugging Face Spaces guide)
  - `docs/SUBMISSION_CHECKLIST.md` (This file)
  - `demo/README.md` (Offline demo fallback instructions)
  - `run_all.py` (Single-command CLI test & pipeline runner)
  - `requirements.txt` (Complete pinned dependencies)
  - `.gitignore` (Virtual environment and temporary files excluded)

---

## 2. Git Commands to Run for Submission

Follow these exact commands to push your project to your GitHub repository:

### Step 1: Check Git Status
```powershell
cd D:\privacy-inventory-scanner
git status
```

### Step 2: Stage and Commit All Files Locally
```powershell
git add .
git commit -m "feat: complete personal-data discovery and privacy evidence inventory engine (PS-019)"
```

### Step 3: Create GitHub Repository & Push
1. Open your browser and go to: **[https://github.com/new](https://github.com/new)**.
2. Repository name: `privacy-inventory-scanner`
3. Description: `Personal-Data Discovery and Privacy Evidence Inventory Engine (AIORI-3 / PS-019)`
4. Keep it **Public** and do NOT initialize with README or .gitignore (we already have them).
5. Click **Create repository**.
6. In your local PowerShell terminal, link and push:
```powershell
git branch -M main
git remote add origin https://github.com/<your-username>/privacy-inventory-scanner.git
git push -u origin main
```

---

## 3. Final Submission Links to Submit on Hackathon Portal

Copy and paste these exact links into the submission portal:
- [ ] **GitHub Repository Link**: `https://github.com/<your-username>/privacy-inventory-scanner`
- [ ] **Live Hosted Demo Link**: `https://huggingface.co/spaces/<your-username>/privacy-inventory-scanner`
- [ ] **Video Walkthrough (YouTube / Loom)**: `https://youtu.be/<your-video-id>`
- [ ] **Technical Report (PDF)**: Export `report.md` to PDF via VS Code / Typora / pandoc and upload to repo / portal
- [ ] **Presentation Slide Deck (PDF)**: Upload your slide deck to the portal

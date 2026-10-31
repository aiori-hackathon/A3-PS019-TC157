# Deployment Guide: Hugging Face Spaces & Local Demo

This beginner-friendly guide walks you through deploying **AEGIS Privacy Evidence Inventory** to **Hugging Face Spaces** (free hosting with a public live URL) and creating a local demo recording fallback.

---

## Part 1: Deploy to Hugging Face Spaces (Live Online Demo)

Hugging Face Spaces provides a free, fast cloud container for Streamlit applications.

### Step 1: Create an Account on Hugging Face
1. Open your browser and navigate to: **[https://huggingface.co/join](https://huggingface.co/join)**.
2. Sign up with your email, username, and password.
3. Verify your email address from your inbox.

### Step 2: Create a New Space
1. Click your profile avatar in the top-right corner of Hugging Face.
2. Click **New Space** (or navigate to [https://huggingface.co/new-space](https://huggingface.co/new-space)).
3. Fill out the form:
   - **Space name**: `privacy-inventory-scanner` (or `aegis-privacy-inventory`)
   - **License**: `mit` or `apache-2.0`
   - **Select the Space SDK**: Click **Streamlit**
   - **Space hardware**: Select **Free (CPU basic • 2 vCPU • 16GB)**
   - **Visibility**: Select **Public**
4. Click the blue button **Create Space**.

### Step 3: Upload the Project Files
You can upload directly via the web browser:
1. Inside your newly created Space, click the **Files** tab (next to App).
2. Click the **Add file** dropdown button and select **Upload files**.
3. Drag and drop (or select) all the files from `D:\privacy-inventory-scanner`:
   - `app.py`
   - `requirements.txt`
   - `README.md`
   - `rules.yaml`
   - Entire `app/` folder (with `app.py`, `styles.py`, `components.py`)
   - Entire `src/` folder (with `detectors/`, `scanner/`, `rules/`, `metadata/`, `evaluation/`, `db/`)
   - Entire `data/` folder (with all CSVs, `enterprise_vault.db`, `metadata.csv`, `labels.csv`, `rules.yaml`)
   *(Note: Do NOT upload `.venv/`, `.git/`, or `pip-cache/`)*
4. Scroll to the bottom and click **Commit changes to main**.

### Step 4: Verify the Build and Find the Live URL
1. Click on the **App** tab.
2. You will see a banner saying *"Building..."* (takes about 1-2 minutes while pip installs requirements).
3. Once the build finishes, the status changes to *"Running"* and your dark-cyber Streamlit dashboard will appear live!
4. **Copy your Live URL**:
   - The public URL is in your browser address bar: `https://huggingface.co/spaces/<your-username>/<your-space-name>`
   - Alternatively, click the three vertical dots (`...`) in the top right of the Space and click **Embed this Space** or **Direct URL**.
5. Open `README.md` and update the link:
   ```markdown
   **Live Demo:** [https://huggingface.co/spaces/<your-username>/privacy-inventory-scanner](https://huggingface.co/spaces/<your-username>/privacy-inventory-scanner)
   ```

---

## Part 2: Fallback Demo (Screenshots & Screen Recording)

If internet or cloud hosting is unavailable during judge evaluation, submit the offline demo folder:

### Step 1: Run the App Locally
Open PowerShell on your computer and run:
```powershell
cd D:\privacy-inventory-scanner
& "D:\privacy-inventory-scanner\.venv\Scripts\streamlit.exe" run app.py
```
This opens the web browser automatically at `http://localhost:8501`.

### Step 2: Capture Screenshots for `/demo` Folder
Take high-resolution screenshots of these 5 key screens and save them inside `demo/`:
1. `overview_dashboard.png`: Executive dashboard with KPI tiles and donut chart.
2. `inventory_table.png`: Filtered inventory table showing confidence badges and compliance chips.
3. `field_detail_evidence.png`: Deep dive showing the 3-signal breakdown, Verhoeff validator, and masked samples.
4. `gap_report.png`: Prioritized compliance gap cards with remediation guidance.
5. `evaluation_benchmark.png`: Precision/Recall bar chart, confusion matrix, and honest error analysis.

*(On Windows, use **Windows Key + Shift + S** to capture screens).*

### Step 3: Record a 2-Minute Screen Video
1. Use Windows built-in screen recorder (**Windows Key + Alt + R**) or OBS Studio.
2. Follow the 2-minute script in the main README / final summary.
3. Save the MP4 video inside `demo/demo_walkthrough.mp4` or upload to YouTube (unlisted) and paste the link in `README.md`.

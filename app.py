"""Main entry point for the Streamlit app (works locally and on Hugging Face Spaces)."""

import os
import runpy
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# runpy executes the page file fresh on every Streamlit rerun,
# unlike "import", which only runs once.
runpy.run_path(os.path.join(ROOT, "app", "app.py"), run_name="__main__")
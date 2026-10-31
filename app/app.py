"""AEGIS Privacy Discovery & Evidence Inventory - Main Streamlit Application."""

import ast
import glob
import json
import os
import sys
import pandas as pd
import streamlit as st

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.components import (
    render_compliance_gauge,
    render_confidence_badge,
    render_confusion_matrix_heatmap,
    render_data_class_donut,
    render_disclaimer_banner,
    render_gap_chip,
    render_hero_header,
    render_metric_card,
    render_precision_recall_chart,
    render_table_heatmap,
)
from app.styles import get_cyber_css
from src.db.reviewer_db import ReviewerDatabase
from src.evaluation.metrics import EvaluationEngine
from src.metadata.gap_analyzer import MetadataRegistry
from src.rules.engine import RuleConfig
from src.scanner.runner import ScannerEngine

# Page Configuration
st.set_page_config(
    page_title="AEGIS | Privacy Evidence Inventory",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Cyber Design Theme
st.markdown(get_cyber_css(), unsafe_allow_html=True)

# File Paths
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RULES_PATH = os.path.join(PROJECT_ROOT, "rules.yaml") if os.path.exists(os.path.join(PROJECT_ROOT, "rules.yaml")) else os.path.join(DATA_DIR, "rules.yaml")
METADATA_PATH = os.path.join(DATA_DIR, "metadata.csv")
LABELS_PATH = os.path.join(DATA_DIR, "labels.csv")
INVENTORY_CSV = os.path.join(DATA_DIR, "inventory_latest.csv")
REVIEWER_DB_PATH = os.path.join(DATA_DIR, "reviewer_notes.db")


# Cached data loader
@st.cache_data(show_spinner=False)
def load_or_run_inventory():
    if os.path.exists(INVENTORY_CSV):
        return pd.read_csv(INVENTORY_CSV)
    
    # Run scan if not yet generated
    rule_config = RuleConfig(RULES_PATH)
    meta_registry = MetadataRegistry(METADATA_PATH)
    engine = ScannerEngine(rule_config, meta_registry)
    csv_files = [f for f in glob.glob(os.path.join(DATA_DIR, "*.csv")) if not f.endswith(("metadata.csv", "labels.csv", "inventory_latest.csv"))]
    db_files = [f for f in glob.glob(os.path.join(DATA_DIR, "*.db")) if not f.endswith("reviewer_notes.db")]
    results = engine.scan_all(csv_files, db_files)
    df = pd.DataFrame(results)
    df.to_csv(INVENTORY_CSV, index=False)
    return df


@st.cache_data(show_spinner=False)
def load_evaluation(df_inventory: pd.DataFrame):
    if not os.path.exists(LABELS_PATH):
        return None
    eval_engine = EvaluationEngine(LABELS_PATH)
    results_list = df_inventory.to_dict(orient="records")
    return eval_engine.evaluate(results_list)


# Initialize State
if "scan_completed" not in st.session_state:
    st.session_state.scan_completed = False

# Sidebar Navigation
st.sidebar.markdown(
    """
    <div style="padding: 0.5rem 0 1.2rem 0; border-bottom: 1px solid rgba(0, 242, 254, 0.18); margin-bottom: 1rem;">
        <div style="font-size: 1.15rem; font-weight: 800; color: #00f2fe; letter-spacing: 0.05em;">
            🛡️ AEGIS PRIVACY
        </div>
        <div style="font-size: 0.75rem; color: #94a3b8;">
            v1.0.0 • AIORI-3 PS-019
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

nav_page = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Overview",
        "⚡ Run Scan",
        "🗃️ Inventory",
        "🔍 Field Detail",
        "⚠️ Gap Report",
        "⚙️ Rules Viewer",
        "📈 Evaluation & Benchmark",
        "📝 Reviewer Notes",
        "📥 Export",
    ],
    index=0,
)

st.sidebar.markdown(
    """
    <div style="margin-top: 2rem; padding: 1rem; background: rgba(15,23,42,0.6); border: 1px solid rgba(0,242,254,0.15); border-radius: 10px; font-size: 0.78rem; color: #94a3b8;">
        <strong style="color: #00f2fe;">Privacy Directive:</strong><br>
        • Verhoeff Checksum (Aadhaar)<br>
        • Structural PAN Verification<br>
        • DoT Cellular Series (Phone)<br>
        • Demographic Age Plausibility<br>
        • Technical Evidence Isolation
    </div>
    """,
    unsafe_allow_html=True,
)

# Load current inventory
df_inv = load_or_run_inventory()
eval_summary = load_evaluation(df_inv)

# Render Branded Header
render_hero_header()
render_disclaimer_banner()


# ==============================================================================
# PAGE 1: OVERVIEW
# ==============================================================================
if nav_page == "📊 Overview":
    st.markdown("### Executive Privacy Discovery Dashboard")
    
    # Compute Top Metrics
    total_fields = len(df_inv)
    pii_records = df_inv[df_inv["is_pii"] == True]
    total_pii = len(pii_records)
    
    crit_gaps = len(pii_records[pii_records["gap_severity"] == "Critical Gap"])
    compliant = len(pii_records[pii_records["gap_severity"] == "Declared"])
    completeness_pct = (compliant / total_pii * 100) if total_pii > 0 else 0.0
    
    macro_f1 = eval_summary["macro_avg"]["F1-Score"] * 100 if eval_summary else 0.0
    macro_rec = eval_summary["macro_avg"]["Recall"] * 100 if eval_summary else 0.0

    # Top KPI Cards
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(render_metric_card("Profiled Columns", str(total_fields), "5 CSVs + 1 Multi-table DB"), unsafe_allow_html=True)
    with c2:
        st.markdown(render_metric_card("Candidate PII", str(total_pii), f"{round(total_pii/total_fields*100,1)}% of total schema"), unsafe_allow_html=True)
    with c3:
        st.markdown(render_metric_card("Compliant RoPA", str(compliant), "Declared purpose & retention"), unsafe_allow_html=True)
    with c4:
        st.markdown(render_metric_card("Critical Gaps", str(crit_gaps), "Missing purpose & retention", delta="Action Req"), unsafe_allow_html=True)
    with c5:
        st.markdown(render_metric_card("Benchmark F1", f"{round(macro_f1, 1)}%", f"Recall: {round(macro_rec,1)}%"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Visuals Row
    v1, v2 = st.columns([1, 1])
    with v1:
        st.plotly_chart(render_data_class_donut(df_inv), use_container_width=True)
    with v2:
        st.plotly_chart(render_compliance_gauge(completeness_pct), use_container_width=True)

    st.plotly_chart(render_table_heatmap(df_inv), use_container_width=True)


# ==============================================================================
# PAGE 2: RUN SCAN
# ==============================================================================
elif nav_page == "⚡ Run Scan":
    st.markdown("### Interactive Privacy Scanner Orchestrator")
    st.markdown("Initiate discovery across target synthetic CSV datasets and the SQLite database vault.")

    col_cfg1, col_cfg2 = st.columns([2, 1])
    with col_cfg1:
        st.markdown("#### Target Data Repositories")
        all_csvs = [f for f in glob.glob(os.path.join(DATA_DIR, "*.csv")) if not f.endswith(("metadata.csv", "labels.csv", "inventory_latest.csv"))]
        all_dbs = [f for f in glob.glob(os.path.join(DATA_DIR, "*.db")) if not f.endswith("reviewer_notes.db")]

        selected_csvs = []
        for csv_path in all_csvs:
            fname = os.path.basename(csv_path)
            if st.checkbox(f"📄 {fname}", value=True, key=f"csv_{fname}"):
                selected_csvs.append(csv_path)

        selected_dbs = []
        for db_path in all_dbs:
            dname = os.path.basename(db_path)
            if st.checkbox(f"🗄️ {dname} (multi-table vault)", value=True, key=f"db_{dname}"):
                selected_dbs.append(db_path)

    with col_cfg2:
        st.markdown("#### Scanner Parameters")
        sample_size = st.slider("Sample Profile Size (rows)", min_value=100, max_value=2000, value=500, step=100)
        st.info("Scanner evaluates regex value-matching, Verhoeff checksums, and metadata compliance linkage.")

    if st.button("🚀 INITIATE AUTONOMOUS SCAN", use_container_width=True):
        progress_bar = st.progress(0.0)
        status_text = st.empty()

        rule_config = RuleConfig(RULES_PATH)
        meta_registry = MetadataRegistry(METADATA_PATH)
        engine = ScannerEngine(rule_config, meta_registry, sample_size=sample_size)

        def update_progress(pct, msg):
            progress_bar.progress(pct)
            status_text.markdown(f"<span style='color: #00f2fe;'>⚙️ {msg}</span>", unsafe_allow_html=True)

        results = engine.scan_all(selected_csvs, selected_dbs, progress_callback=update_progress)
        df_new = pd.DataFrame(results)
        df_new.to_csv(INVENTORY_CSV, index=False)
        st.cache_data.clear()

        status_text.markdown("<span style='color: #34d399; font-weight: 600;'>✓ Scan Complete! Inventory persisted.</span>", unsafe_allow_html=True)
        st.success(f"Profiled {len(df_new)} columns across {len(selected_csvs)} CSVs and {len(selected_dbs)} DBs. Discovered {len(df_new[df_new['is_pii']==True])} candidate personal data fields!")


# ==============================================================================
# PAGE 3: INVENTORY
# ==============================================================================
elif nav_page == "🗃️ Inventory":
    st.markdown("### Discovered Personal-Data Evidence Inventory")
    
    # Filter Controls
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        classes = ["All"] + sorted(list(df_inv["detected_class"].unique()))
        sel_class = st.selectbox("Filter by Data Class", classes)
    with f2:
        tiers = ["All", "High", "Medium", "Low", "None"]
        sel_tier = st.selectbox("Filter by Confidence Tier", tiers)
    with f3:
        tables = ["All"] + sorted(list(df_inv["table_name"].unique()))
        sel_table = st.selectbox("Filter by Dataset / Table", tables)
    with f4:
        gaps = ["All"] + sorted(list(df_inv["gap_severity"].unique()))
        sel_gap = st.selectbox("Filter by Compliance Gap", gaps)

    search_query = st.text_input("🔍 Search by Column or Table Name", "")

    # Apply Filters
    df_filtered = df_inv.copy()
    if sel_class != "All":
        df_filtered = df_filtered[df_filtered["detected_class"] == sel_class]
    if sel_tier != "All":
        df_filtered = df_filtered[df_filtered["confidence_tier"] == sel_tier]
    if sel_table != "All":
        df_filtered = df_filtered[df_filtered["table_name"] == sel_table]
    if sel_gap != "All":
        df_filtered = df_filtered[df_filtered["gap_severity"] == sel_gap]
    if search_query:
        q = search_query.lower()
        df_filtered = df_filtered[
            df_filtered["column_name"].str.lower().str.contains(q)
            | df_filtered["table_name"].str.lower().str.contains(q)
        ]

    st.markdown(f"**Showing {len(df_filtered)} of {len(df_inv)} schema fields**")

    # Display styled table
    display_df = df_filtered[[
        "dataset_name", "table_name", "column_name", "detected_class",
        "confidence_tier", "confidence_score", "declared_purpose",
        "retention_period", "gap_severity", "legal_notes"
    ]].copy()

    display_df["confidence_score"] = (display_df["confidence_score"] * 100).round(1).astype(str) + "%"
    display_df["legal_notes"] = display_df["legal_notes"].fillna("")

    st.dataframe(
        display_df,
        column_config={
            "dataset_name": "Dataset Source",
            "table_name": "Table",
            "column_name": "Column Name",
            "detected_class": "Detected Class",
            "confidence_tier": "Tier",
            "confidence_score": "Confidence",
            "declared_purpose": "Declared Purpose",
            "retention_period": "Retention Schedule",
            "gap_severity": "Compliance Status",
            "legal_notes": "Legal Notes (Human Reviewer)",
        },
        use_container_width=True,
        height=520,
    )


# ==============================================================================
# PAGE 4: FIELD DETAIL (EVIDENCE TRAIL)
# ==============================================================================
elif nav_page == "🔍 Field Detail":
    st.markdown("### Technical Evidence Trail Deep Dive")
    st.markdown("Inspect granular mathematical confidence scores, algorithmic verification, and masked previews.")

    # Field Selector
    field_options = [f"{row['table_name']} -> {row['column_name']} ({row['detected_class']})" for _, row in df_inv.iterrows()]
    sel_idx = st.selectbox("Select Target Field to Inspect", range(len(field_options)), format_func=lambda x: field_options[x])
    field_data = df_inv.iloc[sel_idx]

    # Header Card
    st.markdown(
        f"""
        <div class="cyber-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <div>
                    <span class="mono-token">{field_data['dataset_name']}</span> &nbsp;❯&nbsp; 
                    <span class="mono-token">{field_data['table_name']}</span> &nbsp;❯&nbsp; 
                    <span style="font-size: 1.25rem; font-weight: 700; color: #00f2fe;">{field_data['column_name']}</span>
                </div>
                <div>
                    {render_confidence_badge(field_data['confidence_score'], field_data['confidence_tier'])}
                    &nbsp; {render_gap_chip(field_data['gap_severity'])}
                </div>
            </div>
            <div style="font-size: 0.9rem; color: #94a3b8;">
                Classification: <strong style="color: #f8fafc;">{field_data['detected_class']}</strong> • 
                Candidate PII: <strong style="color: {'#34d399' if field_data['is_pii'] else '#94a3b8'};">{'YES' if field_data['is_pii'] else 'NO'}</strong> • 
                Total Profiled Rows: <strong>{field_data['total_rows']}</strong> • 
                Null Ratio: <strong>{round(field_data['null_ratio']*100, 1)}%</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3-Score Signal Breakdown
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Signal 1: Column Match</div>
                <div class="metric-value">{round(field_data['column_score']*100, 1)}%</div>
                <div class="metric-subtext">Rule: <span class="mono-token">{field_data['column_rule_matched']}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Signal 2: Value Pattern</div>
                <div class="metric-value">{round(field_data['value_pattern_score']*100, 1)}%</div>
                <div class="metric-subtext">Pattern: {field_data['pattern_rule_matched']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Signal 3: Algorithmic Verification</div>
                <div class="metric-value">{round(field_data['validation_score']*100, 1)}%</div>
                <div class="metric-subtext">Algorithm: {field_data['validator_used']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Evidence Steps & Masked Samples
    e1, e2 = st.columns([3, 2])
    with e1:
        st.markdown("#### Detailed Technical Evidence Steps")
        steps = ast.literal_eval(field_data["evidence_steps"]) if isinstance(field_data["evidence_steps"], str) and field_data["evidence_steps"].startswith("[") else [str(field_data["evidence_steps"])]
        for step in steps:
            st.markdown(f"• {step}")

    with e2:
        st.markdown("#### Masked Sample Previews")
        samples_raw = field_data["masked_samples"]
        try:
            samples = ast.literal_eval(samples_raw) if isinstance(samples_raw, str) and samples_raw.startswith("[") else [str(samples_raw)]
        except Exception:
            samples = []
        if samples and samples != [[]] and samples != [""]:
            for sample in samples:
                if sample:
                    st.markdown(f"<span class='mono-token' style='display: block; margin-bottom: 0.4rem;'>{sample}</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color: #64748b;'>No values available in sample.</span>", unsafe_allow_html=True)

    # RoPA Metadata linkage
    st.markdown("#### Privacy Compliance & RoPA Linkage")
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"**Declared Processing Purpose:** `{field_data['declared_purpose']}`")
        st.markdown(f"**Retention Schedule:** `{field_data['retention_period']}`")
    with m2:
        st.markdown(f"**Compliance Status:** {render_gap_chip(field_data['gap_severity'])}", unsafe_allow_html=True)
        st.markdown(f"**Remediation Guidance:** {field_data['remediation_guidance']}")


# ==============================================================================
# PAGE 5: GAP REPORT
# ==============================================================================
elif nav_page == "⚠️ Gap Report":
    st.markdown("### Privacy Compliance Gap & Remediation Report")
    st.markdown("Actionable gap analysis cross-referencing discovered Personal Data candidates against registered purposes in `metadata.csv`.")

    pii_df = df_inv[df_inv["is_pii"] == True].copy()
    gaps_df = pii_df[pii_df["gap_severity"] != "Declared"].copy()

    g1, g2, g3 = st.columns(3)
    with g1:
        crit_count = len(gaps_df[gaps_df["gap_severity"] == "Critical Gap"])
        st.markdown(render_metric_card("Critical Gaps", str(crit_count), "Missing purpose AND retention", delta="Immediate Action"), unsafe_allow_html=True)
    with g2:
        high_count = len(gaps_df[gaps_df["gap_severity"] == "High Gap"])
        st.markdown(render_metric_card("High Gaps", str(high_count), "Missing processing purpose"), unsafe_allow_html=True)
    with g3:
        med_count = len(gaps_df[gaps_df["gap_severity"] == "Medium Gap"])
        st.markdown(render_metric_card("Medium Gaps", str(med_count), "Missing retention schedule"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not gaps_df.empty:
        st.markdown("#### Prioritized Compliance Action Items")
        for _, row in gaps_df.iterrows():
            severity = row["gap_severity"]
            card_border = "#f43f5e" if severity == "Critical Gap" else ("#fb923c" if severity == "High Gap" else "#facc15")
            st.markdown(
                f"""
                <div style="background: rgba(16, 24, 40, 0.7); border: 1px solid rgba(0,242,254,0.15); border-left: 4px solid {card_border}; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 0.8rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; color: #f8fafc; font-size: 1.05rem;">{row['table_name']}.{row['column_name']}</span>
                        {render_gap_chip(severity)}
                    </div>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin: 0.35rem 0;">
                        Detected Class: <strong style="color: #00f2fe;">{row['detected_class']}</strong> • 
                        Confidence: <strong>{round(row['confidence_score']*100, 1)}% ({row['confidence_tier']})</strong>
                    </div>
                    <div style="font-size: 0.84rem; color: #cbd5e1; background: rgba(0,0,0,0.25); padding: 0.5rem 0.75rem; border-radius: 6px; margin-top: 0.4rem;">
                        <strong>Action Guidance:</strong> {row['remediation_guidance']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.success("All discovered Personal Data fields have declared purpose and retention schedules registered!")


# ==============================================================================
# PAGE 6: RULES VIEWER
# ==============================================================================
elif nav_page == "⚙️ Rules Viewer":
    st.markdown("### Configurable Discovery Rules & Heuristics Viewer")
    st.markdown("Detection heuristics, signal weights, and exclusion patterns loaded from `rules.yaml`.")

    rule_cfg = RuleConfig(RULES_PATH)

    r1, r2 = st.columns([1, 1])
    with r1:
        st.markdown("#### Active Multi-Signal Weighting")
        st.json(rule_cfg.weights)
        st.markdown("#### Confidence Tiers Thresholds")
        st.json(rule_cfg.thresholds)

    with r2:
        st.markdown("#### Interactive Pattern Tester")
        test_col = st.text_input("Test Column Header", "emp_aadhaar_no")
        test_val = st.text_input("Test Sample Value", "4567 8901 2345")
        
        if st.button("Evaluate Test String"):
            engine = ScannerEngine(rule_cfg)
            res = engine.scan_column(test_col, [test_val], "test_dataset", "test_table")
            st.markdown(
                f"""
                <div class="cyber-card">
                    <div>Detected Class: <strong style="color: #00f2fe;">{res['detected_class']}</strong></div>
                    <div>Confidence: <strong>{round(res['confidence_score']*100, 1)}% ({res['confidence_tier']})</strong></div>
                    <div>Candidate PII: <strong>{'YES' if res['is_pii'] else 'NO'}</strong></div>
                    <div style="margin-top: 0.5rem; font-size: 0.82rem; color: #94a3b8;">
                        • Column Score: {res['column_score']}<br>
                        • Value Pattern Score: {res['value_pattern_score']}<br>
                        • Algorithmic Validation: {res['validation_score']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("#### Full `rules.yaml` Configuration")
    st.code(rule_cfg.to_yaml_string(), language="yaml")


# ==============================================================================
# PAGE 7: EVALUATION & BENCHMARK
# ==============================================================================
elif nav_page == "📈 Evaluation & Benchmark":
    st.markdown("### Benchmark Evaluation Against Ground Truth (`labels.csv`)")
    st.markdown("Per-class Precision, Recall, F1-Score, Confusion Matrix, and Transparent Error Analysis.")

    if eval_summary and not eval_summary["per_class"].empty:
        # Macro KPIs
        macro = eval_summary["macro_avg"]
        binary = eval_summary["binary_metrics"]

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(render_metric_card("Macro Precision", f"{round(macro['Precision']*100, 1)}%", "Across 5 PII classes"), unsafe_allow_html=True)
        with k2:
            st.markdown(render_metric_card("Macro Recall", f"{round(macro['Recall']*100, 1)}%", "Sensitivity on ground truth"), unsafe_allow_html=True)
        with k3:
            st.markdown(render_metric_card("Macro F1-Score", f"{round(macro['F1-Score']*100, 1)}%", "Harmonic mean of P & R"), unsafe_allow_html=True)
        with k4:
            st.markdown(render_metric_card("Binary PII Accuracy", f"{round(binary['Accuracy']*100, 1)}%", f"TP: {binary['TP']} | TN: {binary['TN']}"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Plotly Visuals
        p1, p2 = st.columns([3, 2])
        with p1:
            st.plotly_chart(render_precision_recall_chart(eval_summary["per_class"]), use_container_width=True)
        with p2:
            st.plotly_chart(render_confusion_matrix_heatmap(eval_summary["confusion_matrix"]), use_container_width=True)

        # Tabular Per-Class Table
        st.markdown("#### Detailed Metric Table")
        st.dataframe(eval_summary["per_class"], use_container_width=True)

        # Honest Error Analysis View
        st.markdown("---")
        st.markdown("### 🔎 Honest Error Analysis (False Alarms & Misses)")
        st.markdown(
            "In real-world data discovery, perfect accuracy is unrealistic. "
            "Below is a transparent analysis of borderlines, decoys, and false classifications."
        )

        tab_fp, tab_fn = st.tabs(["False Alarms (False Positives)", "Misses (False Negatives)"])

        with tab_fp:
            fps = eval_summary["false_positives"]
            if fps:
                st.markdown(f"**Found {len(fps)} False Alarms:**")
                for err in fps:
                    st.markdown(
                        f"""
                        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 0.85rem; margin-bottom: 0.6rem;">
                            <strong>{err['table_name']}.{err['column_name']}</strong> — 
                            Predicted as <span style="color: #00f2fe;">{err['predicted_class']} ({err['confidence_tier']})</span> 
                            but Ground Truth is <span style="color: #f87171;">{err['ground_truth_class']}</span>.<br>
                            <span style="font-size: 0.8rem; color: #94a3b8;">Ground Truth Note: {err['note']}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No false positives identified.")

        with tab_fn:
            fns = eval_summary["false_negatives"]
            if fns:
                st.markdown(f"**Found {len(fns)} Misses:**")
                for err in fns:
                    st.markdown(
                        f"""
                        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 0.85rem; margin-bottom: 0.6rem;">
                            <strong>{err['table_name']}.{err['column_name']}</strong> — 
                            Ground Truth is <span style="color: #34d399;">{err['ground_truth_class']}</span> 
                            but detector scored as Non-PII.<br>
                            <span style="font-size: 0.8rem; color: #94a3b8;">Ground Truth Note: {err['note']}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No false negatives identified! Recall is 100%.")


# ==============================================================================
# PAGE 8: REVIEWER NOTES (SQLITE DB PERSISTENCE)
# ==============================================================================
elif nav_page == "📝 Reviewer Notes":
    st.markdown("### Human Privacy Reviewer & Legal Counsel Workbench")
    st.markdown(
        "Preserving statutory segregation: Technical scanner provides evidence; "
        "human DPO records verification status, lawful processing basis, and retention approvals directly into SQLite."
    )

    db = ReviewerDatabase(REVIEWER_DB_PATH)

    # Field Selection
    field_labels = [f"{row['table_name']}.{row['column_name']} ({row['detected_class']})" for _, row in df_inv.iterrows()]
    sel_idx = st.selectbox("Select Target Field to Audit", range(len(field_labels)), format_func=lambda x: field_labels[x])
    field_rec = df_inv.iloc[sel_idx]

    # Pre-fill with existing note if present
    existing = db.get_note(field_rec["dataset_name"], field_rec["table_name"], field_rec["column_name"])

    rn1, rn2 = st.columns(2)
    with rn1:
        st.markdown(f"**Dataset:** `{field_rec['dataset_name']}`")
        st.markdown(f"**Table:** `{field_rec['table_name']}`")
        st.markdown(f"**Column:** `{field_rec['column_name']}`")
        st.markdown(f"**Technical Classification:** `{field_rec['detected_class']}` ({field_rec['confidence_tier']})")

    with rn2:
        status_options = ["Unreviewed", "Confirmed PII", "False Alarm (Non-PII)", "Needs Clarification", "De-Identified Token"]
        curr_status = existing["verification_status"] if existing else "Unreviewed"
        sel_status = st.selectbox("Verification Status", status_options, index=status_options.index(curr_status) if curr_status in status_options else 0)

        risk_options = ["Unassessed", "High Privacy Risk", "Medium Privacy Risk", "Low Privacy Risk", "Statutory Exemption"]
        curr_risk = existing["risk_assessment"] if existing else "Unassessed"
        sel_risk = st.selectbox("Legal Risk Assessment", risk_options, index=risk_options.index(curr_risk) if curr_risk in risk_options else 0)

    lawful_basis = st.text_area(
        "Lawful Basis Determination (Human Legal Reviewer)",
        value=existing["lawful_basis_note"] if existing else "",
        placeholder="e.g. DPDP Act 2023 Sec 6 Consent / GDPR Art 6(1)(b) Contractual Performance...",
        help="Kept strictly separate from automated technical detection.",
    )

    r_col1, r_col2 = st.columns(2)
    with r_col1:
        ret_options = ["Pending Review", "Approved - Compliant", "Excessive - Purge Required", "Action Item: Set Schedule"]
        curr_ret = existing["retention_approval"] if existing else "Pending Review"
        sel_ret = st.selectbox("Retention Schedule Approval", ret_options, index=ret_options.index(curr_ret) if curr_ret in ret_options else 0)
    with r_col2:
        reviewer = st.text_input("Reviewer Identity", value=existing["reviewer_identity"] if existing else "Senior Privacy Counsel")

    if st.button("💾 SAVE AUDIT NOTE TO DATABASE", use_container_width=True):
        db.save_note(
            dataset_name=field_rec["dataset_name"],
            table_name=field_rec["table_name"],
            column_name=field_rec["column_name"],
            data_class=field_rec["detected_class"],
            verification_status=sel_status,
            lawful_basis_note=lawful_basis,
            risk_assessment=sel_risk,
            retention_approval=sel_ret,
            reviewer_identity=reviewer,
        )
        st.success("Reviewer notes and lawful basis assessment successfully persisted to SQLite database!")

    # Table of Audit Notes
    st.markdown("#### Persisted Reviewer Audit Trail")
    all_notes = db.get_all_notes()
    if all_notes:
        df_notes = pd.DataFrame(all_notes)
        st.dataframe(df_notes, use_container_width=True)
    else:
        st.info("No audit notes recorded yet. Select a field above to save legal reviewer observations.")


# ==============================================================================
# PAGE 9: EXPORT
# ==============================================================================
elif nav_page == "📥 Export":
    st.markdown("### Export Inventory, Gap Reports & Benchmark Results")
    st.markdown("Download generated evidence inventory and compliance audit summaries.")

    e1, e2 = st.columns(2)
    with e1:
        st.markdown("#### Complete Evidence Inventory (CSV)")
        csv_bytes = df_inv.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Inventory (CSV)",
            data=csv_bytes,
            file_name="privacy_evidence_inventory.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.markdown("#### Compliance Gap Audit List (CSV)")
        gaps_export = df_inv[df_inv["gap_severity"].isin(["Critical Gap", "High Gap", "Medium Gap"])]
        gaps_bytes = gaps_export.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Gap Report (CSV)",
            data=gaps_bytes,
            file_name="compliance_gaps_audit.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with e2:
        st.markdown("#### Complete Evidence Inventory (JSON)")
        json_str = df_inv.to_json(orient="records", indent=2)
        st.download_button(
            label="📥 Download Inventory (JSON)",
            data=json_str,
            file_name="privacy_evidence_inventory.json",
            mime="application/json",
            use_container_width=True,
        )

        if eval_summary and not eval_summary["per_class"].empty:
            st.markdown("#### Benchmark Evaluation Metrics (CSV)")
            eval_bytes = eval_summary["per_class"].to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Benchmark Metrics (CSV)",
                data=eval_bytes,
                file_name="benchmark_metrics.csv",
                mime="text/csv",
                use_container_width=True,
            )

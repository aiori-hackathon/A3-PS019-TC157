"""CLI Pipeline Runner for Personal-Data Discovery & Privacy Inventory Scanner.

Executes end-to-end scanning across 5 synthetic CSVs and 1 SQLite database,
computes transparent confidence scores, links compliance metadata, evaluates
precision/recall against ground-truth labels, and outputs summary statistics.
"""

import glob
import os
import sys
import pandas as pd

# Add current directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.evaluation.metrics import EvaluationEngine
from src.metadata.gap_analyzer import MetadataRegistry
from src.rules.engine import RuleConfig
from src.scanner.runner import ScannerEngine


def run_pipeline():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(project_dir, "data")
    rules_path = os.path.join(data_dir, "rules.yaml") if os.path.exists(os.path.join(data_dir, "rules.yaml")) else os.path.join(project_dir, "rules.yaml")
    meta_path = os.path.join(data_dir, "metadata.csv")
    labels_path = os.path.join(data_dir, "labels.csv")

    print("\n" + "=" * 75)
    print("  PRIVACY EVIDENCE INVENTORY & PERSONAL-DATA DISCOVERY ENGINE (PS-019)")
    print("=" * 75)

    # 1. Initialize engine
    print("[1/4] Initializing rules, detectors, and metadata registry...")
    rule_config = RuleConfig(rules_path)
    meta_registry = MetadataRegistry(meta_path)
    engine = ScannerEngine(rule_config=rule_config, metadata_registry=meta_registry)

    # 2. Gather datasets
    csv_files = sorted(glob.glob(os.path.join(data_dir, "*.csv")))
    # Exclude metadata and labels from scanning targets
    csv_targets = [f for f in csv_files if not f.endswith("metadata.csv") and not f.endswith("labels.csv") and not f.endswith("inventory_latest.csv")]
    db_targets = sorted(glob.glob(os.path.join(data_dir, "*.db")))
    # Exclude reviewer db from scan targets if present
    db_targets = [f for f in db_targets if not f.endswith("reviewer_notes.db")]

    print(f"[2/4] Scanning {len(csv_targets)} CSV files and {len(db_targets)} SQLite database...")
    for c in csv_targets:
        print(f"  -> Target CSV: {os.path.basename(c)}")
    for d in db_targets:
        print(f"  -> Target DB:  {os.path.basename(d)}")

    # 3. Execute scan
    results = engine.scan_all(csv_targets, db_targets)
    df_results = pd.DataFrame(results)

    # Save exports
    export_csv = os.path.join(data_dir, "inventory_latest.csv")
    export_json = os.path.join(data_dir, "inventory_latest.json")
    df_results.to_csv(export_csv, index=False)
    df_results.to_json(export_json, orient="records", indent=2)
    print(f"\n[3/4] Scan complete! {len(results)} total fields profiled.")
    print(f"  -> Discovered Inventory saved to: {os.path.relpath(export_csv)}")

    # 4. Evaluation against ground truth
    print("[4/4] Evaluating against hand-labelled ground truth (labels.csv)...")
    eval_engine = EvaluationEngine(labels_path)
    eval_summary = eval_engine.evaluate(results)

    # Print Report Cards
    print("\n" + "-" * 75)
    print("  PER-CLASS PRIVACY DISCOVERY PERFORMANCE")
    print("-" * 75)
    per_class_df = eval_summary["per_class"]
    print(per_class_df.to_string(index=False))

    macro = eval_summary["macro_avg"]
    binary = eval_summary["binary_metrics"]
    print("\n" + "-" * 75)
    print("  OVERALL BENCHMARK ACCURACY & MACRO METRICS")
    print("-" * 75)
    print(f"  Macro Precision:        {round(macro['Precision'] * 100, 2)}%")
    print(f"  Macro Recall:           {round(macro['Recall'] * 100, 2)}%")
    print(f"  Macro F1-Score:         {round(macro['F1-Score'] * 100, 2)}%")
    print(f"  Binary PII Accuracy:    {round(binary['Accuracy'] * 100, 2)}%")
    print(f"  Binary PII F1-Score:    {round(binary['F1-Score'] * 100, 2)}%")

    # Privacy Compliance Gaps
    pii_records = df_results[df_results["is_pii"] == True]
    crit_gaps = len(pii_records[pii_records["gap_severity"] == "Critical Gap"])
    high_gaps = len(pii_records[pii_records["gap_severity"] == "High Gap"])
    med_gaps = len(pii_records[pii_records["gap_severity"] == "Medium Gap"])
    compliant = len(pii_records[pii_records["gap_severity"] == "Declared"])

    print("\n" + "-" * 75)
    print("  PRIVACY COMPLIANCE & GAP ANALYSIS SUMMARY")
    print("-" * 75)
    print(f"  Total PII Fields Discovered:  {len(pii_records)}")
    print(f"  Compliant (Declared Purpose & Retention): {compliant}")
    print(f"  Critical Gaps (Missing Purpose & Retention): {crit_gaps}")
    print(f"  High / Medium Gaps (Missing Retention / Schedule): {high_gaps + med_gaps}")
    print("  Technical Evidence Banner: Technical evidence only, not legal advice.")
    print("=" * 75 + "\n")

    return eval_summary


if __name__ == "__main__":
    run_pipeline()

"""Evaluation metrics engine for Precision, Recall, F1, and Confusion Matrix calculation."""

from typing import Any, Optional
import pandas as pd


class EvaluationEngine:
    """Calculates benchmark metrics against hand-labelled ground truth labels."""

    DATA_CLASSES = ["Name", "Email", "Phone", "Government ID", "Date of Birth", "Non-PII"]

    def __init__(self, labels_path: Optional[str] = None):
        self.labels_path = labels_path
        self.ground_truth_df: pd.DataFrame = pd.DataFrame()
        if labels_path:
            self.load_labels(labels_path)

    def load_labels(self, labels_path: str) -> None:
        self.labels_path = labels_path
        self.ground_truth_df = pd.read_csv(labels_path)

    def evaluate(self, scan_results: list[dict[str, Any]]) -> dict[str, Any]:
        """Compare scan results against ground truth labels.
        
        Returns:
            Dictionary containing per_class_metrics, macro_avg, binary_metrics, confusion_matrix, and errors.
        """
        if self.ground_truth_df.empty:
            raise ValueError("Ground truth labels not loaded.")

        # Create lookup for ground truth: (table_name.lower(), col_name.lower()) -> row
        gt_lookup = {}
        for _, row in self.ground_truth_df.iterrows():
            tbl = str(row.get("table_name", "")).strip().lower()
            col = str(row.get("column_name", "")).strip().lower()
            gt_class = str(row.get("ground_truth_class", "")).strip()
            gt_is_pii = bool(row.get("is_pii", False))
            gt_lookup[(tbl, col)] = {
                "dataset_name": str(row.get("dataset_name", "")),
                "table_name": tbl,
                "column_name": col,
                "ground_truth_class": gt_class,
                "is_pii": gt_is_pii,
                "note": str(row.get("description_note", "")),
            }

        # Match predictions
        comparison_records: list[dict[str, Any]] = []
        for pred in scan_results:
            tbl = str(pred["table_name"]).strip().lower()
            col = str(pred["column_name"]).strip().lower()
            pred_class = pred["detected_class"]
            pred_is_pii = pred["is_pii"]
            conf = pred["confidence_score"]

            gt = gt_lookup.get((tbl, col))
            if gt:
                comparison_records.append({
                    "dataset_name": pred["dataset_name"],
                    "table_name": pred["table_name"],
                    "column_name": pred["column_name"],
                    "predicted_class": pred_class,
                    "ground_truth_class": gt["ground_truth_class"],
                    "pred_is_pii": pred_is_pii,
                    "gt_is_pii": gt["is_pii"],
                    "confidence_score": conf,
                    "confidence_tier": pred["confidence_tier"],
                    "column_rule_matched": pred.get("column_rule_matched", "None"),
                    "pattern_rule_matched": pred.get("pattern_rule_matched", "None"),
                    "validator_used": pred.get("validator_used", "None"),
                    "note": gt["note"],
                })

        comp_df = pd.DataFrame(comparison_records)
        if comp_df.empty:
            return {
                "per_class": pd.DataFrame(),
                "macro_avg": {},
                "binary_metrics": {},
                "confusion_matrix": pd.DataFrame(),
                "false_positives": [],
                "false_negatives": [],
                "comparison_df": comp_df,
            }

        # Calculate per-class metrics
        class_stats = []
        for cls_name in self.DATA_CLASSES:
            tp = len(comp_df[(comp_df["predicted_class"] == cls_name) & (comp_df["ground_truth_class"] == cls_name)])
            fp = len(comp_df[(comp_df["predicted_class"] == cls_name) & (comp_df["ground_truth_class"] != cls_name)])
            fn = len(comp_df[(comp_df["predicted_class"] != cls_name) & (comp_df["ground_truth_class"] == cls_name)])
            support = len(comp_df[comp_df["ground_truth_class"] == cls_name])

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

            class_stats.append({
                "Data Class": cls_name,
                "Precision": round(precision, 4),
                "Recall": round(recall, 4),
                "F1-Score": round(f1, 4),
                "Support": support,
                "TP": tp,
                "FP": fp,
                "FN": fn,
            })

        per_class_df = pd.DataFrame(class_stats)

        # Macro average (across 5 PII classes)
        pii_stats = per_class_df[per_class_df["Data Class"] != "Non-PII"]
        macro_p = pii_stats["Precision"].mean() if not pii_stats.empty else 0.0
        macro_r = pii_stats["Recall"].mean() if not pii_stats.empty else 0.0
        macro_f1 = pii_stats["F1-Score"].mean() if not pii_stats.empty else 0.0

        # Binary PII metrics (Personal Data vs Non-Personal Data)
        b_tp = len(comp_df[(comp_df["pred_is_pii"] == True) & (comp_df["gt_is_pii"] == True)])
        b_fp = len(comp_df[(comp_df["pred_is_pii"] == True) & (comp_df["gt_is_pii"] == False)])
        b_fn = len(comp_df[(comp_df["pred_is_pii"] == False) & (comp_df["gt_is_pii"] == True)])
        b_tn = len(comp_df[(comp_df["pred_is_pii"] == False) & (comp_df["gt_is_pii"] == False)])

        b_prec = b_tp / (b_tp + b_fp) if (b_tp + b_fp) > 0 else 0.0
        b_rec = b_tp / (b_tp + b_fn) if (b_tp + b_fn) > 0 else 0.0
        b_f1 = (2 * b_prec * b_rec) / (b_prec + b_rec) if (b_prec + b_rec) > 0 else 0.0
        accuracy = (b_tp + b_tn) / len(comp_df) if len(comp_df) > 0 else 0.0

        binary_metrics = {
            "Precision": round(b_prec, 4),
            "Recall": round(b_rec, 4),
            "F1-Score": round(b_f1, 4),
            "Accuracy": round(accuracy, 4),
            "TP": b_tp,
            "FP": b_fp,
            "FN": b_fn,
            "TN": b_tn,
        }

        # Confusion matrix (Rows: Ground Truth, Columns: Predicted)
        conf_matrix = pd.crosstab(
            comp_df["ground_truth_class"],
            comp_df["predicted_class"],
            rownames=["Ground Truth"],
            colnames=["Predicted"],
            dropna=False,
        )
        # Ensure all classes are present in both axes
        for c in self.DATA_CLASSES:
            if c not in conf_matrix.index:
                conf_matrix.loc[c] = 0
            if c not in conf_matrix.columns:
                conf_matrix[c] = 0
        conf_matrix = conf_matrix.reindex(index=self.DATA_CLASSES, columns=self.DATA_CLASSES, fill_value=0)

        # Identify False Positives and False Negatives for error analysis
        false_positives = comp_df[
            (comp_df["pred_is_pii"] == True) & (comp_df["gt_is_pii"] == False)
        ].to_dict(orient="records")

        false_negatives = comp_df[
            (comp_df["pred_is_pii"] == False) & (comp_df["gt_is_pii"] == True)
        ].to_dict(orient="records")

        class_mismatches = comp_df[
            (comp_df["gt_is_pii"] == True)
            & (comp_df["pred_is_pii"] == True)
            & (comp_df["predicted_class"] != comp_df["ground_truth_class"])
        ].to_dict(orient="records")

        return {
            "per_class": per_class_df,
            "macro_avg": {
                "Precision": round(macro_p, 4),
                "Recall": round(macro_r, 4),
                "F1-Score": round(macro_f1, 4),
            },
            "binary_metrics": binary_metrics,
            "confusion_matrix": conf_matrix,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "class_mismatches": class_mismatches,
            "comparison_df": comp_df,
        }

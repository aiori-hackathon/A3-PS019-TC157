"""Unit tests for Evaluation metrics engine."""

import pandas as pd
from src.evaluation.metrics import EvaluationEngine


def test_evaluation_engine_metrics(tmp_path):
    labels_file = tmp_path / "test_labels.csv"
    labels_file.write_text(
        "dataset_name,table_name,column_name,ground_truth_class,is_pii,description_note\n"
        "d1,t1,col_email,Email,True,Email address\n"
        "d1,t1,col_name,Name,True,Full name\n"
        "d1,t1,col_num,Non-PII,False,Decoy\n",
        encoding="utf-8",
    )

    engine = EvaluationEngine(str(labels_file))

    # Mock predictions
    mock_preds = [
        {"dataset_name": "d1", "table_name": "t1", "column_name": "col_email", "detected_class": "Email", "is_pii": True, "confidence_score": 0.95, "confidence_tier": "High"},
        {"dataset_name": "d1", "table_name": "t1", "column_name": "col_name", "detected_class": "Name", "is_pii": True, "confidence_score": 0.90, "confidence_tier": "High"},
        {"dataset_name": "d1", "table_name": "t1", "column_name": "col_num", "detected_class": "Non-PII", "is_pii": False, "confidence_score": 0.10, "confidence_tier": "None"},
    ]

    metrics = engine.evaluate(mock_preds)
    assert "per_class" in metrics
    assert "binary_metrics" in metrics
    assert metrics["binary_metrics"]["Accuracy"] == 1.0
    assert metrics["binary_metrics"]["F1-Score"] == 1.0

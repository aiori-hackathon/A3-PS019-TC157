"""Unit tests for Metadata Registry and Compliance Gap Analyzer."""

from src.metadata.gap_analyzer import GapSeverity, MetadataRegistry


def test_metadata_registry_linkage(tmp_path):
    csv_file = tmp_path / "test_meta.csv"
    csv_file.write_text(
        "dataset_name,table_name,column_name,declared_purpose,retention_period,legal_notes\n"
        "test.csv,users,full_name,Identity verification,5 years,\n"
        "test.csv,users,aadhaar,,,\n"
        "test.csv,users,phone,SMS auth,,\n",
        encoding="utf-8",
    )

    reg = MetadataRegistry(str(csv_file))

    # Case 1: Fully declared
    rec1 = reg.link_and_analyze("test.csv", "users", "full_name", "Name", "High", 0.95)
    assert rec1.gap_severity == GapSeverity.COMPLIANT
    assert rec1.is_purpose_missing is False
    assert rec1.is_retention_missing is False

    # Case 2: Both missing (Critical Gap for High confidence PII)
    rec2 = reg.link_and_analyze("test.csv", "users", "aadhaar", "Government ID", "High", 0.90)
    assert rec2.gap_severity == GapSeverity.CRITICAL
    assert rec2.is_purpose_missing is True
    assert rec2.is_retention_missing is True

    # Case 3: Retention missing (Medium Gap)
    rec3 = reg.link_and_analyze("test.csv", "users", "phone", "Phone", "High", 0.85)
    assert rec3.gap_severity == GapSeverity.MEDIUM
    assert rec3.is_retention_missing is True

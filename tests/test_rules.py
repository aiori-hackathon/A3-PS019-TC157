"""Unit tests for Rule Engine configuration."""

import os
from src.rules.engine import RuleConfig, DEFAULT_RULES


def test_rule_config_defaults():
    config = RuleConfig()
    assert "column_name" in config.weights
    assert "value_pattern" in config.weights
    assert "algorithmic_validation" in config.weights
    assert config.weights["column_name"] + config.weights["value_pattern"] + config.weights["algorithmic_validation"] == 1.0
    assert "high" in config.thresholds


def test_yaml_export_and_update(tmp_path):
    path = tmp_path / "test_rules.yaml"
    config = RuleConfig()
    config.save(str(path))
    assert os.path.exists(path)

    loaded = RuleConfig(str(path))
    assert loaded.weights == config.weights

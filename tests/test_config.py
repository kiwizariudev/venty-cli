import os
import sys
import json
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_load_config_defaults():
    from core.config import load_config, DEFAULT_CONFIG
    cfg = load_config()
    for key in DEFAULT_CONFIG:
        assert key in cfg, f"Missing key in config: {key}"


def test_default_config_has_required_keys():
    from core.config import DEFAULT_CONFIG
    required = ["api_key", "model", "url", "provider", "max_tokens",
                "temperature", "max_loop", "save_history", "working_dir"]
    for key in required:
        assert key in DEFAULT_CONFIG, f"Missing required key: {key}"


def test_save_and_load_config(tmp_path, monkeypatch):
    cfg_path = str(tmp_path / "settings.json")
    monkeypatch.setattr("core.config.CONFIG_PATH", cfg_path)
    from core.config import save_config, load_config

    test_cfg = {"api_key": "test123", "model": "test-model", "temperature": 0.5}
    save_config(test_cfg)

    loaded = load_config()
    assert loaded["api_key"] == "test123"
    assert loaded["model"] == "test-model"
    assert loaded["temperature"] == 0.5


def test_load_config_missing_file(tmp_path, monkeypatch):
    cfg_path = str(tmp_path / "nonexistent.json")
    monkeypatch.setattr("core.config.CONFIG_PATH", cfg_path)
    from core.config import load_config, DEFAULT_CONFIG

    cfg = load_config()
    assert cfg["max_tokens"] == DEFAULT_CONFIG["max_tokens"]


def test_paths_exist():
    from core.paths import (
        BASE_DIR, DATA_DIR, CONFIG_DIR, MEMORY_DIR, LOGS_DIR,
        CACHE_DIR, SANDBOX_DIR, PLUGINS_DIR
    )
    assert os.path.isdir(BASE_DIR)
    for path in [DATA_DIR, CONFIG_DIR, MEMORY_DIR, LOGS_DIR, CACHE_DIR, SANDBOX_DIR]:
        assert os.path.isdir(path), f"Directory missing: {path}"

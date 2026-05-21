import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from actions import ACTIONS


def test_actions_loaded():
    assert len(ACTIONS) > 200, f"Expected 200+ actions, got {len(ACTIONS)}"


def test_all_actions_have_description():
    missing = [k for k, v in ACTIONS.items() if not v.get("description")]
    assert not missing, f"Actions missing description: {missing}"


def test_all_actions_have_execute():
    missing = [k for k, v in ACTIONS.items() if "execute" not in v]
    assert not missing, f"Actions missing execute: {missing}"


def test_control_actions_exist():
    for name in ("none", "cannot_do", "loop_start"):
        assert name in ACTIONS, f"Missing control action: {name}"


def test_docker_actions_exist():
    docker_actions = [k for k in ACTIONS if k.startswith("docker_")]
    assert len(docker_actions) >= 10, f"Expected 10+ docker actions, got {len(docker_actions)}"


def test_crossplatform_actions_exist():
    xp_actions = [k for k in ACTIONS if k.startswith("xp_")]
    assert len(xp_actions) >= 10, f"Expected 10+ xp_ actions, got {len(xp_actions)}"


def test_config_actions_exist():
    cfg_actions = [k for k in ACTIONS if k.startswith("cfg_")]
    assert len(cfg_actions) >= 5, f"Expected 5+ cfg_ actions, got {len(cfg_actions)}"


def test_language_actions_exist():
    for prefix in ("rust_", "go_", "deno_", "dotnet_"):
        found = [k for k in ACTIONS if k.startswith(prefix)]
        assert found, f"No actions found for prefix: {prefix}"


def test_memory_actions_exist():
    for name in ("memory_remember", "memory_forget", "memory_list", "memory_clear"):
        assert name in ACTIONS, f"Missing memory action: {name} (memory actions are added in cli.py, not actions package)"


def test_execute_none_action():
    result = ACTIONS["none"]["execute"]([])
    assert result is None


def test_execute_cannot_do():
    result = ACTIONS["cannot_do"]["execute"]([])
    assert result is None


def test_os_get_time():
    key = "os_get_time" if "os_get_time" in ACTIONS else "xp_get_time"
    result = ACTIONS[key]["execute"]([])
    assert hasattr(result, "stdout")
    assert len(result.stdout) > 5


def test_xp_hostname():
    result = ACTIONS["xp_hostname"]["execute"]([])
    assert hasattr(result, "stdout")
    assert len(result.stdout) > 0


def test_xp_python_version():
    result = ACTIONS["xp_python_version"]["execute"]([])
    assert hasattr(result, "stdout")
    assert "." in result.stdout


def test_os_base64_encode_decode():
    encoded = ACTIONS["os_base64_encode"]["execute"](["hello world"])
    assert hasattr(encoded, "stdout")
    decoded = ACTIONS["os_base64_decode"]["execute"]([encoded.stdout])
    assert decoded.stdout == "hello world"


def test_os_sha256_string():
    result = ACTIONS["os_sha256_string"]["execute"](["test"])
    assert hasattr(result, "stdout")
    assert len(result.stdout) == 64


def test_cfg_list():
    result = ACTIONS["cfg_list"]["execute"]([])
    assert hasattr(result, "stdout")

import os
import sys
import json
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import core.memory as mem_module


@pytest.fixture(autouse=True)
def isolated_notes(tmp_path):
    original = mem_module.NOTES_PATH
    test_path = str(tmp_path / "notes.json")
    mem_module.NOTES_PATH = test_path
    yield test_path
    mem_module.NOTES_PATH = original
    # clean up real notes.json after each test to prevent cross-test pollution
    if os.path.exists(original):
        try:
            with open(original, "w") as f:
                json.dump({"facts": [], "preferences": [], "projects": []}, f)
        except Exception:
            pass


def test_remember_and_list(isolated_notes):
    mem_module.remember("my project is at D:/za/reflect")
    data = json.loads(open(isolated_notes).read())
    assert any(e["text"] == "my project is at D:/za/reflect" for e in data.get("facts", []))


def test_list_notes_output(isolated_notes):
    mem_module.remember("test note")
    result = mem_module.list_notes()
    assert "test note" in result


def test_forget(isolated_notes):
    mem_module.remember("keep this note")
    mem_module.remember("delete this note")
    mem_module.forget("delete this")
    result = mem_module.list_notes()
    assert "keep this note" in result
    assert "delete this note" not in result


def test_clear_notes(isolated_notes):
    mem_module.remember("something")
    mem_module.clear_notes()
    result = mem_module.list_notes()
    assert result == "No notes saved yet."


def test_memory_block_empty(isolated_notes):
    mem_module.clear_notes()
    block = mem_module.get_memory_block()
    assert block == ""


def test_memory_block_with_notes(isolated_notes):
    mem_module.remember("user prefers Python")
    block = mem_module.get_memory_block()
    assert "user prefers Python" in block
    assert "MEMORY" in block


def test_remember_categories(isolated_notes):
    mem_module.remember("use dark theme", "preferences")
    mem_module.remember("project at D:/za", "projects")
    result = mem_module.list_notes()
    assert "use dark theme" in result
    assert "project at D:/za" in result

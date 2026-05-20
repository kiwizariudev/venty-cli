import pytest
from core.jsonutil import extract_first_json

def test_extract_simple_json():
    text = 'Some text before {"action": "test", "args": []} some text after'
    result = extract_first_json(text)
    assert result == {"action": "test", "args": []}

def test_extract_json_with_markdown():
    text = '```json\n{"action": "test", "args": ["arg1"]}\n```'
    result = extract_first_json(text)
    assert result == {"action": "test", "args": ["arg1"]}

def test_extract_nested_json():
    text = 'Here is the plan: {"action": "task_plan", "steps": [{"action": "step1", "args": []}]}'
    result = extract_first_json(text)
    assert result["action"] == "task_plan"
    assert len(result["steps"]) == 1

def test_invalid_json():
    text = "This is not json { invalid }"
    result = extract_first_json(text)
    assert result is None

def test_empty_input():
    assert extract_first_json("") is None
    assert extract_first_json(None) is None

import pytest
from unittest.mock import MagicMock, patch
from core.agent import ask

@patch("core.agent._requests.post")
def test_ask_success(mock_post):
    # Mock response
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": '{"action": "hello", "args": []}'}}]
    }
    mock_post.return_value = mock_resp

    cfg = {"api_key": "test", "url": "http://test.com", "model": "test-model"}
    history = []
    
    result = ask("hello", history, cfg, "system prompt")
    
    assert result == '{"action": "hello", "args": []}'
    assert len(history) == 2 # user + assistant
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"

@patch("core.agent._requests.post")
def test_ask_retry_on_invalid_json(mock_post):
    # First response invalid, second valid
    mock_resp_invalid = MagicMock()
    mock_resp_invalid.status_code = 200
    mock_resp_invalid.json.return_value = {
        "choices": [{"message": {"content": "invalid json"}}]
    }
    
    mock_resp_valid = MagicMock()
    mock_resp_valid.status_code = 200
    mock_resp_valid.json.return_value = {
        "choices": [{"message": {"content": '{"action": "retry_success"}'}}]
    }
    
    mock_post.side_effect = [mock_resp_invalid, mock_resp_valid]
    
    cfg = {"api_key": "test", "url": "http://test.com", "model": "test-model"}
    history = []
    
    result = ask("hello", history, cfg, "system prompt")
    
    assert result == '{"action": "retry_success"}'
    # History should have: user, assistant(invalid), user(correction), assistant(valid)
    assert len(history) == 4

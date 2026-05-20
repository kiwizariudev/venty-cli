import json
import time
import requests as _requests

from core.logger   import get_logger
from core.jsonutil import extract_first_json as _extract_first_json

logger = get_logger()

def build_messages(system_prompt: str, history: list) -> list:
    return [{"role": "system", "content": system_prompt}] + history

def ask(user_input: str, conversation_history: list, cfg: dict, system_prompt: str) -> str | None:
    conversation_history.append({"role": "user", "content": user_input})
    logger.info(f"User: {user_input}")

    api_key = cfg.get("api_key", "")
    url     = cfg.get("url",     "")
    model   = cfg.get("model",   "")

    if not api_key or not url:
        logger.error("API Key or URL missing in config")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type":  "application/json",
    }

    last_raw = None

    for attempt in range(3):
        messages = build_messages(system_prompt, conversation_history)
        payload  = {
            "model":       model,
            "messages":    messages,
            "temperature": cfg.get("temperature", 0.2),
            "max_tokens":  cfg.get("max_tokens",  700),
        }

        try:
            resp = _requests.post(
                url, headers=headers, json=payload,
                timeout=cfg.get("timeout", 60)
            )
            
            if resp.status_code != 200:
                logger.error(f"API Error {resp.status_code}: {resp.text}")
                if attempt < 2:
                    time.sleep(2)
                    continue
                return None

            resp_json = resp.json()
            if "choices" not in resp_json or not resp_json["choices"]:
                logger.error(f"Unexpected API response format: {resp_json}")
                return None

            raw      = resp_json["choices"][0]["message"]["content"].strip()
            last_raw = raw

            if _extract_first_json(raw) is not None:
                conversation_history.append({"role": "assistant", "content": raw})
                logger.info(f"Venty: {raw[:100]}")
                return raw

            logger.warning(f"Invalid JSON attempt {attempt + 1}: {raw[:80]}")
            if attempt < 2:
                conversation_history.append({"role": "assistant", "content": raw})
                conversation_history.append({
                    "role":    "user",
                    "content": "Invalid JSON. Reply ONLY with a single valid JSON object. No markdown, no extra text.",
                })

        except json.JSONDecodeError:
            logger.error("Failed to decode API response JSON")
        except _requests.exceptions.Timeout:
            logger.warning("Request timeout")
            time.sleep(1)
        except _requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return None
        except Exception as e:
            logger.error(f"ask() error: {e}")
            return None

    logger.error("All 3 attempts failed")
    return last_raw


def parse_response(raw: str) -> dict | None:
    return _extract_first_json(raw)


extract_first_json = _extract_first_json


def check_connection(url: str, timeout: int = 5) -> bool:
    try:
        base = url.split("/v1/")[0] if "/v1/" in url else url
        _requests.get(base, timeout=timeout)
        return True
    except Exception:
        return False

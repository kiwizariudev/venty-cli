"""
core/logger.py — centralised logging
"""
import os
import logging
import datetime

from core.paths import LOGS_DIR, LOG_PATH, ERROR_PATH, SESSION_PATH

os.makedirs(LOGS_DIR, exist_ok=True)

_logger = logging.getLogger("venty")
_logger.setLevel(logging.DEBUG)

if not _logger.handlers:
    _fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    _fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
    _fh.setLevel(logging.INFO)
    _fh.setFormatter(_fmt)

    _eh = logging.FileHandler(ERROR_PATH, encoding="utf-8")
    _eh.setLevel(logging.ERROR)
    _eh.setFormatter(_fmt)

    _logger.addHandler(_fh)
    _logger.addHandler(_eh)


def get_logger() -> logging.Logger:
    return _logger


def log_session_start() -> None:
    with open(SESSION_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] SESSION START\n")


def log_session_end() -> None:
    with open(SESSION_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] SESSION END\n")


def read_log_tail(path: str = LOG_PATH, lines: int = 30) -> str:
    if not os.path.exists(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
        return "".join(all_lines[-lines:])
    except Exception:
        return ""


def clear_logs() -> str:
    for p in (LOG_PATH, ERROR_PATH):
        if os.path.exists(p):
            open(p, "w", encoding="utf-8").close()
    return "logs cleared"

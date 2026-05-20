import os
import json
import time
import threading
import datetime
from core.paths import SCHEDULER_DIR, JOBS_PATH

os.makedirs(SCHEDULER_DIR, exist_ok=True)
_lock = threading.Lock()

def _load_jobs() -> list:
    if not os.path.exists(JOBS_PATH):
        return []
    try:
        with open(JOBS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_jobs(jobs: list) -> None:
    try:
        with open(JOBS_PATH, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2)
    except Exception:
        pass

def schedule_once(action: str, args: list, delay_seconds: int, label: str = "") -> str:
    run_at = (datetime.datetime.now() + datetime.timedelta(seconds=delay_seconds)).isoformat()
    job_id = f"job_{int(time.time() * 1000)}"
    job = {
        "id":      job_id,
        "label":   label or f"{action} in {delay_seconds}s",
        "action":  action,
        "args":    args,
        "run_at":  run_at,
        "repeat":  False,
        "done":    False,
    }
    with _lock:
        jobs = _load_jobs()
        jobs.append(job)
        _save_jobs(jobs)
    return job_id

def schedule_repeat(action: str, args: list, interval_seconds: int, label: str = "") -> str:
    run_at = (datetime.datetime.now() + datetime.timedelta(seconds=interval_seconds)).isoformat()
    job_id = f"job_{int(time.time() * 1000)}"
    job = {
        "id":       job_id,
        "label":    label or f"{action} every {interval_seconds}s",
        "action":   action,
        "args":     args,
        "run_at":   run_at,
        "repeat":   True,
        "interval": interval_seconds,
        "done":     False,
    }
    with _lock:
        jobs = _load_jobs()
        jobs.append(job)
        _save_jobs(jobs)
    return job_id

def cancel_job(job_id: str) -> bool:
    with _lock:
        jobs = _load_jobs()
        before = len(jobs)
        jobs = [j for j in jobs if j["id"] != job_id]
        _save_jobs(jobs)
        return len(jobs) < before

def list_jobs() -> list:
    return [j for j in _load_jobs() if not j.get("done")]

def tick(execute_fn, actions: dict, cfg: dict) -> list:
    now  = datetime.datetime.now()
    ran  = []
    with _lock:
        jobs = _load_jobs()
        for job in jobs:
            if job.get("done"): continue
            run_at = datetime.datetime.fromisoformat(job["run_at"])
            if now >= run_at:
                success, out = execute_fn(job["action"], job["args"], actions, cfg)
                ran.append((job["action"], job["args"], out))
                if job.get("repeat"):
                    interval = job.get("interval", 60)
                    job["run_at"] = (now + datetime.timedelta(seconds=interval)).isoformat()
                else:
                    job["done"] = True
        _save_jobs(jobs)
    return ran

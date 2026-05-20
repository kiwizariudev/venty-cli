import datetime
import platform
import socket
from core.paths import BASE_DIR, SANDBOX_DIR

def get_context(cfg: dict) -> str:
    working_dir = cfg.get("working_dir", SANDBOX_DIR)
    now         = datetime.datetime.now().strftime("%A %d %B %Y  %H:%M")
    hostname    = socket.gethostname()
    os_name     = f"{platform.system()} {platform.release()}"

    return (
        f"CONTEXT:\n"
        f"  working_dir : {working_dir}\n"
        f"  datetime    : {now}\n"
        f"  hostname    : {hostname}\n"
        f"  os          : {os_name}\n"
        f"  base_dir    : {BASE_DIR}\n"
        f"\n"
        f"Always use absolute paths based on working_dir unless the user specifies otherwise.\n"
        f"Never create files outside working_dir unless explicitly asked.\n"
    )

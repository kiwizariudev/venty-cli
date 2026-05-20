import os
import time
from core.logger  import get_logger
from core.history import log_action
from core.paths   import SANDBOX_DIR

logger = get_logger()

def resolve_path(path: str, working_dir: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.join(working_dir, path)

def _resolve_args(action_name: str, args: list, working_dir: str) -> list:
    PATH_ACTIONS = {
        "os_create_file", "os_write_file", "os_append_file", "os_read_file",
        "os_read_file_lines", "os_delete_file", "os_rename_file", "os_copy_file",
        "os_move_file", "os_list_files", "os_list_files_detail", "os_create_folder",
        "os_delete_folder", "os_delete_folder_recursive", "os_copy_folder",
        "os_file_exists", "os_file_size", "os_file_hash", "os_file_hash_md5",
        "os_zip_folder", "os_zip_file", "os_unzip", "os_count_files",
        "os_search_files", "os_search_content", "os_tree", "os_open_in_explorer",
        "os_file_modified", "os_get_extension", "os_get_filename", "os_get_folder",
        "os_compile_gcc", "os_compile_gcc_flags", "os_compile_gpp", "os_compile_gpp_flags",
        "os_compile_cs", "os_compile_java", "os_run_java", "os_run_exe",
        "os_run_exe_wait", "os_run_python", "os_run_python_args", "os_run_python3",
        "os_run_node", "os_run_batch", "os_run_powershell_script",
        "os_pip_install_req", "os_pip_freeze", "os_reg_export",
        "os_make_shortcut", "os_find_duplicates", "os_disk_usage",
        "os_run_rust", "os_run_go", "os_go_build", "os_run_ruby", "os_run_php",
        "tool_format_json", "tool_zip", "tool_unzip", "tool_http_server"
    }
    if action_name not in PATH_ACTIONS or not args:
        return args

    resolved = list(args)
    first = resolved[0]
    if not first.startswith("http") and not os.path.isabs(first):
        resolved[0] = resolve_path(first, working_dir)
    return resolved

def execute_action(action_name: str, args: list, actions: dict, cfg: dict) -> tuple[bool, str | None]:
    if action_name not in actions:
        return False, f"unknown action: {action_name}"

    if action_name in ("none", "cannot_do", "loop_start"):
        return True, None

    working_dir = cfg.get("working_dir", SANDBOX_DIR)
    resolved    = _resolve_args(action_name, args, working_dir)

    try:
        result = actions[action_name]["execute"](resolved)
        output = getattr(result, "stdout", None)
        log_action(action_name, resolved, True, output)
        logger.info(f"executed: {action_name} {resolved}")
        return True, output
    except FileNotFoundError as e:
        log_action(action_name, resolved, False, str(e))
        logger.error(f"FileNotFound: {action_name} — {e}")
        return False, f"file not found: {e}"
    except PermissionError:
        log_action(action_name, resolved, False, "PermissionError")
        logger.error(f"PermissionError: {action_name}")
        return False, "permission denied — try running as administrator"
    except Exception as e:
        log_action(action_name, resolved, False, str(e))
        logger.error(f"failed: {action_name} — {e}")
        return False, str(e)

def handle_loop(args: list, actions: dict, cfg: dict, ui) -> None:
    if len(args) < 2:
        ui.print_error("loop needs at least: count action_name")
        return
    try:
        count = int(args[0])
    except ValueError:
        ui.print_error(f"invalid count: {args[0]}")
        return

    max_loop = cfg.get("max_loop", 20)
    if count > max_loop:
        ui.print_warning(f"loop capped at {max_loop}")
        count = max_loop

    action_name = args[1]
    action_args = args[2:] if len(args) > 2 else []

    if action_name not in actions:
        ui.print_error(f"unknown action: {action_name}")
        return

    logger.info(f"loop: {count}x {action_name} {action_args}")
    ui.print_info(f"starting loop ×{count}")
    ui.print_separator()

    for i in range(1, count + 1):
        ui.print_loop_step(i, count, action_name, action_args)
        success, output = execute_action(action_name, action_args, actions, cfg)
        if success:
            ui.print_success(f"step {i} done")
            if output and cfg.get("show_output", True):
                ui.print_output(str(output)[:200])
        else:
            ui.print_error(f"step {i} failed: {output}")
        time.sleep(0.3)

    ui.print_separator()
    ui.print_success(f"loop done — {count} iterations")

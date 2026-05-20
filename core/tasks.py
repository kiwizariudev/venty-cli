"""
core/tasks.py — multi-step task plan executor
"""
import time


def run_task_plan(parsed: dict, execute_fn, actions: dict, cfg: dict, ui) -> int:
    """
    Execute a task_plan response.
    execute_fn = cli.execute_action(action_name, args)
    ui         = object with print_* methods
    Returns number of steps completed.
    """
    steps   = parsed.get("steps", [])
    message = parsed.get("message", "Running task...")

    if not steps:
        ui.print_error("task_plan has no steps")
        return 0

    ui.print_venty(message)
    ui.print_separator()
    ui.print_info(f"task plan — {len(steps)} steps")
    ui.print_separator()

    completed = 0
    for i, step in enumerate(steps, 1):
        action = step.get("action", "none")
        args   = step.get("args",   [])
        label  = step.get("label",  "")

        ui.print_step(i, len(steps), action, args, label)

        if action in ("none", "cannot_do"):
            ui.print_info("skipped")
            continue

        success, output = execute_fn(action, args)
        if success:
            ui.print_success(f"step {i} done")
            if output and cfg.get("show_output", True):
                ui.print_output(str(output)[:300])
            completed += 1
        else:
            ui.print_error(f"step {i} failed: {output}")
            try:
                confirm = input(f"  continue anyway? [y/N] > ").strip().lower()
            except Exception:
                confirm = "n"
            if confirm != "y":
                ui.print_warning("task aborted")
                return completed
        time.sleep(0.15)

    ui.print_separator()
    ui.print_success(f"task complete — {completed}/{len(steps)} steps done")
    return completed

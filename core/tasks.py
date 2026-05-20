import time
from typing import Callable

def run_task_plan(
    parsed: dict,
    execute_fn: Callable[[str, list], tuple[bool, str | None]],
    ui,
    *,
    depth: int = 0,
    max_depth: int = 8,
) -> bool:
    if depth > max_depth:
        ui.print_error("task plan nested too deeply — aborted")
        return False

    steps = parsed.get("steps", [])
    message = parsed.get("message", "Running task...")
    if not steps:
        ui.print_error("task_plan has no steps")
        return False

    if depth == 0:
        ui.print_venty(message)
        ui.print_separator()
        ui.print_info(f"task plan — {len(steps)} steps")
        ui.print_separator()

    for i, step in enumerate(steps, 1):
        if not isinstance(step, dict):
            ui.print_warning(f"step {i}: invalid step (skipped)")
            continue

        action = step.get("action", "none")
        args = step.get("args", [])
        if not isinstance(args, list):
            args = [str(args)] if args else []

        prefix = "  " * depth
        ui.print_step(i, len(steps), action)
        ui.print_action(action, args)

        if action in ("none", "cannot_do"):
            ui.print_info("skipped")
            continue

        if action == "task_plan":
            ok = run_task_plan(step, execute_fn, ui, depth=depth + 1, max_depth=max_depth)
            if not ok:
                return False
            continue

        success, output = execute_fn(action, args)
        if success:
            ui.print_success(f"step {i} done")
            if output:
                ui.print_output(str(output)[:400])
        else:
            ui.print_error(f"step {i} failed: {output}")
            try:
                confirm = input(
                    f"  {ui.Colors.YELLOW}continue anyway? [y/N] >{ui.Colors.RESET} "
                ).strip().lower()
            except (EOFError, KeyboardInterrupt):
                confirm = "n"
            if confirm != "y":
                ui.print_warning("task aborted")
                return False
        time.sleep(0.15)

    if depth == 0:
        ui.print_separator()
        ui.print_success(f"task complete — {len(steps)} steps done")
    return True

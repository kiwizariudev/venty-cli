ACTIONS = {
    "loop_start": {
        "description": "Repeat an action N times, args = [count, action_name, ...action_args]",
        "execute": lambda a: None,
    },
    "cannot_do": {
        "description": "Use when request is impossible, dangerous, or illegal",
        "execute": lambda a: None,
    },
    "none": {
        "description": "No action needed, just reply",
        "execute": lambda a: None,
    },
}

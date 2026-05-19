"""
Fun Pack — dice, coins, jokes, random choices.
"""
import json
import random
import urllib.request

from core.plugin_sdk import Plugin, ok, fail

plugin = Plugin(
    id="fun_pack",
    name="Fun Pack",
    version="1.0.0",
    description="Games and fun utilities",
    author="Venty",
)


@plugin.action("fun_dice", "Roll dice, args = [sides] or [] for d6")
def fun_dice(args):
    sides = 6
    if args:
        try:
            sides = max(2, min(1000, int(args[0])))
        except ValueError:
            return fail("sides must be a number")
    return ok(f"Rolled d{sides}: {random.randint(1, sides)}")


@plugin.action("fun_coin", "Flip a coin, args = []")
def fun_coin(args):
    return ok(random.choice(["Heads", "Tails"]))


@plugin.action("fun_pick", "Pick random item, args = [item1, item2, item3, ...]")
def fun_pick(args):
    if not args:
        return fail("pass options to pick from")
    return ok(f"Picked: {random.choice(args)}")


@plugin.action("fun_joke", "Random programming joke (needs internet), args = []")
def fun_joke(args):
    try:
        req = urllib.request.Request(
            "https://v2.jokeapi.dev/joke/Programming?blacklistFlags=nsfw,religious,political",
            headers={"User-Agent": "Venty/1.0"},
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode())
        if data.get("type") == "twopart":
            return ok(f"{data['setup']}\n…{data['delivery']}")
        return ok(data.get("joke", "no joke"))
    except Exception as e:
        return fail(f"joke API: {e}")


@plugin.action("fun_8ball", "Magic 8-ball, args = [your question]")
def fun_8ball(args):
    answers = [
        "Yes", "No", "Maybe", "Ask again later", "Definitely", "Very doubtful",
        "Outlook good", "Cannot predict now", "Signs point to yes",
    ]
    q = args[0] if args else "?"
    return ok(f"🎱 {q}\n→ {random.choice(answers)}")


ACTIONS = plugin.actions
PLUGIN_META = plugin.meta

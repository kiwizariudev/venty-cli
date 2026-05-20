"""
actions/__init__.py — assembles the master ACTIONS dict from all sub-modules
and loads any plugins from the plugins/ folder.
"""
import os
import importlib.util
import sys

from actions.files     import ACTIONS as _FILES
from actions.process   import ACTIONS as _PROCESS
from actions.compile   import ACTIONS as _COMPILE
from actions.git       import ACTIONS as _GIT
from actions.network   import ACTIONS as _NETWORK
from actions.system    import ACTIONS as _SYSTEM
from actions.power     import ACTIONS as _POWER
from actions.windows   import ACTIONS as _WINDOWS
from actions.registry  import ACTIONS as _REGISTRY
from actions.clipboard import ACTIONS as _CLIPBOARD
from actions.encode    import ACTIONS as _ENCODE
from actions.web       import ACTIONS as _WEB
from actions.browser   import ACTIONS as _BROWSER
from actions.control   import ACTIONS as _CONTROL
from actions.utils     import ACTIONS as _UTILS

ACTIONS: dict = {}
ACTIONS.update(_FILES)
ACTIONS.update(_PROCESS)
ACTIONS.update(_COMPILE)
ACTIONS.update(_GIT)
ACTIONS.update(_NETWORK)
ACTIONS.update(_SYSTEM)
ACTIONS.update(_POWER)
ACTIONS.update(_WINDOWS)
ACTIONS.update(_REGISTRY)
ACTIONS.update(_CLIPBOARD)
ACTIONS.update(_ENCODE)
ACTIONS.update(_WEB)
ACTIONS.update(_BROWSER)
ACTIONS.update(_CONTROL)
ACTIONS.update(_UTILS)

# Plugins are loaded by cli.py via core.plugins (after ACTIONS is imported).

import os
import importlib.util
import sys

import os
import importlib.util
import sys

from actions.files          import ACTIONS as _FILES
from actions.process        import ACTIONS as _PROCESS
from actions.compile        import ACTIONS as _COMPILE
from actions.git            import ACTIONS as _GIT
from actions.network        import ACTIONS as _NETWORK
from actions.system         import ACTIONS as _SYSTEM
from actions.power          import ACTIONS as _POWER
from actions.windows        import ACTIONS as _WINDOWS
from actions.registry       import ACTIONS as _REGISTRY
from actions.clipboard      import ACTIONS as _CLIPBOARD
from actions.encode         import ACTIONS as _ENCODE
from actions.web            import ACTIONS as _WEB
from actions.browser        import ACTIONS as _BROWSER
from actions.control        import ACTIONS as _CONTROL
from actions.utils          import ACTIONS as _UTILS
from actions.crossplatform  import ACTIONS as _CROSSPLATFORM
from actions.config_actions import ACTIONS as _CONFIG_ACTIONS
from actions.docker         import ACTIONS as _DOCKER
from actions.languages      import ACTIONS as _LANGUAGES
from actions.ssh            import ACTIONS as _SSH
from actions.pkgmanagers    import ACTIONS as _PKGMANAGERS

try:
    from core.native import ACTIONS as _NATIVE
except Exception:
    _NATIVE = {}

ACTIONS: dict = {}
for _src in [
    _FILES, _PROCESS, _COMPILE, _GIT, _NETWORK, _SYSTEM, _POWER,
    _WINDOWS, _REGISTRY, _CLIPBOARD, _ENCODE, _WEB, _BROWSER,
    _CONTROL, _UTILS, _CROSSPLATFORM, _CONFIG_ACTIONS,
    _DOCKER, _LANGUAGES, _SSH, _PKGMANAGERS, _NATIVE,
]:
    ACTIONS.update(_src)

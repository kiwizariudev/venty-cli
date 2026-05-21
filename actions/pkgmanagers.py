import subprocess
import platform

_OS = platform.system()

def _run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

ACTIONS = {
    "winget_install":   {"description": "Install a package with winget, args = [package_id]",                "execute": lambda a: _run(f"winget install --id {a[0]} -e --silent")},
    "winget_uninstall": {"description": "Uninstall a package with winget, args = [package_id]",              "execute": lambda a: _run(f"winget uninstall --id {a[0]} -e")},
    "winget_upgrade":   {"description": "Upgrade a package with winget, args = [package_id]",                "execute": lambda a: _run(f"winget upgrade --id {a[0]} -e")},
    "winget_upgrade_all":{"description": "Upgrade all packages with winget",                                  "execute": lambda a: _run("winget upgrade --all")},
    "winget_search":    {"description": "Search winget packages, args = [query]",                            "execute": lambda a: _run(f"winget search {a[0]}")},
    "winget_list":      {"description": "List installed packages via winget",                                 "execute": lambda a: _run("winget list")},

    "choco_install":    {"description": "Install a package with Chocolatey, args = [package]",               "execute": lambda a: _run(f"choco install {a[0]} -y")},
    "choco_uninstall":  {"description": "Uninstall a Chocolatey package, args = [package]",                  "execute": lambda a: _run(f"choco uninstall {a[0]} -y")},
    "choco_upgrade":    {"description": "Upgrade a Chocolatey package, args = [package]",                    "execute": lambda a: _run(f"choco upgrade {a[0]} -y")},
    "choco_upgrade_all":{"description": "Upgrade all Chocolatey packages",                                    "execute": lambda a: _run("choco upgrade all -y")},
    "choco_list":       {"description": "List installed Chocolatey packages",                                 "execute": lambda a: _run("choco list --local-only")},
    "choco_search":     {"description": "Search Chocolatey packages, args = [query]",                        "execute": lambda a: _run(f"choco search {a[0]}")},

    "brew_install":     {"description": "Install a package with Homebrew, args = [package]",                 "execute": lambda a: _run(f"brew install {a[0]}")},
    "brew_uninstall":   {"description": "Uninstall a Homebrew package, args = [package]",                    "execute": lambda a: _run(f"brew uninstall {a[0]}")},
    "brew_upgrade":     {"description": "Upgrade a Homebrew package, args = [package]",                      "execute": lambda a: _run(f"brew upgrade {a[0]}")},
    "brew_upgrade_all": {"description": "Upgrade all Homebrew packages",                                      "execute": lambda a: _run("brew upgrade")},
    "brew_list":        {"description": "List installed Homebrew packages",                                   "execute": lambda a: _run("brew list")},
    "brew_search":      {"description": "Search Homebrew packages, args = [query]",                          "execute": lambda a: _run(f"brew search {a[0]}")},
    "brew_info":        {"description": "Get info about a Homebrew package, args = [package]",               "execute": lambda a: _run(f"brew info {a[0]}")},

    "apt_install":      {"description": "Install a package with apt, args = [package]",                      "execute": lambda a: _run(f"sudo apt-get install -y {a[0]}")},
    "apt_remove":       {"description": "Remove a package with apt, args = [package]",                       "execute": lambda a: _run(f"sudo apt-get remove -y {a[0]}")},
    "apt_update":       {"description": "Update apt package list",                                            "execute": lambda a: _run("sudo apt-get update")},
    "apt_upgrade":      {"description": "Upgrade all apt packages",                                           "execute": lambda a: _run("sudo apt-get upgrade -y")},
    "apt_search":       {"description": "Search apt packages, args = [query]",                               "execute": lambda a: _run(f"apt-cache search {a[0]}")},
    "apt_list":         {"description": "List installed apt packages",                                        "execute": lambda a: _run("apt list --installed")},

    "scoop_install":    {"description": "Install a package with Scoop, args = [package]",                    "execute": lambda a: _run(f"scoop install {a[0]}")},
    "scoop_uninstall":  {"description": "Uninstall a Scoop package, args = [package]",                       "execute": lambda a: _run(f"scoop uninstall {a[0]}")},
    "scoop_update":     {"description": "Update all Scoop packages",                                          "execute": lambda a: _run("scoop update *")},
    "scoop_list":       {"description": "List installed Scoop packages",                                      "execute": lambda a: _run("scoop list")},
    "scoop_search":     {"description": "Search Scoop packages, args = [query]",                             "execute": lambda a: _run(f"scoop search {a[0]}")},
}

# scripts/

Convenience launchers so you don't have to type `python` every time.

| File | Command | Description |
|------|---------|-------------|
| `run.bat` | `scripts\run.bat` | Start Venty (Windows CMD) |
| `run.ps1` | `.\scripts\run.ps1` | Start Venty (PowerShell) |
| `setup.bat` | `scripts\setup.bat` | Run setup wizard (Windows CMD) |

## Usage

```bat
# From project root
scripts\run.bat

# Or directly
python cli.py
python setup.py
python config.py
```

## What `run.bat` does

1. Activates `env\` virtual environment if it exists
2. Runs `python cli.py`
3. On exit, deactivates the venv

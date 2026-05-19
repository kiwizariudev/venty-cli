@echo off
cd /d "%~dp0.."
if exist env\Scripts\python.exe (
    env\Scripts\python.exe cli.py
) else (
    python cli.py
)

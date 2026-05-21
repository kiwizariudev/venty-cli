@echo off
echo Building venty_engine...
g++ -std=c++17 -O2 -o venty_engine.exe venty_engine.cpp
if %errorlevel% == 0 (
    echo Build successful: venty_engine.exe
) else (
    echo Build failed. Make sure g++ is installed.
)

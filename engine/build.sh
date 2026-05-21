#!/bin/bash
echo "Building venty_engine..."
g++ -std=c++17 -O2 -o venty_engine venty_engine.cpp
if [ $? -eq 0 ]; then
    echo "Build successful: venty_engine"
else
    echo "Build failed. Make sure g++ is installed."
fi

#!/bin/bash
echo "Starting Venty Bridge..."
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi
if [ ! -d "dist" ]; then
    echo "Building TypeScript..."
    npm run build
fi
npm start

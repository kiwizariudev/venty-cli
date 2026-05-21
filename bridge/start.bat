@echo off
echo Starting Venty Bridge...
if not exist node_modules (
    echo Installing dependencies...
    npm install
)
if not exist dist (
    echo Building TypeScript...
    npm run build
)
npm start

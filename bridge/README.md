# Venty Bridge

Web UI and REST API for Venty. Built with TypeScript + Express + WebSocket.

## Setup

```bash
cd bridge
npm install
npm run build
npm start
```

Then open http://localhost:7432 in your browser.

## Dev mode (hot reload)

```bash
npm run dev
```

## Or ask Venty directly

```
bridge_install
bridge_start
bridge_open
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/status | Venty status + model info |
| GET | /api/config | Current config (key masked) |
| POST | /api/config | Update config |
| GET | /api/history | Last 100 conversation turns |
| GET | /api/stats | Action usage statistics |
| GET | /api/memory | Saved notes |
| GET | /api/logs?type=venty&lines=50 | Log file contents |
| WS | ws://localhost:7432 | Real-time chat |

## WebSocket messages

Send:
```json
{ "type": "chat", "content": "open notepad" }
```

Receive:
```json
{ "type": "thinking" }
{ "type": "token", "content": "..." }
{ "type": "response", "data": { "action": "os_open", "message": "...", "suggestions": [...] } }
```

## Port

Default: `7432`. Change with env var `VENTY_PORT=8080 npm start`.

import express, { Request, Response } from "express";
import cors from "cors";
import { WebSocketServer, WebSocket } from "ws";
import path from "path";
import fs from "fs";
import http from "http";

const PORT     = parseInt(process.env.VENTY_PORT || "7432");
const BASE_DIR = path.resolve(__dirname, "..", "..");
const DATA_DIR = path.join(BASE_DIR, "data");

const app    = express();
const server = http.createServer(app);
const wss    = new WebSocketServer({ server });

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, "..", "public")));

interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
}

interface ActionLog {
  timestamp: string;
  action: string;
  args: string[];
  success: boolean;
  output_preview: string | null;
}

function readJson<T>(filePath: string, fallback: T): T {
  try {
    if (!fs.existsSync(filePath)) return fallback;
    return JSON.parse(fs.readFileSync(filePath, "utf-8")) as T;
  } catch {
    return fallback;
  }
}

function readConfig(): Record<string, unknown> {
  return readJson(path.join(DATA_DIR, "config", "settings.json"), {});
}

app.get("/api/status", (_req: Request, res: Response) => {
  const cfg = readConfig();
  res.json({
    status:   "running",
    provider: cfg.provider || "unknown",
    model:    cfg.display_name || cfg.model || "unknown",
    version:  "1.0.0",
  });
});

app.get("/api/config", (_req: Request, res: Response) => {
  const cfg = readConfig();
  const safe = { ...cfg };
  if (safe.api_key) safe.api_key = "***";
  res.json(safe);
});

app.post("/api/config", (req: Request, res: Response) => {
  const cfgPath = path.join(DATA_DIR, "config", "settings.json");
  const current = readConfig();
  const updated = { ...current, ...req.body };
  if (req.body.api_key === "***") updated.api_key = current.api_key;
  fs.writeFileSync(cfgPath, JSON.stringify(updated, null, 2));
  res.json({ ok: true });
});

app.get("/api/history", (_req: Request, res: Response) => {
  const history = readJson<ChatMessage[]>(
    path.join(DATA_DIR, "memory", "history.json"), []
  );
  res.json(history.slice(-100));
});

app.get("/api/stats", (_req: Request, res: Response) => {
  const cache = readJson<ActionLog[]>(
    path.join(DATA_DIR, "cache", "actions.json"), []
  );
  const total   = cache.length;
  const success = cache.filter(a => a.success).length;
  const counts: Record<string, number> = {};
  for (const a of cache) counts[a.action] = (counts[a.action] || 0) + 1;
  const top = Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([action, count]) => ({ action, count }));
  res.json({ total, success, failed: total - success, top });
});

app.get("/api/memory", (_req: Request, res: Response) => {
  const notes = readJson(path.join(DATA_DIR, "memory", "notes.json"), {});
  res.json(notes);
});

app.get("/api/logs", (req: Request, res: Response) => {
  const type  = (req.query.type as string) || "venty";
  const lines = parseInt((req.query.lines as string) || "50");
  const logFile = path.join(DATA_DIR, "logs", `${type}.log`);
  if (!fs.existsSync(logFile)) { res.json({ lines: [] }); return; }
  const all = fs.readFileSync(logFile, "utf-8").split("\n").filter(Boolean);
  res.json({ lines: all.slice(-lines) });
});

app.get("/api/action-log", (_req: Request, res: Response) => {
  const cache = readJson<ActionLog[]>(
    path.join(DATA_DIR, "cache", "actions.json"), []
  );
  res.json(cache);
});

const clients = new Set<WebSocket>();

wss.on("connection", (ws: WebSocket) => {
  clients.add(ws);
  ws.send(JSON.stringify({ type: "connected", message: "Venty dashboard connected" }));
  ws.on("close", () => clients.delete(ws));
});

server.listen(PORT, () => {
  console.log(`Venty bridge running at http://localhost:${PORT}`);
  console.log(`WebSocket at ws://localhost:${PORT}`);
});

export default app;

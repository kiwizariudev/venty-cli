const API = "http://localhost:7432/api";
let autoRefreshTimer = null;
let currentConfig = {};

function $(id) { return document.getElementById(id); }

async function fetchJSON(path) {
  try {
    const r = await fetch(API + path);
    return await r.json();
  } catch { return null; }
}

function setStatus(state, text) {
  $("status-dot").className = "dot " + state;
  $("status-text").textContent = text;
}

function colorizeLog(line) {
  const el = document.createElement("span");
  if (line.includes("[ERROR]") || line.includes("ERROR")) el.className = "log-line-error";
  else if (line.includes("[WARNING]") || line.includes("WARN")) el.className = "log-line-warning";
  else el.className = "log-line-info";
  el.textContent = line + "\n";
  return el;
}

// ── TABS ──────────────────────────────────────────────────────────────────────
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    btn.classList.add("active");
    $("tab-" + btn.dataset.tab).classList.add("active");
    const loaders = {
      overview: loadOverview,
      logs:     loadLogs,
      actions:  loadActions,
      memory:   loadMemory,
      history:  loadHistory,
      config:   loadConfig,
    };
    loaders[btn.dataset.tab]?.();
  });
});

$("refresh-all").addEventListener("click", () => {
  const active = document.querySelector(".tab-btn.active")?.dataset.tab;
  const loaders = { overview: loadOverview, logs: loadLogs, actions: loadActions, memory: loadMemory, history: loadHistory, config: loadConfig };
  loaders[active]?.();
});

// ── OVERVIEW ──────────────────────────────────────────────────────────────────
async function loadOverview() {
  const stats = await fetchJSON("/stats");
  if (stats) {
    $("stat-total").textContent   = stats.total;
    $("stat-success").textContent = stats.success;
    $("stat-failed").textContent  = stats.failed;
    const top = $("top-actions");
    top.innerHTML = "";
    const max = stats.top[0]?.count || 1;
    stats.top.forEach(({ action, count }) => {
      const row = document.createElement("div");
      row.className = "bar-row";
      row.innerHTML = `
        <div class="bar-label">${action}</div>
        <div class="bar-fill" style="width:${Math.max(3, (count/max)*180)}px"></div>
        <div class="bar-count">${count}</div>`;
      top.appendChild(row);
    });
  }
  const errLog = await fetchJSON("/logs?type=errors&lines=20");
  if (errLog) {
    const pre = $("recent-errors");
    pre.innerHTML = "";
    errLog.lines.slice(-15).forEach(l => pre.appendChild(colorizeLog(l)));
    pre.scrollTop = pre.scrollHeight;
  }
  const log = await fetchJSON("/logs?type=venty&lines=30");
  if (log) {
    const pre = $("recent-log");
    pre.innerHTML = "";
    log.lines.slice(-20).forEach(l => pre.appendChild(colorizeLog(l)));
    pre.scrollTop = pre.scrollHeight;
  }
}

// ── LOGS ──────────────────────────────────────────────────────────────────────
async function loadLogs() {
  const type  = $("log-type").value;
  const lines = $("log-lines").value;
  const data  = await fetchJSON(`/logs?type=${type}&lines=${lines}`);
  if (!data) return;
  const pre = $("log-output");
  pre.innerHTML = "";
  data.lines.forEach(l => pre.appendChild(colorizeLog(l)));
  pre.scrollTop = pre.scrollHeight;
}

$("refresh-logs").addEventListener("click", loadLogs);
$("log-type").addEventListener("change", loadLogs);
$("log-lines").addEventListener("change", loadLogs);
$("clear-log-view").addEventListener("click", () => { $("log-output").innerHTML = ""; });

$("auto-refresh-logs").addEventListener("change", (e) => {
  if (e.target.checked) {
    autoRefreshTimer = setInterval(loadLogs, 3000);
  } else {
    clearInterval(autoRefreshTimer);
    autoRefreshTimer = null;
  }
});

// ── ACTIONS ───────────────────────────────────────────────────────────────────
let allActions = [];

async function loadActions() {
  const data = await fetchJSON("/action-log");
  if (!data) return;
  allActions = data.reverse();
  renderActions();
}

function renderActions() {
  const filter     = $("action-filter").value.toLowerCase();
  const statusFilt = $("action-status-filter").value;
  const tbody = $("actions-tbody");
  tbody.innerHTML = "";
  allActions
    .filter(a => {
      if (filter && !a.action.toLowerCase().includes(filter)) return false;
      if (statusFilt === "success" && !a.success) return false;
      if (statusFilt === "failed"  &&  a.success) return false;
      return true;
    })
    .slice(0, 200)
    .forEach(a => {
      const tr = document.createElement("tr");
      const ts = a.timestamp ? a.timestamp.replace("T", " ").slice(0, 19) : "";
      const args = Array.isArray(a.args) ? a.args.map(x => JSON.stringify(x)).join(", ") : "";
      tr.innerHTML = `
        <td class="action-time">${ts}</td>
        <td><span class="action-name">${a.action}</span></td>
        <td><span class="action-args" title="${args}">${args}</span></td>
        <td><span class="badge ${a.success ? 'badge-ok' : 'badge-err'}">${a.success ? '✓ ok' : '✗ fail'}</span></td>
        <td><span class="action-output" title="${a.output_preview || ''}">${a.output_preview || ''}</span></td>`;
      tbody.appendChild(tr);
    });
}

$("refresh-actions").addEventListener("click", loadActions);
$("action-filter").addEventListener("input", renderActions);
$("action-status-filter").addEventListener("change", renderActions);

// ── MEMORY ────────────────────────────────────────────────────────────────────
async function loadMemory() {
  const data = await fetchJSON("/memory");
  const el = $("memory-content");
  el.innerHTML = "";
  if (!data) { el.textContent = "Could not load memory."; return; }
  let hasAny = false;
  for (const [cat, entries] of Object.entries(data)) {
    if (!Array.isArray(entries) || !entries.length) continue;
    hasAny = true;
    const section = document.createElement("div");
    section.className = "memory-category";
    const title = document.createElement("div");
    title.className = "memory-cat-title";
    title.textContent = cat;
    section.appendChild(title);
    entries.forEach(e => {
      const item = document.createElement("div");
      item.className = "memory-item";
      item.innerHTML = `<span class="memory-item-text">${e.text}</span><span class="memory-item-date">${e.added || ""}</span>`;
      section.appendChild(item);
    });
    el.appendChild(section);
  }
  if (!hasAny) el.innerHTML = `<div style="color:var(--muted);padding:20px">No notes saved yet.</div>`;
}

$("refresh-memory").addEventListener("click", loadMemory);

// ── HISTORY ───────────────────────────────────────────────────────────────────
let allHistory = [];

async function loadHistory() {
  const data = await fetchJSON("/history");
  if (!data) return;
  allHistory = data;
  renderHistory();
}

function renderHistory() {
  const filter = $("history-filter").value.toLowerCase();
  const list = $("history-list");
  list.innerHTML = "";
  allHistory
    .filter(e => !filter || (e.content || "").toLowerCase().includes(filter))
    .slice(-100)
    .reverse()
    .forEach(e => {
      const el = document.createElement("div");
      el.className = "history-entry " + (e.role || "");
      let text = e.content || "";
      try { const p = JSON.parse(text); text = p.message || text; } catch {}
      el.innerHTML = `<div class="history-role">${e.role || "?"}</div><div class="history-content">${text.slice(0, 300)}</div>`;
      list.appendChild(el);
    });
}

$("refresh-history").addEventListener("click", loadHistory);
$("history-filter").addEventListener("input", renderHistory);

// ── CONFIG ────────────────────────────────────────────────────────────────────
async function loadConfig() {
  const data = await fetchJSON("/config");
  if (!data) return;
  currentConfig = data;
  const grid = $("config-grid");
  grid.innerHTML = "";
  const editable = [
    "model", "display_name", "provider", "url",
    "temperature", "max_tokens", "max_loop", "timeout",
    "working_dir", "theme", "stream", "max_session_turns",
    "enable_bridge", "bridge_port", "show_output",
  ];
  editable.forEach(key => {
    const field = document.createElement("div");
    field.className = "config-field";
    field.innerHTML = `<label>${key}</label><input type="text" name="${key}" value="${data[key] ?? ""}"/>`;
    grid.appendChild(field);
  });
}

$("refresh-config").addEventListener("click", loadConfig);

$("save-config").addEventListener("click", async () => {
  const inputs = document.querySelectorAll("#config-grid input");
  const updated = { ...currentConfig };
  inputs.forEach(inp => { updated[inp.name] = inp.value; });
  try {
    await fetch(API + "/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updated),
    });
    $("save-config").textContent = "Saved ✓";
    setTimeout(() => { $("save-config").textContent = "Save Changes"; }, 2000);
  } catch {
    $("save-config").textContent = "Error";
  }
});

// ── INIT ──────────────────────────────────────────────────────────────────────
async function init() {
  setStatus("offline", "connecting...");
  try {
    const status = await fetchJSON("/status");
    if (status) {
      setStatus("online", "connected");
      $("model-badge").textContent = `${status.provider} / ${status.model}`;
    } else {
      setStatus("offline", "bridge not running");
    }
  } catch {
    setStatus("offline", "bridge not running");
  }
  loadOverview();
}

init();

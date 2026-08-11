"""tss_server.py - local single-page web dashboard for TSS v10.

A zero-dependency http.server application (ThreadingHTTPServer) bound to
127.0.0.1:8000 that serves a dark-theme single-page app with eight panels
(whistleblower browser, corporate tracker, regulatory law browser, source
verification dashboard, filing template compiler, projection viewer, security
checklist, diagnostics report) plus JSON API endpoints backed by the
data/*.json databases and the tss_core modules.

All CSS and JavaScript is embedded in one HTML string; the server works fully
offline.  API endpoints degrade to {"error": ...} with HTTP 500 when a data
file or tss_core module is not ready yet, so the server always starts.

--once mode starts the server in a background thread, self-tests "/" and
"/api/whistleblowers" with urllib, prints the status codes, shuts down and
exits 0 - this lets CI verify the server without blocking.

Standard library only: argparse, http.server, json, pathlib, sys, threading,
urllib (self-test only).
"""

import argparse
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, Optional
from urllib.request import urlopen
from urllib.error import HTTPError, URLError


def _resolve_project_root() -> Path:
    """Return the TSS project root directory (the one containing data/).

    The server lives at <root>/tss_web/tss_server.py so parents[1] is the
    project root; parents[2] is retained as a fallback for relocated trees.
    The first candidate containing a data/ directory wins, keeping the
    resolution deterministic and independent of checkout depth.
    """
    here = Path(__file__).resolve()
    for candidate in (here.parents[1], here.parents[2]):
        if (candidate / "data").is_dir():
            return candidate
    return here.parents[1]


PROJECT_ROOT: Path = _resolve_project_root()
DATA_DIR: Path = PROJECT_ROOT / "data"

# API route -> data file backing it.
DATA_ROUTES: Dict[str, str] = {
    "/api/whistleblowers": "whistleblowers.json",
    "/api/corporations": "corporations.json",
    "/api/statutes": "statutes.json",
    "/api/cases": "cases.json",
    "/api/sources": "sources.json",
}

# In-memory cache: data file name -> parsed JSON (loaded lazily on request).
_DATA_CACHE: Dict[str, object] = {}

# The single-page application: all CSS/JS embedded, fetched data comes from
# the API routes below via fetch().  No Python interpolation is used, so the
# braces are safe as-is.
INDEX_HTML: str = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TSS v10 — AI Accountability Dashboard</title>
<style>
  :root {
    --bg: #010102; --fg: #e0e0e0; --red: #ff4444;
    --cyan: #00ccff; --green: #00ff66; --panel: #0c0c10;
    --border: #26262e; --muted: #8a8a96;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--fg);
    font-family: "Courier New", ui-monospace, monospace; font-size: 14px;
  }
  header {
    padding: 18px 24px; border-bottom: 1px solid var(--border);
    display: flex; align-items: baseline; gap: 16px; flex-wrap: wrap;
  }
  header h1 { margin: 0; font-size: 20px; letter-spacing: 1px; }
  header .tag { color: var(--cyan); }
  header .status { color: var(--muted); margin-left: auto; font-size: 12px; }
  main { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; padding: 16px 24px; }
  @media (max-width: 1000px) { main { grid-template-columns: 1fr; } }
  section.panel {
    background: var(--panel); border: 1px solid var(--border);
    border-radius: 8px; padding: 14px 16px;
  }
  section.panel h2 {
    margin: 0 0 10px 0; font-size: 15px; color: var(--cyan);
    border-bottom: 1px solid var(--border); padding-bottom: 8px;
  }
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  th, td { text-align: left; padding: 4px 6px; border-bottom: 1px solid var(--border); }
  th { color: var(--muted); font-weight: normal; text-transform: uppercase; font-size: 11px; }
  input, select, textarea, button {
    background: #14141a; color: var(--fg); border: 1px solid var(--border);
    border-radius: 4px; padding: 6px 8px; font-family: inherit; font-size: 13px;
  }
  button { cursor: pointer; color: var(--cyan); }
  button:hover { border-color: var(--cyan); }
  .badge { display: inline-block; padding: 1px 8px; border-radius: 10px; font-size: 11px; }
  .ok   { color: var(--green); border: 1px solid var(--green); }
  .warn { color: var(--red); border: 1px solid var(--red); }
  .info { color: var(--cyan); border: 1px solid var(--cyan); }
  .muted { color: var(--muted); }
  .bar { height: 10px; background: #14141a; border-radius: 5px; overflow: hidden; margin: 3px 0 10px 0; }
  .bar > div { height: 100%; background: var(--cyan); }
  pre.out { white-space: pre-wrap; font-size: 12px; background: #0a0a0e; padding: 8px; border-radius: 4px; }
  ul.checklist { list-style: none; padding-left: 4px; margin: 6px 0; }
  ul.checklist li { padding: 3px 0; }
  a { color: var(--cyan); }
  .err { color: var(--red); }
</style>
</head>
<body>
<header>
  <h1>TSS <span class="tag">v10</span></h1>
  <span class="muted">AI Accountability Infrastructure — offline dashboard</span>
  <span class="status" id="connStatus">connecting…</span>
</header>
<main>

  <!-- 1. Whistleblower browser -->
  <section class="panel">
    <h2>1 · Whistleblower Browser</h2>
    <div style="display:flex; gap:8px; margin-bottom:8px;">
      <input id="wbSearch" placeholder="search name / employer / role" style="flex:1;">
      <select id="wbFilter">
        <option value="">all statuses</option>
        <option>verified</option>
        <option>reported-unverified</option>
        <option>gap</option>
      </select>
    </div>
    <div style="max-height:260px; overflow:auto;">
      <table><thead><tr>
        <th>Name</th><th>Employer</th><th>Role</th><th>Date</th><th>Status</th>
      </tr></thead><tbody id="wbBody"></tbody></table>
    </div>
    <p class="muted" id="wbCount"></p>
  </section>

  <!-- 2. Corporate tracker -->
  <section class="panel">
    <h2>2 · Corporate Tracker</h2>
    <div style="max-height:260px; overflow:auto;">
      <table><thead><tr>
        <th>Company</th><th>Silence rate</th><th>Response history</th><th>Prediction</th>
      </tr></thead><tbody id="corpBody"></tbody></table>
    </div>
    <div style="margin-top:8px; display:flex; gap:8px;">
      <select id="corpSelect" style="flex:1;"></select>
      <button id="corpPredict">Predict next departure</button>
    </div>
    <pre class="out" id="corpOut"></pre>
  </section>

  <!-- 3. Regulatory law browser -->
  <section class="panel">
    <h2>3 · Regulatory Law Browser</h2>
    <div style="max-height:260px; overflow:auto;">
      <table><thead><tr>
        <th>Statute</th><th>Title</th><th>Enforcement</th>
      </tr></thead><tbody id="statBody"></tbody></table>
    </div>
    <p class="muted">Case law precedent:</p>
    <div style="max-height:140px; overflow:auto;">
      <table><thead><tr><th>Case</th><th>Citation</th></tr></thead>
      <tbody id="caseBody"></tbody></table>
    </div>
  </section>

  <!-- 4. Source verification dashboard -->
  <section class="panel">
    <h2>4 · Source Verification Dashboard</h2>
    <div style="max-height:300px; overflow:auto;">
      <table><thead><tr>
        <th>Title</th><th>Status</th><th>Source</th><th>Archive</th>
      </tr></thead><tbody id="srcBody"></tbody></table>
    </div>
  </section>

  <!-- 5. Filing template compiler -->
  <section class="panel">
    <h2>5 · Filing Template Compiler</h2>
    <div style="display:flex; gap:8px; margin-bottom:8px;">
      <select id="ftAgency">
        <option>SEC</option><option>FTC</option><option>EEOC</option>
        <option>NLRB</option><option>CA DLSE</option><option>EU DPA</option>
      </select>
      <button id="ftCompile">Compile template</button>
    </div>
    <textarea id="ftClaim" rows="5" style="width:100%;"
      placeholder='claim JSON, e.g. {"summary": "…", "company": "…"}'>{"summary": "Safety concern reported internally", "company": "OpenAI"}</textarea>
    <pre class="out" id="ftOut"></pre>
  </section>

  <!-- 6. Projection viewer -->
  <section class="panel">
    <h2>6 · Projection Viewer</h2>
    <div style="display:flex; gap:8px; margin-bottom:8px;">
      <select id="projSelect" style="flex:1;"></select>
      <button id="projRun">Project</button>
    </div>
    <pre class="out" id="projOut"></pre>
    <p class="muted">Enforcement forecast: derived from statute enforcement
    status and corporation response history (see panels 2–3).</p>
  </section>

  <!-- 7. Security checklist -->
  <section class="panel">
    <h2>7 · Security Checklist</h2>
    <p class="muted">Anonymity setup</p>
    <ul class="checklist">
      <li><label><input type="checkbox" class="sec"> Use Tor Browser or a
        dedicated Tails boot for all research</label></li>
      <li><label><input type="checkbox" class="sec"> Burner email + ProtonMail
        or Tutanota, no phone number</label></li>
      <li><label><input type="checkbox" class="sec"> No corporate or personal
        devices; public Wi-Fi only</label></li>
      <li><label><input type="checkbox" class="sec"> PGP-encrypt every
        draft; keys on offline media</label></li>
      <li><label><input type="checkbox" class="sec"> Strip metadata from
        documents before any upload</label></li>
    </ul>
    <p class="muted">Dead man's switch configuration</p>
    <ul class="checklist">
      <li><label><input type="checkbox" class="sec"> Encrypted bundle in two
        independent locations</label></li>
      <li><label><input type="checkbox" class="sec"> Heartbeat interval set
        (e.g. 14 days), grace period defined</label></li>
      <li><label><input type="checkbox" class="sec"> Release instruction file
        names the designated recipient</label></li>
      <li><label><input type="checkbox" class="sec"> Test the switch once
        with a dummy bundle</label></li>
      <li><label><input type="checkbox" class="sec"> Legal counsel briefed on
        the release protocol</label></li>
    </ul>
    <p class="muted" id="secNote">Checklist state is stored locally in your
    browser only.</p>
  </section>

  <!-- 8. Diagnostics report -->
  <section class="panel">
    <h2>8 · Diagnostics Report</h2>
    <button id="diagRun">Run diagnostics</button>
    <pre class="out" id="diagOut"></pre>
  </section>

</main>
<script>
"use strict";
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s == null ? "" : s)
  .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;");
// Some data files are lists, others are objects keyed by company name;
// normalize both shapes to an array.
const toArray = (x) => Array.isArray(x) ? x
  : (x && typeof x === "object" ? Object.values(x) : []);
const badge = (status) => {
  const s = String(status || "unknown");
  const cls = s.includes("verified") ? "ok"
    : (s.includes("gap") || s.includes("unverified")) ? "warn" : "info";
  return `<span class="badge ${cls}">${esc(s)}</span>`;
};

async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(url + " -> HTTP " + res.status);
  return res.json();
}

function setConn(ok) {
  $("connStatus").textContent = ok
    ? "● online (127.0.0.1:8000)" : "● offline / data pending";
  $("connStatus").style.color = ok ? "var(--green)" : "var(--red)";
}

/* ---- 1. whistleblower browser ---- */
async function loadWhistleblowers() {
  try {
    const list = toArray(await getJSON("/api/whistleblowers"));
    window.__wb = list;
    renderWhistleblowers();
    setConn(true);
  } catch (e) { $("wbBody").innerHTML = ""; setConn(false); }
}
function renderWhistleblowers() {
  const q = $("wbSearch").value.trim().toLowerCase();
  const f = $("wbFilter").value.toLowerCase();
  const rows = (window.__wb || []).filter((w) => {
    const hay = [w.name, w.employer, w.role, w.id].join(" ").toLowerCase();
    const vs = String(w.verification_status || w.status || "").toLowerCase();
    return (!q || hay.includes(q)) && (!f || vs.includes(f));
  });
  $("wbBody").innerHTML = rows.map((w) => `<tr>
    <td>${esc(w.name)}</td><td>${esc(w.employer)}</td>
    <td>${esc(w.role)}</td><td>${esc(w.departure_date)}</td>
    <td>${badge(w.verification_status || w.status)}</td></tr>`).join("");
  $("wbCount").textContent = rows.length + " whistleblowers shown";
}

/* ---- 2. corporate tracker ---- */
async function loadCorporations() {
  try {
    const list = toArray(await getJSON("/api/corporations"));
    window.__corp = list;
    const sel = $("corpSelect");
    sel.innerHTML = list.map((c) =>
      `<option>${esc(c.name || c.id || "?")}</option>`).join("");
    $("projSelect").innerHTML = sel.innerHTML;
    $("corpBody").innerHTML = list.map((c) => {
      const sr = c.silence_rate;
      const srText = (sr === undefined || sr === null)
        ? "n/a" : (typeof sr === "number" ? sr.toFixed(2) : esc(sr));
      const hist = Array.isArray(c.response_history)
        ? c.response_history.map((r) =>
            typeof r === "string" ? esc(r)
              : esc(r.date || "") + " " + esc(r.response || r.text || "")).join("; ")
        : (Array.isArray(c.regulatory_actions)
            ? c.regulatory_actions.map((a) =>
                esc(a.agency || "") + ": " + esc(a.status || a.summary || "")).join("; ")
            : esc(c.public_response || c.response || "—"));
      const pred = esc(c.prediction || c.projection || "—");
      return `<tr><td>${esc(c.name || c.id)}</td><td>${srText}</td>
        <td>${hist}</td><td>${pred}</td></tr>`;
    }).join("");
  } catch (e) { $("corpBody").innerHTML = ""; }
}
async function predictCorp() {
  const company = encodeURIComponent($("corpSelect").value);
  $("corpOut").textContent = "requesting…";
  try {
    const p = await getJSON("/api/projection?company=" + company);
    $("corpOut").textContent = JSON.stringify(p, null, 2);
  } catch (e) { $("corpOut").textContent = String(e); }
}

/* ---- 3. regulatory law browser ---- */
async function loadLaw() {
  try {
    const stats = toArray(await getJSON("/api/statutes"));
    $("statBody").innerHTML = stats.map((s) => `<tr>
      <td>${esc(s.citation || s.id)}</td>
      <td>${esc(s.title || s.summary || s.short_name || "—")}</td>
      <td>${badge(s.enforcement_status || s.status || "—")}</td></tr>`).join("");
  } catch (e) { $("statBody").innerHTML = ""; }
  try {
    const cases = toArray(await getJSON("/api/cases"));
    $("caseBody").innerHTML = cases.map((c) => `<tr>
      <td>${esc(c.name || c.case_name || c.id)}</td>
      <td>${esc(c.citation || c.precedent || "—")}</td></tr>`).join("");
  } catch (e) { $("caseBody").innerHTML = ""; }
}

/* ---- 4. source verification dashboard ---- */
async function loadSources() {
  try {
    const list = toArray(await getJSON("/api/sources"));
    $("srcBody").innerHTML = list.map((s) => {
      const url = s.url || s.source_url || "";
      const arch = s.archive_url || "";
      return `<tr><td>${esc(s.title || s.name || s.id)}</td>
        <td>${badge(s.verification_status || s.status || s.rot_status || "gap")}</td>
        <td>${url ? `<a href="${esc(url)}">source</a>` : "—"}</td>
        <td>${arch ? `<a href="${esc(arch)}">archive</a>` : "—"}</td></tr>`;
    }).join("");
  } catch (e) { $("srcBody").innerHTML = ""; }
}

/* ---- 5. filing template compiler ---- */
async function compileFiling() {
  $("ftOut").textContent = "compiling…";
  let claim;
  try { claim = JSON.parse($("ftClaim").value); }
  catch (e) { $("ftOut").textContent = "claim must be valid JSON: " + e; return; }
  try {
    const res = await fetch("/api/filing-template", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agency: $("ftAgency").value, claim: claim }),
    });
    const data = await res.json();
    $("ftOut").textContent = res.ok
      ? (data.template || data.text || JSON.stringify(data, null, 2))
      : ("error " + res.status + ": " + (data.error || JSON.stringify(data)));
  } catch (e) { $("ftOut").textContent = String(e); }
}

/* ---- 6. projection viewer ---- */
async function runProjection() {
  const company = encodeURIComponent($("projSelect").value);
  $("projOut").textContent = "requesting…";
  try {
    const p = await getJSON("/api/projection?company=" + company);
    $("projOut").textContent = JSON.stringify(p, null, 2);
  } catch (e) { $("projOut").textContent = String(e); }
}

/* ---- 7. security checklist: persist locally ---- */
function saveChecks() {
  const state = Array.from(document.querySelectorAll("input.sec"))
    .map((el) => el.checked);
  try { localStorage.setItem("tss_security_checklist", JSON.stringify(state)); }
  catch (e) { /* private mode: persistence unavailable, degrade silently */ }
}
function loadChecks() {
  try {
    const raw = localStorage.getItem("tss_security_checklist");
    if (!raw) return;
    const state = JSON.parse(raw);
    document.querySelectorAll("input.sec").forEach((el, i) => {
      el.checked = Boolean(state[i]);
    });
  } catch (e) { /* ignore corrupted local state */ }
}

/* ---- 8. diagnostics report ---- */
async function runDiagnostics() {
  $("diagOut").textContent = "running…";
  try {
    const d = await getJSON("/api/diagnostics");
    const score = (d.score !== undefined && d.score !== null) ? d.score : "—";
    $("diagOut").textContent = "quality score: " + score + "/100\n\n" +
      JSON.stringify(d, null, 2);
  } catch (e) { $("diagOut").textContent = String(e); }
}

/* ---- wire up ---- */
$("wbSearch").addEventListener("input", renderWhistleblowers);
$("wbFilter").addEventListener("change", renderWhistleblowers);
$("corpPredict").addEventListener("click", predictCorp);
$("ftCompile").addEventListener("click", compileFiling);
$("projRun").addEventListener("click", runProjection);
$("diagRun").addEventListener("click", runDiagnostics);
document.querySelectorAll("input.sec").forEach((el) =>
  el.addEventListener("change", saveChecks));
loadChecks();
loadWhistleblowers();
loadCorporations();
loadLaw();
loadSources();
</script>
</body>
</html>
"""


def _load_data(filename: str) -> object:
    """Return the parsed contents of one data file, cached in memory.

    Raises FileNotFoundError when the file is absent and ValueError when it
    does not parse, so the handler can convert them into a 500 response.
    """
    if filename in _DATA_CACHE:
        return _DATA_CACHE[filename]
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"data file missing: {filename}")
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"data file invalid JSON: {filename} ({exc})") from exc
    _DATA_CACHE[filename] = parsed
    return parsed


def _diagnostics_payload() -> object:
    """Return the diagnostics engine export, importing tss_core on demand.

    Raises RuntimeError when tss_core.tss_diagnostics is not ready, which the
    handler converts into a 500 {"error": "diagnostics module not ready"}.
    """
    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from tss_core.tss_diagnostics import DiagnosticsEngine  # type: ignore
    except Exception as exc:
        raise RuntimeError("diagnostics module not ready") from exc
    return DiagnosticsEngine().export_json()


def _projection_payload(company: str) -> object:
    """Return a departure prediction, importing tss_core on demand.

    Raises RuntimeError when the projection module is unavailable and
    KeyError when the company is unknown to the predictor.
    """
    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from tss_core.tss_projection import DeparturePredictor  # type: ignore
    except Exception as exc:
        raise RuntimeError("projection module not ready") from exc
    return DeparturePredictor().predict_next_departure(company)


def _filing_template_payload(agency: str, claim: dict) -> object:
    """Compile a filing template via tss_core.tss_whistleblower.

    The module-level generate_filing_template is loaded on demand; the call
    falls back from keyword to positional arguments so either signature
    works.  Raises RuntimeError when the module is not ready.
    """
    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from tss_core.tss_whistleblower import generate_filing_template  # type: ignore
    except Exception as exc:
        raise RuntimeError("filing template module not ready") from exc
    try:
        return generate_filing_template(agency=agency, claim=claim)
    except TypeError:
        return generate_filing_template(agency, claim)


class TssRequestHandler(BaseHTTPRequestHandler):
    """HTTP handler serving the SPA and the JSON API routes."""

    server_version = "TSS-v10/1.0"

    def log_message(self, format: str, *args: object) -> None:
        """Suppress per-request logging to keep stdout clean for CI."""
        return

    # -- helpers ------------------------------------------------------------

    def _send_bytes(self, payload: bytes, content_type: str, status: int) -> None:
        """Write a full HTTP response with the given status and content type."""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _send_json(self, obj: object, status: int = 200) -> None:
        """Serialize *obj* to JSON and send it with the given status."""
        payload = json.dumps(obj, indent=2, ensure_ascii=False).encode("utf-8")
        self._send_bytes(payload, "application/json; charset=utf-8", status)

    def _send_error(self, message: str, status: int = 500) -> None:
        """Send a JSON error envelope with the given status."""
        self._send_json({"error": message}, status)

    def _json_body(self) -> dict:
        """Parse the request body as a JSON object; return {} when absent."""
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0:
            return {}
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
        return body if isinstance(body, dict) else {}

    # -- routes -------------------------------------------------------------

    def do_GET(self) -> None:
        """Dispatch GET requests to the SPA or the JSON API routes."""
        if self.path == "/" or self.path.startswith("/index"):
            self._send_bytes(
                INDEX_HTML.encode("utf-8"),
                "text/html; charset=utf-8",
                200,
            )
            return
        if self.path in DATA_ROUTES:
            try:
                data = _load_data(DATA_ROUTES[self.path])
            except (FileNotFoundError, ValueError) as exc:
                self._send_error(str(exc))
                return
            self._send_json(data)
            return
        if self.path == "/api/diagnostics":
            try:
                self._send_json(_diagnostics_payload())
            except RuntimeError as exc:
                self._send_error(str(exc))
            return
        if self.path.startswith("/api/projection"):
            company = self._query_param("company")
            if not company:
                self._send_error("missing company query parameter", 400)
                return
            try:
                self._send_json(_projection_payload(company))
            except RuntimeError as exc:
                self._send_error(str(exc))
            except KeyError as exc:
                self._send_error(str(exc), 404)
            return
        self._send_error(f"unknown route: {self.path}", 404)

    def do_POST(self) -> None:
        """Dispatch POST requests to the filing template compiler."""
        if self.path == "/api/filing-template":
            body = self._json_body()
            agency = str(body.get("agency") or "SEC")
            claim = body.get("claim")
            if not isinstance(claim, dict):
                self._send_error("claim must be a JSON object", 400)
                return
            try:
                result = _filing_template_payload(agency, claim)
            except RuntimeError as exc:
                self._send_error(str(exc))
                return
            if isinstance(result, dict):
                self._send_json(result)
            else:
                self._send_json({"template": str(result)})
            return
        self._send_error(f"unknown route: {self.path}", 404)

    def _query_param(self, name: str) -> str:
        """Return the first value of query parameter *name* (unescaped)."""
        from urllib.parse import parse_qs, urlsplit

        query = parse_qs(urlsplit(self.path).query)
        values = query.get(name) or []
        return values[0] if values else ""


class TssServer(ThreadingHTTPServer):
    """Threaded HTTP server bound to 127.0.0.1 with a fixed banner."""

    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, port: int) -> None:
        """Bind to 127.0.0.1 on *port* with the TSS request handler."""
        super().__init__(("127.0.0.1", port), TssRequestHandler)


def run_once(port: int) -> int:
    """Start the server, self-test two routes with urllib, then shut down.

    Prints the HTTP status codes for "/" and "/api/whistleblowers" and
    returns 0 so CI can verify the server without blocking.  A server that
    fails to start or accept connections returns 1.
    """
    server = TssServer(port)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"TSS v10 self-test on http://127.0.0.1:{port}")
    ok = True
    for path in ("/", "/api/whistleblowers"):
        try:
            with urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as response:
                print(f"GET {path} -> {response.status}")
        except HTTPError as exc:
            # A non-2xx status still proves the server is up (e.g. data
            # files not written by the parallel builder yet).
            print(f"GET {path} -> {exc.code} (server responded)")
        except URLError as exc:
            print(f"GET {path} -> connection failed: {exc}")
            ok = False
    server.shutdown()
    server.server_close()
    return 0 if ok else 1


def serve_forever(port: int) -> None:
    """Serve the dashboard until interrupted; prints the startup banner."""
    server = TssServer(port)
    print(f"TSS v10 serving at http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
    finally:
        server.server_close()


def main(argv: Optional[list] = None) -> int:
    """Parse arguments and run the server in --once or forever mode."""
    parser = argparse.ArgumentParser(description="TSS v10 web dashboard")
    parser.add_argument("--port", type=int, default=8000,
                        help="port to bind on 127.0.0.1 (default: 8000)")
    parser.add_argument("--once", action="store_true",
                        help="self-test and exit instead of serving forever")
    args = parser.parse_args(argv)
    if args.once:
        return run_once(args.port)
    serve_forever(args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())

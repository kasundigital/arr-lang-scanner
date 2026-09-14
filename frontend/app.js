const apiBase = "/api";
const $ = (id) => document.getElementById(id);

let authToken = localStorage.getItem("arr_auth_token") || null;
let instances = [];
let searchTimer = null;

async function api(path, options = {}, auth = true) {
  const opts = { ...options, headers: { ...(options.headers || {}) } };
  if (options.body && !opts.headers["Content-Type"]) opts.headers["Content-Type"] = "application/json";
  if (auth && authToken) opts.headers.Authorization = `Bearer ${authToken}`;
  const res = await fetch(`${apiBase}${path}`, opts);
  if (res.status === 401 && auth) {
    authToken = null;
    localStorage.removeItem("arr_auth_token");
    showLogin();
    throw new Error("Session expired. Please sign in again.");
  }
  return res;
}

async function jsonOrError(res) {
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
  return data;
}

function showOnly(id) {
  ["setup-card", "login-card", "app-cards", "settings-panel"].forEach((x) => $(x).hidden = x !== id);
  $("settings-button").hidden = id !== "app-cards";
  $("logout-button").hidden = !["app-cards", "settings-panel"].includes(id);
}

function showLogin() { showOnly("login-card"); }

async function boot() {
  const status = await jsonOrError(await api("/setup-status", {}, false));
  if (!status.setupComplete) return showOnly("setup-card");
  if (!authToken) return showLogin();
  try {
    await loadInstances();
    showOnly("app-cards");
  } catch (_) { showLogin(); }
}

$("setup-button").onclick = async () => {
  $("setup-error").textContent = "";
  try {
    const data = await jsonOrError(await api("/setup", { method: "POST", body: JSON.stringify({ username: $("setup-username").value.trim(), password: $("setup-password").value }) }, false));
    authToken = data.token; localStorage.setItem("arr_auth_token", authToken);
    await loadInstances(); showOnly("settings-panel");
  } catch (e) { $("setup-error").textContent = e.message; }
};

$("login-button").onclick = doLogin;
$("login-password").addEventListener("keydown", e => { if (e.key === "Enter") doLogin(); });
async function doLogin() {
  $("login-error").textContent = "";
  try {
    const data = await jsonOrError(await api("/login", { method: "POST", body: JSON.stringify({ username: $("login-username").value.trim(), password: $("login-password").value }) }, false));
    authToken = data.token; localStorage.setItem("arr_auth_token", authToken); $("login-password").value = "";
    await loadInstances(); showOnly("app-cards");
  } catch (e) { $("login-error").textContent = e.message; }
}

$("logout-button").onclick = () => { authToken = null; localStorage.removeItem("arr_auth_token"); showLogin(); };
$("settings-button").onclick = async () => { await loadInstances(); renderSettings(); showOnly("settings-panel"); };
$("close-settings").onclick = async () => { await loadInstances(); showOnly("app-cards"); };

async function loadInstances() {
  instances = await jsonOrError(await api("/instances"));
  refreshInstanceSelector();
  $("server-summary").innerHTML = instances.length ? instances.map(i => `<div class="server-chip"><b>${escapeHtml(i.name)}</b><span>${i.kind}</span></div>`).join("") : `<div class="hint">No servers configured yet. Open Settings to add one.</div>`;
}

function refreshInstanceSelector() {
  const type = $("type").value;
  const kind = type === "tv" ? "sonarr" : "radarr";
  const eligible = instances.filter(i => i.kind === kind && i.enabled);
  $("instance").innerHTML = eligible.length ? eligible.map(i => `<option value="${i.id}">${escapeHtml(i.name)}</option>`).join("") : `<option value="">No ${kind} servers configured</option>`;
}
$("type").onchange = () => { refreshInstanceSelector(); $("results").innerHTML = ""; };

$("search").addEventListener("input", () => {
  clearTimeout(searchTimer);
  const q = $("search").value.trim();
  if (q.length < 2) return $("results").innerHTML = "";
  searchTimer = setTimeout(() => runSearch(q), 300);
});

async function runSearch(q) {
  const instanceId = $("instance").value;
  if (!instanceId) return $("error").textContent = "Add and select a server first.";
  $("error").textContent = ""; $("results").innerHTML = `<div class="hint">Searching...</div>`;
  try {
    const items = await jsonOrError(await api(`/search?type=${encodeURIComponent($("type").value)}&instance_id=${instanceId}&q=${encodeURIComponent(q)}`));
    $("results").innerHTML = items.length ? "" : `<div class="hint">No matches.</div>`;
    items.forEach(item => { const b = document.createElement("button"); b.className = "result-item"; b.textContent = `${item.title}${item.year ? ` (${item.year})` : ""}`; b.onclick = () => selectItem(item); $("results").appendChild(b); });
  } catch (e) { $("results").innerHTML = ""; $("error").textContent = e.message; }
}

async function selectItem(item) {
  $("error").textContent = ""; $("selected-title").textContent = `${item.title}${item.year ? ` (${item.year})` : ""} — ${item.instanceName}`;
  try {
    const data = await jsonOrError(await api(`/languages?type=${item.type}&id=${item.id}&instance_id=${item.instanceId}`));
    renderLanguages(data);
    if (item.type === "tv") { $("episodes-card").hidden = false; await loadEpisodes(item.id, item.instanceId); }
    else { $("episodes-card").hidden = true; $("episodes-container").innerHTML = ""; }
  } catch (e) { $("error").textContent = e.message; }
}

function renderLanguages(data) {
  const body = document.querySelector("#langs-table tbody"); body.innerHTML = "";
  const langs = data.audioLanguages || [];
  langs.forEach(x => { const tr = document.createElement("tr"); const code = (x.code || "").toUpperCase(); tr.className = (code === "ENG" || code === "EN") ? "lang-row-eng" : "lang-row-foreign"; tr.innerHTML = `<td>${escapeHtml(x.code || "-")}</td><td>${x.count}</td>`; body.appendChild(tr); });
  $("summary").textContent = data.totalFiles ? `Total files: ${data.totalFiles}. ${langs.length ? `Languages: ${langs.map(x => x.code).join(", ")}` : "No audio language tags found."}` : "No media files found.";
}

async function loadEpisodes(seriesId, instanceId) {
  $("episodes-container").innerHTML = `<div class="hint">Loading episodes...</div>`;
  try { renderEpisodes(await jsonOrError(await api(`/tv/${seriesId}/episodes?instance_id=${instanceId}`))); }
  catch (e) { $("episodes-container").innerHTML = ""; $("error").textContent = e.message; }
}

function renderEpisodes(data) {
  const root = $("episodes-container"); root.innerHTML = "";
  (data.seasons || []).forEach(season => {
    const block = document.createElement("div"); block.className = "season-block";
    block.innerHTML = `<h3>${season.seasonNumber === 0 ? "Season 0 (Specials)" : `Season ${season.seasonNumber}`}</h3><div class="table-wrap"><table class="langs-table compact"><thead><tr><th>Episode</th><th>Title</th><th>Audio</th></tr></thead><tbody></tbody></table></div>`;
    const tbody = block.querySelector("tbody");
    (season.episodes || []).forEach(ep => { const tr = document.createElement("tr"); const langs = ep.audioLanguages || []; tr.className = !ep.hasFile ? "row-nofile" : !langs.length ? "row-nolang" : langs.every(l => ["EN","ENG"].includes(l.toUpperCase())) ? "row-eng" : langs.some(l => ["EN","ENG"].includes(l.toUpperCase())) ? "row-mixed" : "row-foreign"; tr.innerHTML = `<td>S${String(ep.seasonNumber).padStart(2,"0")}E${String(ep.episodeNumber).padStart(2,"0")}</td><td>${escapeHtml(ep.title || "")}</td><td>${!ep.hasFile ? "No file" : escapeHtml(langs.join(", ") || "-")}</td>`; tbody.appendChild(tr); });
    root.appendChild(block);
  });
}

function renderSettings() {
  $("instance-list").innerHTML = instances.length ? instances.map(i => `<div class="instance-row"><div><b>${escapeHtml(i.name)}</b><div class="hint">${i.kind} · ${escapeHtml(i.url)} · ${i.enabled ? "Enabled" : "Disabled"}</div></div><div class="button-row"><button class="btn small" onclick="testInstance(${i.id})">Test</button><button class="btn small" onclick="editInstance(${i.id})">Edit</button><button class="btn small danger" onclick="deleteInstance(${i.id})">Delete</button></div></div>`).join("") : `<div class="hint">No servers configured.</div>`;
}

$("save-instance").onclick = async () => {
  $("settings-message").textContent = "";
  const id = $("instance-id").value;
  const body = { kind: $("setting-kind").value, name: $("setting-name").value.trim(), url: $("setting-url").value.trim(), api_key: $("setting-key").value.trim(), enabled: true };
  try { await jsonOrError(await api(id ? `/instances/${id}` : "/instances", { method: id ? "PUT" : "POST", body: JSON.stringify(body) })); clearInstanceForm(); await loadInstances(); renderSettings(); $("settings-message").textContent = "Server saved."; }
  catch (e) { $("settings-message").textContent = e.message; }
};

window.editInstance = (id) => { const i = instances.find(x => x.id === id); if (!i) return; $("instance-id").value = i.id; $("setting-kind").value = i.kind; $("setting-name").value = i.name; $("setting-url").value = i.url; $("setting-key").value = i.api_key; window.scrollTo({ top: 0, behavior: "smooth" }); };
window.testInstance = async (id) => { try { const d = await jsonOrError(await api(`/instances/${id}/test`, { method: "POST" })); alert(`Connection OK${d.version ? ` — version ${d.version}` : ""}`); } catch (e) { alert(`Connection failed: ${e.message}`); } };
window.deleteInstance = async (id) => { if (!confirm("Delete this server?")) return; await jsonOrError(await api(`/instances/${id}`, { method: "DELETE" })); await loadInstances(); renderSettings(); };

function clearInstanceForm() { $("instance-id").value = ""; $("setting-name").value = ""; $("setting-url").value = ""; $("setting-key").value = ""; }
$("cancel-instance").onclick = clearInstanceForm;

$("save-credentials").onclick = async () => {
  try { await jsonOrError(await api("/credentials", { method: "PUT", body: JSON.stringify({ username: $("new-username").value.trim(), password: $("new-password").value }) })); authToken = null; localStorage.removeItem("arr_auth_token"); alert("Login updated. Please sign in again."); showLogin(); }
  catch (e) { $("credential-message").textContent = e.message; }
};

function escapeHtml(value) { return String(value ?? "").replace(/[&<>'"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[c])); }

boot().catch(e => { $("login-error").textContent = e.message; showLogin(); });

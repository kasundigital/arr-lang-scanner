const apiBase = "/api";

const loginCard = document.getElementById("login-card");
const appCards = document.getElementById("app-cards");
const loginUser = document.getElementById("login-username");
const loginPass = document.getElementById("login-password");
const loginBtn = document.getElementById("login-button");
const loginError = document.getElementById("login-error");

const typeSelect = document.getElementById("type");
const searchInput = document.getElementById("search");
const resultsDiv = document.getElementById("results");
const langsTableBody = document.querySelector("#langs-table tbody");
const selectedTitleDiv = document.getElementById("selected-title");
const summaryDiv = document.getElementById("summary");
const errorDiv = document.getElementById("error");
const episodesCard = document.getElementById("episodes-card");
const episodesContainer = document.getElementById("episodes-container");

let authToken = localStorage.getItem("sr_auth_token") || null;

function updateAuthUI() {
  if (authToken) {
    loginCard.style.display = "none";
    appCards.style.display = "block";
    loginError.textContent = "";
  } else {
    loginCard.style.display = "block";
    appCards.style.display = "none";
  }
}
updateAuthUI();

async function authFetch(url, options = {}) {
  const opts = { ...options };
  opts.headers = opts.headers || {};

  if (authToken) {
    opts.headers["Authorization"] = "Bearer " + authToken;
  }

  const res = await fetch(url, opts);

  if (res.status === 401) {
    authToken = null;
    localStorage.removeItem("sr_auth_token");
    updateAuthUI();
    throw new Error("Unauthorized – please log in again.");
  }

  return res;
}

loginBtn.addEventListener("click", doLogin);
loginPass.addEventListener("keydown", (e) => {
  if (e.key === "Enter") doLogin();
});

async function doLogin() {
  loginError.textContent = "";
  const username = loginUser.value.trim();
  const password = loginPass.value;

  if (!username || !password) {
    loginError.textContent = "Enter username and password.";
    return;
  }

  try {
    const res = await fetch(`${apiBase}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (!res.ok) {
      const txt = await res.text();
      throw new Error(`Login failed: ${txt}`);
    }

    const data = await res.json();
    if (!data.token) {
      throw new Error("No token received from server.");
    }

    authToken = data.token;
    localStorage.setItem("sr_auth_token", authToken);
    loginPass.value = "";
    updateAuthUI();
  } catch (e) {
    loginError.textContent = e.message;
  }
}

let searchTimeout = null;

if (searchInput) {
  searchInput.addEventListener("input", () => {
    const q = searchInput.value.trim();
    if (searchTimeout) clearTimeout(searchTimeout);

    if (q.length < 2) {
      resultsDiv.innerHTML = "";
      return;
    }

    searchTimeout = setTimeout(() => runSearch(q), 300);
  });
}

async function runSearch(q) {
  const type = typeSelect.value;
  errorDiv.textContent = "";
  resultsDiv.innerHTML = "<div class='hint'>Searching...</div>";

  try {
    const res = await authFetch(
      `${apiBase}/search?type=${encodeURIComponent(type)}&q=${encodeURIComponent(
        q
      )}`
    );
    if (!res.ok) {
      const txt = await res.text();
      throw new Error(`Search failed: ${txt}`);
    }

    const items = await res.json();
    renderSearchResults(items);
  } catch (e) {
    errorDiv.textContent = e.message;
    resultsDiv.innerHTML = "";
  }
}

function renderSearchResults(items) {
  resultsDiv.innerHTML = "";

  if (!items || items.length === 0) {
    resultsDiv.innerHTML = "<div class='hint'>No matches.</div>";
    return;
  }

  items.forEach((item) => {
    const btn = document.createElement("button");
    btn.className = "result-item";
    const year = item.year ? ` (${item.year})` : "";
    btn.textContent = `${item.title}${year}`;
    btn.onclick = () => selectItem(item);
    resultsDiv.appendChild(btn);
  });
}

async function selectItem(item) {
  errorDiv.textContent = "";
  langsTableBody.innerHTML = "";
  summaryDiv.textContent = "";
  selectedTitleDiv.textContent = `Selected: ${item.title}${
    item.year ? " (" + item.year + ")" : ""
  }`;

  try {
    const res = await authFetch(
      `${apiBase}/languages?type=${encodeURIComponent(
        item.type
      )}&id=${encodeURIComponent(item.id)}`
    );
    if (!res.ok) {
      const txt = await res.text();
      throw new Error(`Language query failed: ${txt}`);
    }

    const data = await res.json();
    renderLanguages(data);

    if (item.type === "tv") {
      episodesCard.style.display = "block";
      await loadEpisodes(item.id);
    } else {
      episodesCard.style.display = "none";
      episodesContainer.innerHTML = "";
    }
  } catch (e) {
    errorDiv.textContent = e.message;
  }
}

function renderLanguages(data) {
  langsTableBody.innerHTML = "";

  const langs = data.audioLanguages || [];
  const total = data.totalFiles || 0;

  if (total === 0) {
    summaryDiv.textContent =
      "No files found or mediaInfo not available for this item.";
    return;
  }

  langs.forEach((entry) => {
    const tr = document.createElement("tr");
    const code = (entry.code || "").toUpperCase();

    if (code === "ENG" || code === "EN") {
      tr.classList.add("lang-row-eng");
    } else if (code.includes("ENG") || code.includes("EN")) {
      tr.classList.add("lang-row-mixed");
    } else {
      tr.classList.add("lang-row-foreign");
    }

    const tdCode = document.createElement("td");
    const tdCount = document.createElement("td");

    tdCode.textContent = entry.code;
    tdCount.textContent = entry.count;

    tr.appendChild(tdCode);
    tr.appendChild(tdCount);

    langsTableBody.appendChild(tr);
  });

  if (langs.length === 0) {
    summaryDiv.textContent = `Total files: ${total}. No audio language tags found (check Analyze MediaInfo settings in Sonarr/Radarr).`;
  } else {
    const codes = langs.map((l) => l.code).join(", ");
    summaryDiv.textContent = `Total files: ${total}. Audio languages detected: ${codes}.`;
  }
}

async function loadEpisodes(seriesId) {
  episodesContainer.innerHTML = "<div class='hint'>Loading episodes...</div>";

  try {
    const res = await authFetch(
      `${apiBase}/tv/${encodeURIComponent(seriesId)}/episodes`
    );
    if (!res.ok) {
      const txt = await res.text();
      throw new Error(`Episodes query failed: ${txt}`);
    }

    const data = await res.json();
    renderEpisodes(data);
  } catch (e) {
    episodesContainer.innerHTML = "";
    errorDiv.textContent = e.message;
  }
}

function renderEpisodes(data) {
  episodesContainer.innerHTML = "";

  const seasons = data.seasons || [];
  if (seasons.length === 0) {
    episodesContainer.innerHTML = "<div class='hint'>No episodes found.</div>";
    return;
  }

  seasons.forEach((season) => {
    const block = document.createElement("div");
    block.className = "season-block";

    const header = document.createElement("h3");
    header.textContent =
      season.seasonNumber === 0
        ? "Season 0 (Specials)"
        : `Season ${season.seasonNumber}`;
    block.appendChild(header);

    const table = document.createElement("table");
    table.className = "langs-table compact";

    const thead = document.createElement("thead");
    thead.innerHTML = `
      <tr>
        <th>Episode</th>
        <th>Title</th>
        <th>Audio Languages</th>
      </tr>`;
    table.appendChild(thead);

    const tbody = document.createElement("tbody");

    (season.episodes || []).forEach((ep) => {
      const tr = document.createElement("tr");

      const tdEp = document.createElement("td");
      tdEp.textContent = `S${String(ep.seasonNumber).padStart(
        2,
        "0"
      )}E${String(ep.episodeNumber).padStart(2, "0")}`;

      const tdTitle = document.createElement("td");
      tdTitle.textContent = ep.title || "";

      const tdLang = document.createElement("td");
      if (!ep.hasFile) {
        tdLang.textContent = "No file";
        tr.classList.add("row-nofile");
      } else if (!ep.audioLanguages || ep.audioLanguages.length === 0) {
        tdLang.textContent = "-";
        tr.classList.add("row-nolang");
      } else {
        tdLang.textContent = ep.audioLanguages.join(", ");

        const langsUpper = ep.audioLanguages.map((l) => l.toUpperCase());
        const onlyEng = langsUpper.every(
          (l) => l === "ENG" || l === "EN"
        );
        const hasEng = langsUpper.some((l) => l === "ENG" || l === "EN");

        if (onlyEng) {
          tr.classList.add("row-eng");
        } else if (hasEng) {
          tr.classList.add("row-mixed");
        } else {
          tr.classList.add("row-foreign");
        }
      }

      tr.appendChild(tdEp);
      tr.appendChild(tdTitle);
      tr.appendChild(tdLang);

      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    block.appendChild(table);
    episodesContainer.appendChild(block);
  });
}

const healthEl = document.getElementById("health");
const healthLabel = document.getElementById("health-label");
const pinHint = document.getElementById("pin-hint");
const splitEl = document.getElementById("split");
const homeAbbr = document.getElementById("home-abbr");
const awayAbbr = document.getElementById("away-abbr");
const homePct = document.getElementById("home-pct");
const awayPct = document.getElementById("away-pct");
const marketEl = document.getElementById("market");
const marketPct = document.getElementById("market-pct");
const marketLabel = document.querySelector(".market__label");
const banner = document.getElementById("banner");
const idleHint = document.getElementById("idle-hint");
const methodologyBody = document.getElementById("methodology-body");
const limitationsBody = document.getElementById("limitations-body");
const form = document.getElementById("lookup");
const go = form.querySelector(".lookup__go");
const leagueSelect = document.getElementById("league");

function apiError(payload, status) {
  const err = payload && payload.error;
  if (err && err.code) {
    return { code: err.code, message: err.message || "Request failed" };
  }
  return { code: "http_" + status, message: "Request failed (" + status + ")" };
}

async function getJson(url) {
  const res = await fetch(url, { headers: { Accept: "application/json" } });
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = null;
  }
  if (!res.ok) {
    throw apiError(data, res.status);
  }
  return data;
}

function recovery(code) {
  switch (code) {
    case "game_not_found":
      return "That game_id is not in this database. Use an id from the loaded pipeline.";
    case "features_not_found":
      return "The game exists but features for the served feature_version are missing. Re-run the pipeline.";
    case "model_unavailable":
      return "No served pin/artifact. Run the Compose pipeline, then refresh.";
    case "db_unavailable":
      return "Postgres is not reachable. Check Compose and DATABASE_URL.";
    case "invalid_request":
      return "Enter a whole-number game_id.";
    default:
      return "Retry, or inspect GET /v1/health and GET /v1/model.";
  }
}

function syncLeagueButtons() {
  const value = leagueSelect.value;
  document.querySelectorAll(".seg__btn").forEach((btn) => {
    btn.setAttribute("aria-pressed", btn.dataset.league === value ? "true" : "false");
  });
}

async function refreshHealth() {
  try {
    await getJson("/v1/health");
    healthEl.dataset.state = "ok";
    healthLabel.textContent = "Health";
  } catch (err) {
    healthEl.dataset.state = "down";
    healthLabel.textContent = err.code || "API down";
  }
}

function pct(p) {
  if (typeof p !== "number" || Number.isNaN(p)) return "—";
  return Math.round(p * 100) + "%";
}

function barWidth(p) {
  if (typeof p !== "number" || Number.isNaN(p)) return 0;
  return Math.max(0, Math.min(100, p * 100));
}

function ident(name, abbreviation, fallback) {
  const abbr = String(abbreviation || "").trim();
  if (abbr) return abbr;
  const full = String(name || "").trim();
  if (full) return full;
  return fallback;
}

function resetSplit() {
  splitEl.dataset.state = "idle";
  splitEl.style.removeProperty("--home-p");
  homeAbbr.textContent = "HOME";
  awayAbbr.textContent = "AWAY";
  homePct.textContent = "—";
  awayPct.textContent = "—";
  splitEl.setAttribute("aria-label", "Home win probability split. Idle. Enter a game id.");
  marketEl.dataset.state = "idle";
  marketEl.style.removeProperty("--market-p");
  marketPct.textContent = "—";
  marketLabel.textContent = "Market P · Synthetic · not a book";
  idleHint.hidden = false;
  banner.hidden = true;
  banner.textContent = "";
}

function renderPrediction(body) {
  const p = body.p_home_win;
  const awayP = typeof p === "number" ? 1 - p : null;
  const home = ident(body.home_team_name, body.home_team_abbreviation, "HOME");
  const away = ident(body.away_team_name, body.away_team_abbreviation, "AWAY");
  splitEl.dataset.state = "live";
  splitEl.style.setProperty("--home-p", barWidth(p).toFixed(2) + "%");
  homeAbbr.textContent = home;
  awayAbbr.textContent = away;
  homePct.textContent = pct(p);
  awayPct.textContent = pct(awayP);
  splitEl.setAttribute(
    "aria-label",
    "Home win probability " +
      pct(p) +
      " for " +
      home +
      ". Away implied " +
      pct(awayP) +
      " for " +
      away +
      "."
  );
  const hasMarket = typeof body.market_p_home_win === "number";
  marketEl.dataset.state = hasMarket ? "live" : "empty";
  if (hasMarket) {
    marketEl.style.setProperty("--market-p", barWidth(body.market_p_home_win).toFixed(2) + "%");
  } else {
    marketEl.style.removeProperty("--market-p");
  }
  marketPct.textContent = hasMarket ? pct(body.market_p_home_win) : "—";
  marketLabel.textContent =
    body.market_source === "synthetic"
      ? "Market P · Synthetic · not a book"
      : hasMarket
        ? "Market P"
        : "Market P · No snapshot";
  idleHint.hidden = true;
  banner.hidden = true;
  banner.textContent = "";
}

function renderError(err) {
  resetSplit();
  splitEl.dataset.state = "error";
  banner.hidden = false;
  banner.innerHTML =
    "<strong>" +
    escapeHtml(err.code) +
    "</strong>" +
    escapeHtml(err.message) +
    " " +
    escapeHtml(recovery(err.code));
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function sentence(text) {
  const t = String(text || "").trim();
  if (!t) return "";
  const capped = t.charAt(0).toUpperCase() + t.slice(1);
  return /[.!?]$/.test(capped) ? capped : capped + ".";
}

function methodologyCopy(model) {
  const m = model.methodology || {};
  const split = m.split || {};
  const sel = m.selection || {};
  const parts = [
    sentence(m.task),
    sentence(m.temporal_boundary),
    split.scheme ? sentence("Split: " + split.scheme + (split.shuffle === false ? ", no shuffle" : "")) : "",
    sel.metric ? sentence("Selection: " + sel.metric + " on " + (sel.partition || "validation")) : "",
    model.baselines_served === false ? "Baselines are never served." : "",
  ];
  return parts.filter(Boolean).join(" ");
}

async function refreshModel() {
  const league = leagueSelect.value || "nba";
  try {
    const model = await getJson("/v1/model?league=" + encodeURIComponent(league));
    const pin = model.model_version || "unknown pin";
    pinHint.innerHTML = `<span class="chip">${escapeHtml(pin)}</span>`;
    methodologyBody.innerHTML = `
      <p class="meta"><strong>${escapeHtml(pin)}</strong> · dataset ${escapeHtml(model.dataset_version || "—")}</p>
      <p class="methodology">${escapeHtml(methodologyCopy(model))}</p>
      <p class="meta">Model card: ${escapeHtml(model.model_card_ref || "docs/06-design/model-card.md")}</p>`;
    limitationsBody.innerHTML = `<p class="limitations">${escapeHtml(model.limitations || "")}</p>`;
  } catch (err) {
    pinHint.innerHTML = "";
    const bannerHtml = `<p class="banner" role="status"><strong>${escapeHtml(err.code)}</strong> ${escapeHtml(err.message)} ${escapeHtml(recovery(err.code))}</p>`;
    methodologyBody.innerHTML = bannerHtml;
    limitationsBody.innerHTML = bannerHtml;
  }
}

async function runLookup(id) {
  go.disabled = true;
  splitEl.dataset.state = "loading";
  banner.hidden = true;
  try {
    const body = await getJson("/v1/predict?game_id=" + encodeURIComponent(String(id).trim()));
    renderPrediction(body);
  } catch (err) {
    renderError(err);
  } finally {
    go.disabled = false;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(form);
  await runLookup(data.get("game_id"));
});

idleHint.addEventListener("click", (event) => {
  const btn = event.target.closest("[data-fill]");
  if (!btn) return;
  const id = btn.getAttribute("data-fill");
  const input = document.getElementById("game-id");
  input.value = id;
  input.focus();
  runLookup(id);
});

document.querySelectorAll(".seg__btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    leagueSelect.value = btn.dataset.league;
    syncLeagueButtons();
    refreshModel();
  });
});

leagueSelect.addEventListener("change", () => {
  syncLeagueButtons();
  refreshModel();
});

syncLeagueButtons();
resetSplit();
refreshHealth();
refreshModel();

const banner = document.getElementById("banner");
const countEl = document.getElementById("board-count");
const liveEl = document.getElementById("live-games");
const idleHint = document.getElementById("idle-hint");
const health = document.getElementById("health");

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

function showError(err) {
  banner.hidden = false;
  banner.innerHTML =
    "<strong>" +
    (err.code || "error") +
    "</strong> " +
    (err.message || "Request failed");
  health.dataset.state = "down";
}

function nameOf(game, side) {
  return game[side + "_team_name"] || side.toUpperCase();
}

function scoreOf(game, side) {
  const value = game[side + "_score"];
  return value == null ? "—" : String(value);
}

function render(games) {
  liveEl.replaceChildren();
  countEl.textContent = games.length + " live";
  idleHint.hidden = games.length > 0;
  for (const game of games) {
    const row = document.createElement("article");
    row.className = "third";
    const clock = game.clock ? String(game.clock) : "";
    row.innerHTML =
      '<div class="third__home"><p class="third__role">Home</p><p class="third__name"></p><p class="third__score"></p></div>' +
      '<div class="third__away"><p class="third__role">Away</p><p class="third__name"></p><p class="third__score"></p></div>' +
      '<div class="third__meta"><span></span><span class="clock"></span></div>';
    row.querySelector(".third__home .third__name").textContent = nameOf(game, "home");
    row.querySelector(".third__away .third__name").textContent = nameOf(game, "away");
    row.querySelector(".third__home .third__score").textContent = scoreOf(game, "home");
    row.querySelector(".third__away .third__score").textContent = scoreOf(game, "away");
    row.querySelector(".third__meta span").textContent =
      (game.league || "") + " · id " + game.game_id;
    const clockEl = row.querySelector(".clock");
    if (clock) {
      clockEl.textContent = clock;
    }
    liveEl.appendChild(row);
  }
}

async function load() {
  const data = await getJson("/v1/board");
  health.dataset.state = "ok";
  render(data.games || []);
}

load().catch(showError);
window.setInterval(() => {
  load().catch(showError);
}, 30000);

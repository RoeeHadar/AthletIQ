const params = new URLSearchParams(window.location.search);
const user = params.get("user") === "demo-2" ? "demo-2" : "demo-1";
const banner = document.getElementById("banner");
const balanceEl = document.getElementById("balance");
const countEl = document.getElementById("slate-count");
const upcomingEl = document.getElementById("upcoming");
const openEl = document.getElementById("open-stakes");
const form = document.getElementById("lock");
const nextHome = document.getElementById("next-home");
const nextAway = document.getElementById("next-away");
const nextHomeTip = document.getElementById("next-home-tip");
const nextAwayLeague = document.getElementById("next-away-league");
const nextSplit = document.getElementById("next-split");
const demo1 = document.getElementById("user-demo-1");
const demo2 = document.getElementById("user-demo-2");

demo1.setAttribute("aria-pressed", user === "demo-1" ? "true" : "false");
demo2.setAttribute("aria-pressed", user === "demo-2" ? "true" : "false");
if (user === "demo-1") demo1.setAttribute("aria-current", "true");
if (user === "demo-2") demo2.setAttribute("aria-current", "true");

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
}

function clearError() {
  banner.hidden = true;
  banner.textContent = "";
}

function nameOf(game, side) {
  return game[side + "_team_name"] || side.toUpperCase();
}

function renderUpcoming(games) {
  upcomingEl.replaceChildren();
  const rest = games.slice(1);
  for (const game of rest) {
    const row = document.createElement("article");
    row.className = "third";
    row.innerHTML =
      '<div class="third__home"><p class="third__role">Home</p><p class="third__name"></p></div>' +
      '<div class="third__away"><p class="third__role">Away</p><p class="third__name"></p></div>' +
      '<div class="third__meta"><span></span><button type="button" class="producer__take">LOCK</button></div>';
    row.querySelector(".third__home .third__name").textContent = nameOf(game, "home");
    row.querySelector(".third__away .third__name").textContent = nameOf(game, "away");
    row.querySelector(".third__meta span").textContent =
      (game.league || "") + " · " + (game.game_start_time || "") + " · id " + game.game_id;
    row.querySelector("button").addEventListener("click", () => {
      document.getElementById("lock-game").value = String(game.game_id);
      document.getElementById("lock-amount").focus();
    });
    upcomingEl.appendChild(row);
  }
}

function renderOpen(stakes) {
  openEl.replaceChildren();
  for (const stake of stakes) {
    const row = document.createElement("article");
    row.className = "lock-row";
    row.innerHTML =
      "<p></p><button type=\"button\" class=\"producer__take\">CANCEL</button>";
    row.querySelector("p").textContent =
      "Open stake · game " +
      stake.game_id +
      " · " +
      stake.side +
      " · " +
      stake.amount;
    row.querySelector("button").addEventListener("click", async () => {
      try {
        clearError();
        await fetch("/v1/stakes/" + stake.stake_id + "/cancel", {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify({ user }),
        }).then(async (res) => {
          const data = await res.json();
          if (!res.ok) throw apiError(data, res.status);
        });
        await load();
      } catch (err) {
        showError(err);
      }
    });
    openEl.appendChild(row);
  }
}

async function load() {
  const data = await getJson("/v1/slate?user=" + encodeURIComponent(user));
  balanceEl.textContent = "Balance " + data.balance;
  const upcoming = data.upcoming || [];
  const open = data.open_stakes || [];
  countEl.textContent = "Upcoming " + upcoming.length + " · Open " + open.length;
  if (upcoming.length) {
    nextSplit.dataset.state = "live";
    const first = upcoming[0];
    nextHome.textContent = nameOf(first, "home");
    nextAway.textContent = nameOf(first, "away");
    nextHomeTip.textContent = first.game_start_time || "—";
    nextAwayLeague.textContent = (first.league || "") + " · id " + first.game_id;
    document.getElementById("lock-game").placeholder = String(first.game_id);
  } else {
    nextSplit.dataset.state = "idle";
    nextHome.textContent = "HOME";
    nextAway.textContent = "AWAY";
    nextHomeTip.textContent = "—";
    nextAwayLeague.textContent = "—";
  }
  renderUpcoming(upcoming);
  renderOpen(open);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    clearError();
    const amount = Number(document.getElementById("lock-amount").value);
    const body = {
      user,
      game_id: Number(document.getElementById("lock-game").value),
      side: document.getElementById("lock-side").value,
      amount,
      replace: false,
    };
    const res = await fetch("/v1/stakes", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) throw apiError(data, res.status);
    await load();
  } catch (err) {
    showError(err);
  }
});

load().catch(showError);

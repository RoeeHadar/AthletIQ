const healthEl = document.getElementById("health");
const healthLabel = document.getElementById("health-label");
const pinHint = document.getElementById("pin-hint");
const resultEl = document.getElementById("result");
const methodologyBody = document.getElementById("methodology-body");
const limitationsBody = document.getElementById("limitations-body");
const form = document.getElementById("lookup");
const go = form.querySelector(".lookup__go");

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
  return (p * 100).toFixed(1) + "%";
}

function renderPrediction(body) {
  const win = Boolean(body.home_win_pred);
  const p = body.p_home_win;
  const width = typeof p === "number" ? Math.max(0, Math.min(100, p * 100)) : 0;
  const game = escapeHtml(String(body.game_id ?? "—"));
  const features = escapeHtml(body.feature_version || "—");
  resultEl.innerHTML = `
    <p class="caption">Game ${game} · features ${features}</p>
    <div class="table-wrap">
      <table class="box">
        <thead>
          <tr>
            <th>Home win</th>
            <th>P(home win)</th>
            <th>Model</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="win">${win ? "Yes" : "No"}</td>
            <td>
              <div class="bar">
                <span>${pct(p)}</span>
                <span class="bar__track" aria-hidden="true"><span class="bar__fill" style="width:${width}%"></span></span>
                <span class="bar__cap">100%</span>
              </div>
            </td>
            <td>${escapeHtml(body.model_version || "—")}</td>
          </tr>
        </tbody>
      </table>
    </div>`;
}

function renderError(err) {
  resultEl.innerHTML = `
    <p class="banner" role="alert">
      <strong>${escapeHtml(err.code)}</strong>
      ${escapeHtml(err.message)}
      ${escapeHtml(recovery(err.code))}
    </p>`;
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
  try {
    const model = await getJson("/v1/model");
    const pin = model.model_version || "unknown pin";
    pinHint.textContent =
      "Served pin: " + pin + (model.feature_version ? " · " + model.feature_version : "");
    methodologyBody.innerHTML = `
      <p class="meta"><strong>${escapeHtml(pin)}</strong> · dataset ${escapeHtml(model.dataset_version || "—")}</p>
      <p class="methodology">${escapeHtml(methodologyCopy(model))}</p>
      <p class="meta">Model card: ${escapeHtml(model.model_card_ref || "docs/06-design/model-card.md")}</p>`;
    limitationsBody.innerHTML = `<p class="limitations">${escapeHtml(model.limitations || "")}</p>`;
  } catch (err) {
    pinHint.textContent = "";
    const banner = `<p class="banner" role="status"><strong>${escapeHtml(err.code)}</strong> ${escapeHtml(err.message)} ${escapeHtml(recovery(err.code))}</p>`;
    methodologyBody.innerHTML = banner;
    limitationsBody.innerHTML = banner;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const id = new FormData(form).get("game_id");
  go.disabled = true;
  resultEl.innerHTML = `<div class="skeleton" role="status">Looking up game ${escapeHtml(String(id).trim())}…</div>`;
  try {
    const body = await getJson("/v1/predict?game_id=" + encodeURIComponent(String(id).trim()));
    renderPrediction(body);
  } catch (err) {
    renderError(err);
  } finally {
    go.disabled = false;
  }
});

refreshHealth();
refreshModel();

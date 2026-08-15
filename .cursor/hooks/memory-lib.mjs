import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";

export const SWEEP_EVERY = 5;
export const SWEEP_MODEL = "composer-2.5-fast";
export const CONSOLIDATE_MODEL = "cursor-grok-4.5-high";

export function projectRoot(payload = {}) {
  const fromEnv = process.env.CURSOR_PROJECT_DIR || process.env.CLAUDE_PROJECT_DIR;
  if (fromEnv) return fromEnv;
  const roots = payload.workspace_roots;
  if (Array.isArray(roots) && roots[0]) return roots[0];
  return process.cwd();
}

export function memoryDir(root) {
  return join(root, "memory");
}

export function indexPath(root) {
  return join(memoryDir(root), "INDEX.md");
}

export function situationPath(root) {
  return join(memoryDir(root), "situation.md");
}

/** Adapter-tunable. Arbitrary until measured. TTL drops inject, not history. */
export const SITUATION_TTL_MS = 48 * 60 * 60 * 1000;

const TTL_HOURS = /<!--\s*ttl-hours:\s*(\d+)\s*-->/i;
const BULLET_DATE = /^-\s+\*\*(\d{4}-\d{2}-\d{2}(?:T[\d:.]+Z)?)\*\*/;

export function situationTtlMs(text, fallbackMs = SITUATION_TTL_MS) {
  const m = text.match(TTL_HOURS);
  if (!m) return fallbackMs;
  const hours = Number(m[1]);
  return Number.isFinite(hours) && hours > 0 ? hours * 3600 * 1000 : fallbackMs;
}

function bulletStampMs(raw) {
  const iso = raw.includes("T") ? raw : `${raw}T00:00:00Z`;
  const t = Date.parse(iso);
  return Number.isFinite(t) ? t : null;
}

/**
 * Keep preamble + bullets still inside TTL. Undated bullets still inject.
 * Expired dated bullets are omitted from inject only.
 */
export function filterAccessibleSituation(text, nowMs = Date.now(), fallbackTtlMs = SITUATION_TTL_MS) {
  if (!text || !text.trim()) return "";
  const ttlMs = situationTtlMs(text, fallbackTtlMs);
  const chunks = text.split(/(?=^- )/m);
  const kept = [];
  for (const chunk of chunks) {
    if (!chunk.startsWith("- ")) {
      kept.push(chunk);
      continue;
    }
    const m = chunk.match(BULLET_DATE);
    if (!m) {
      kept.push(chunk);
      continue;
    }
    const stamp = bulletStampMs(m[1]);
    if (stamp == null || nowMs - stamp <= ttlMs) kept.push(chunk);
  }
  return kept.join("").trim();
}

export function readAccessibleSituation(root, nowMs = Date.now()) {
  const path = situationPath(root);
  if (!existsSync(path)) return "";
  try {
    const filtered = filterAccessibleSituation(readFileSync(path, "utf8"), nowMs);
    if (!filtered || !/^- /m.test(filtered)) return "";
    return filtered;
  } catch {
    return "";
  }
}

export function statePath(root) {
  return join(memoryDir(root), ".state.json");
}

export function readJson(path, fallback) {
  try {
    if (!existsSync(path)) return structuredClone(fallback);
    return JSON.parse(readFileSync(path, "utf8"));
  } catch {
    return structuredClone(fallback);
  }
}

export function writeJson(path, value) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

export function loadState(root) {
  return readJson(statePath(root), { conversations: {} });
}

export function saveState(root, state) {
  writeJson(statePath(root), state);
}

export function convKey(payload) {
  return (
    payload.conversation_id ||
    payload.session_id ||
    process.env.CURSOR_CONVERSATION_ID ||
    "default"
  );
}

export function getConv(state, key) {
  if (!state.conversations[key]) {
    state.conversations[key] = {
      lastByteOffset: 0,
      sweepCount: 0,
      pendingCompactSweep: false,
      inFlight: null,
      transcriptPath: null,
      lastSweepAt: null,
    };
  }
  return state.conversations[key];
}

export function transcriptPathOf(payload) {
  return (
    payload.transcript_path ||
    process.env.CURSOR_TRANSCRIPT_PATH ||
    null
  );
}

export function transcriptSize(path) {
  if (!path || !existsSync(path)) return 0;
  try {
    return statSync(path).size;
  } catch {
    return 0;
  }
}

export function readIndex(root) {
  const path = indexPath(root);
  if (!existsSync(path)) return "# Memory index\n\n_(empty — no subject files yet)_\n";
  return readFileSync(path, "utf8");
}

export function hasUnread(conv, path) {
  if (conv.pendingCompactSweep) return true;
  if (!path) return false;
  return transcriptSize(path) > (conv.lastByteOffset || 0);
}

export function respond(obj) {
  process.stdout.write(`${JSON.stringify(obj)}\n`);
}

export function buildSweepFollowup({ root, path, offset }) {
  const unreadHint =
    path && existsSync(path)
      ? `Unread transcript: \`${path}\` from byte offset ${offset}. Read only the slice after that offset (or the tail if slicing is awkward).`
      : "No transcript path available — use this conversation’s recent turns as the source.";

  return [
    "MEMORY_LOOP_SWEEP (automated — do this now, then stop)",
    "",
    `1. Launch a Task subagent with model \`${SWEEP_MODEL}\` (Composer 2.5).`,
    "2. Give it the instructions in `.cursor/hooks/memory-prompts/sweep.md`.",
    `3. Project root: \`${root}\``,
    `4. ${unreadHint}`,
    "5. Do not edit `memory/.state.json` yourself — the stop hook finalizes cursor/count after you finish.",
    "6. Do not load the whole memory tree. INDEX first; only subject files you must update.",
    "7. Reply with a one-line summary of what changed (or “nothing durable”).",
  ].join("\n");
}

export function buildConsolidateFollowup({ root }) {
  return [
    "MEMORY_LOOP_CONSOLIDATE (automated — do this now, then stop)",
    "",
    `1. Launch a Task subagent with model \`${CONSOLIDATE_MODEL}\` (Grok).`,
    "2. Give it the instructions in `.cursor/hooks/memory-prompts/consolidate.md`.",
    `3. Project root: \`${root}\``,
    "4. Do not edit `memory/.state.json` — the stop hook clears `inFlight` after you finish.",
    "5. One-line summary only when finished.",
  ].join("\n");
}

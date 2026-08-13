import {
  convKey,
  getConv,
  loadState,
  projectRoot,
  respond,
  saveState,
  transcriptPathOf,
} from "./memory-lib.mjs";

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  const text = Buffer.concat(chunks).toString("utf8").trim();
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch {
    return {};
  }
}

const payload = await readStdin();
const root = projectRoot(payload);
const key = convKey(payload);
const state = loadState(root);
const conv = getConv(state, key);
const tPath = transcriptPathOf(payload);
if (tPath) conv.transcriptPath = tPath;
conv.pendingCompactSweep = true;
saveState(root, state);

respond({
  user_message:
    "Memory loop: compact pending — unread transcript marked for sweep on next agent stop.",
});

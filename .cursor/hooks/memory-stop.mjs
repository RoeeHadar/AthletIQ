import {
  buildConsolidateFollowup,
  buildSweepFollowup,
  convKey,
  getConv,
  hasUnread,
  loadState,
  projectRoot,
  respond,
  saveState,
  SWEEP_EVERY,
  transcriptPathOf,
  transcriptSize,
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
const tPath = transcriptPathOf(payload) || conv.transcriptPath;
if (tPath) conv.transcriptPath = tPath;

const status = payload.status || "completed";
const loopCount = Number(payload.loop_count ?? 0);

// Never chase aborted/error turns into more work.
if (status !== "completed") {
  saveState(root, state);
  respond({});
  process.exit(0);
}

// Finalize a just-finished automated follow-up without re-entering forever.
if (conv.inFlight === "sweep") {
  conv.lastByteOffset = transcriptSize(tPath);
  conv.pendingCompactSweep = false;
  conv.sweepCount = (conv.sweepCount || 0) + 1;
  conv.lastSweepAt = new Date().toISOString();
  const consolidateDue = conv.sweepCount > 0 && conv.sweepCount % SWEEP_EVERY === 0;
  if (consolidateDue && loopCount < 2) {
    conv.inFlight = "consolidate";
    saveState(root, state);
    respond({ followup_message: buildConsolidateFollowup({ root }) });
    process.exit(0);
  }
  conv.inFlight = null;
  saveState(root, state);
  respond({});
  process.exit(0);
}

if (conv.inFlight === "consolidate") {
  conv.inFlight = null;
  saveState(root, state);
  respond({});
  process.exit(0);
}

// Fresh stop: only sweep when there is unread work or a compact pending flag.
const unread = hasUnread(conv, tPath);
if (!unread || loopCount >= 2) {
  saveState(root, state);
  respond({});
  process.exit(0);
}

conv.inFlight = "sweep";
// Keep pendingCompactSweep until finalize so a crashed sweep still retries.
saveState(root, state);

respond({
  followup_message: buildSweepFollowup({
    root,
    path: tPath,
    offset: conv.lastByteOffset || 0,
  }),
});

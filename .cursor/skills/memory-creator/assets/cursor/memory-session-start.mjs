import { indexPath, projectRoot, readIndex, respond } from "./memory-lib.mjs";

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
const index = readIndex(root);

respond({
  additional_context: [
    "## Memory index (always loaded — subject files on demand only)",
    "",
    `Source: \`${indexPath(root)}\``,
    "",
    "Rules: load INDEX only by default. Open a subject file only when the task clearly needs it. Never read the whole memory tree. Before saving anything durable, check this index first.",
    "",
    index.trim(),
  ].join("\n"),
});

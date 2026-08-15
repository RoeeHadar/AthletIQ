import {
  indexPath,
  projectRoot,
  readAccessibleSituation,
  readIndex,
  respond,
  situationPath,
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
const index = readIndex(root);
const situation = readAccessibleSituation(root);

const parts = [
  "## Memory index (always loaded — subject files on demand only)",
  "",
  `Source: \`${indexPath(root)}\``,
  "",
  "Rules: load INDEX only by default. Open a subject file only when the task clearly needs it. Never read the whole memory tree. Before saving anything durable, check this index first. Status belongs in situation.md, not durable policy.",
  "",
  index.trim(),
];

if (situation) {
  parts.push(
    "",
    "## Accessible situation (working memory — not policy)",
    "",
    `Source: \`${situationPath(root)}\``,
    "",
    "TTL has already dropped expired bullets from this inject. Do not treat this as standing rules. Do not copy it into Must never miss.",
    "",
    situation,
  );
}

respond({
  additional_context: parts.join("\n"),
});

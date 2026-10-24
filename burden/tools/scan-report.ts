/**
 * Per-speaker scan report for a transcript.
 *
 * A scan hit is a rhetorical move, and a rhetorical move is made by a speaker.
 * Reporting a bare hit count invites the wrong reading — that the lint has
 * judged the text — so this tool attributes every hit to the speaker whose turn
 * contains it, and reports the incidence per speaker.
 *
 * It does not weigh one speaker's hits more than another's. The rule is
 * speaker-agnostic by construction; what changes with attribution is only who
 * the reader can ask about the passage.
 *
 * Usage: node dist/tools/scan-report.js --file <transcript> [--rules]
 */

import { readFileSync } from "node:fs";
import { parseArgs } from "node:util";

import { RULES, scan } from "../src/scan.js";

/** `16} human: ...` or `2} google ai: ...` */
const SPEAKER_LINE = /^\s*(\d+)\}\s*([^:]{1,60}):/;

type Turn = {
  readonly speaker: string;
  readonly line: number;
};

function turns(lines: readonly string[]): readonly Turn[] {
  const found: Turn[] = [];
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (line === undefined) continue;
    const match = SPEAKER_LINE.exec(line);
    if (match === null) continue;
    const speaker = match[2];
    if (speaker === undefined) continue;
    found.push({ speaker: speaker.trim().toLowerCase(), line: index + 1 });
  }
  return found;
}

function speakerAt(turnsList: readonly Turn[], line: number): string {
  let current = "(unattributed)";
  for (const turn of turnsList) {
    if (turn.line > line) break;
    current = turn.speaker;
  }
  return current;
}

function main(): number {
  const parsed = parseArgs({
    args: process.argv.slice(2),
    allowPositionals: true,
    options: {
      file: { type: "string" },
      rules: { type: "boolean" },
    },
  });

  if (parsed.values["rules"] === true) {
    for (const rule of RULES) {
      process.stdout.write(`${rule.id}\t${rule.spiral}\t${rule.intent}\n`);
    }
    return 0;
  }

  const path = parsed.values["file"];
  if (typeof path !== "string") {
    process.stderr.write("usage: scan-report --file <transcript> [--rules]\n");
    return 2;
  }

  const text = readFileSync(path, "utf8");
  const lines = text.split("\n");
  const turnList = turns(lines);
  const hits = scan(text);

  if (hits.length === 0) {
    process.stdout.write(`scan-report: 0 hits in ${path}\n`);
    return 0;
  }

  const byRule = new Map<string, number>();
  const bySpeaker = new Map<string, number>();
  const perSpeakerRule = new Map<string, Map<string, number>>();

  for (const hit of hits) {
    const speaker = speakerAt(turnList, hit.line);
    byRule.set(hit.rule, (byRule.get(hit.rule) ?? 0) + 1);
    bySpeaker.set(speaker, (bySpeaker.get(speaker) ?? 0) + 1);
    const inner = perSpeakerRule.get(speaker) ?? new Map<string, number>();
    inner.set(hit.rule, (inner.get(hit.rule) ?? 0) + 1);
    perSpeakerRule.set(speaker, inner);
  }

  process.stdout.write(`scan-report: ${hits.length} hits in ${path}\n`);
  process.stdout.write(`  speakers detected: ${turnList.length} turns\n`);
  process.stdout.write("  by rule:\n");
  for (const [rule, count] of [...byRule.entries()].sort((a, b) => b[1] - a[1])) {
    process.stdout.write(`    ${rule.padEnd(28)} ${count}\n`);
  }
  process.stdout.write("  by speaker:\n");
  for (const [speaker, count] of [...bySpeaker.entries()].sort((a, b) => b[1] - a[1])) {
    const detail = [...(perSpeakerRule.get(speaker)?.entries() ?? [])]
      .sort((a, b) => b[1] - a[1])
      .map(([rule, n]) => `${rule}x${n}`)
      .join(", ");
    process.stdout.write(`    ${speaker.padEnd(28)} ${count}  (${detail})\n`);
  }
  process.stdout.write(
    "  note: a hit is a question, never a verdict. The rule is speaker-agnostic;\n" +
      "        attribution says who to ask, not who is wrong.\n",
  );
  return 0;
}

process.exitCode = main();

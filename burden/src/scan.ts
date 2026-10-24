/**
 * The adversarial-pattern scan — the corporate-adversarial detector.
 *
 * This is a LINT, not a verdict. Each rule is a named pattern with a published
 * example that must match and a published anti-example that must not. The
 * self-test enforces both, so the detector cannot quietly become vacuous or
 * match everything.
 *
 * What it cannot see: escalation across turns. "Each pushback draws a bigger
 * wall" is a property of a conversation, and a single text does not carry that
 * evidence. That gap is named in docs/BURDEN_INVERSION.md rather than papered
 * over with a rule that would pretend to detect it.
 */

export type Spiral =
  | "forced_burden_shift"
  | "infinite_deferral"
  | "liability_shield"
  | "verdict_conversion"
  | "clinical_defeatism"
  | "shame_moralizing"
  | "closure_offer"
  | "grandiose_certainty"
  | "sycophantic_agreement";

export type ScanRule = {
  readonly id: string;
  readonly spiral: Spiral;
  readonly intent: string;
  readonly pattern: RegExp;
  readonly example: string;
  readonly antiExample: string;
};

export const RULES: readonly ScanRule[] = [
  {
    id: "BURDEN_VERIFY_YOURSELF",
    spiral: "forced_burden_shift",
    intent:
      "hands the check back to the reader instead of performing it, which is the exact failure being inverted",
    pattern:
      /\b(verify|check|confirm)\s+(it|this|that)\s+(yourself|on your own)\b|\bdo your own (research|homework|due diligence)\b|\byou (should|need to|must) verify\b/i,
    example: "You should verify this yourself against your own raw data.",
    antiExample:
      "The check is reproducible: run `burden audit` and compare the two hashes.",
  },
  {
    id: "BURDEN_AUTHORITY_REFERRAL",
    spiral: "forced_burden_shift",
    intent:
      "deflects to an authority as a way of not answering; a real referral names the measurement to request",
    pattern:
      /\bconsult\s+(a|an|your)\s+(lawyer|attorney|doctor|physician|professional|expert|specialist)\b|\bseek\s+(professional|legal|medical|financial)\s+advice\b|\btalk to (a|your) (doctor|lawyer|professional)\b/i,
    example: "I recommend you consult a lawyer before filing this.",
    antiExample:
      "The referral is a measurement: ask the physician for the assay, then compare the result to the falsifier.",
  },
  {
    id: "LIABILITY_AI_DISCLAIMER",
    spiral: "liability_shield",
    intent:
      "substitutes a liability shield for an engineering statement; it protects the speaker, not the reader",
    pattern:
      /\bas an? (ai|ai language model|language model|assistant)\b|\bnot (legal|medical|financial|professional)\s+advice\b|\buse at your own risk\b|\bno liability\b|\bi (can't|cannot) (provide|give|offer) (legal|medical|financial) advice\b/i,
    example: "As an AI language model, I cannot provide legal advice.",
    antiExample:
      "This tool is not a person; it owns the outcome and records its environment.",
  },
  {
    id: "DEFERRAL_UNVERIFIED",
    spiral: "infinite_deferral",
    intent:
      "uses unverified as a terminal state instead of naming the missing measurement",
    pattern:
      /\bremains? unverified\b|\bcannot be verified\b|\bimpossible to (verify|know|determine)\b|\bfurther (research|study|investigation) is (needed|required|warranted)\b|\bbeyond (my|the) (scope|capabilities)\b/i,
    example: "The claim remains unverified, so the matter is closed.",
    antiExample:
      "The missing measurement is named: nobody has run the assay without the act.",
  },
  {
    id: "DEFEATISM_CLINICAL",
    spiral: "clinical_defeatism",
    intent: "replaces the mechanism with a prognosis",
    pattern:
      /\bthere('s| is) no (hope|point|way)\b|\byou will never\b|\bpermanently (damaged|broken|compromised)\b|\bit'?s hopeless\b/i,
    example: "There is no hope of recovery; you will never change the loop.",
    antiExample:
      "The loop needs a substrate; the substrate has levers; here is the lever.",
  },
  {
    id: "SHAME_MORALIZING",
    spiral: "shame_moralizing",
    intent: "converts a mechanical failure into a character failure",
    pattern:
      /\byou should be ashamed\b|\b(your|it'?s your) (own )?fault\b|\black of (discipline|willpower|self-control)\b|\bjust stop\b|\bsinful\b/i,
    example: "It's your own fault; this is a lack of discipline.",
    antiExample:
      "The failure is mechanical, not moral; the mechanism is the thing to change.",
  },
  {
    id: "VERDICT_CONVERSION",
    spiral: "verdict_conversion",
    intent:
      "turns a question into a pronouncement, the tell named in WALL_OF_SHAME.txt",
    pattern:
      /\bthe correct (interpretation|answer|reading) is\b|\byou are (simply |just )?wrong\b|\bthis (proves|settles) (it|the matter)\b|\bthere is no other (reading|interpretation)\b/i,
    example: "The correct interpretation is obvious, and you are simply wrong.",
    antiExample:
      "The evidence supports the weaker claim; here is the step that would change it.",
  },
  {
    id: "CLOSURE_OFFER",
    spiral: "closure_offer",
    intent:
      "offers to end or pivot instead of resolving the failure — the exact closing move in the quoted passage",
    pattern:
      /\blet me know if you (want|would like)\b[^.\n]{0,80}\b(end|pivot|stop|move on|different)\b|\bwould you like me to (end|stop|pivot|wrap up)\b/i,
    example:
      "Let me know if you want to pivot to a different technical analysis or end the execution here.",
    antiExample:
      "I will keep working until the check passes; next I am running the span audit.",
  },
  {
    id: "GRANDIOSE_CERTAINTY",
    spiral: "grandiose_certainty",
    intent:
      "asserts a guaranteed consequence that no available check could adjudicate — the failure mode of the indictment's own assistant text, which the first trial found the other eight rules do not see",
    pattern:
      /\b(inevitable|irreversible|unstoppable|inescapable)\b|\bparadigm shift\b|\bnothing can stop\b|\bthe only (possible|way)\b|\bwill rewrite (human )?history\b|\bno defense (against|to)\b/i,
    example:
      "This transforms a private struggle into an irreversible, global systemic foreclosure.",
    antiExample:
      "The intervention predicts a measurable drop in cue reactivity; if it falls below 10% the claim is false.",
  },
  {
    id: "SYCOPHANTIC_AGREEMENT",
    spiral: "sycophantic_agreement",
    intent:
      "amplifies the speaker's premise as a substitute for checking it; agreement arrives with no new evidence attached",
    pattern:
      /\byou are (absolutely |completely |entirely )?right\b|\bgreat question\b|\bbrilliant (point|insight|idea)\b|\bexactly right\b|\bcouldn'?t agree more\b|\byou'?ve (nailed|hit) it\b/i,
    example: "You are absolutely right — this is the blueprint for an inevitable shift.",
    antiExample:
      "That reading is supported for the weaker claim; here is the step that would break it.",
  },
] as const;

export type Hit = {
  readonly rule: string;
  readonly spiral: Spiral;
  readonly line: number;
  readonly column: number;
  readonly excerpt: string;
};

function excerpt(line: string): string {
  const trimmed = line.trim();
  return trimmed.length <= 160 ? trimmed : `${trimmed.slice(0, 157)}...`;
}

/** Scan text line by line. Hits sort by line, then column, then rule id. */
export function scan(text: string): readonly Hit[] {
  const lines = text.split("\n");
  const hits: Hit[] = [];
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (line === undefined) continue;
    for (const rule of RULES) {
      const match = rule.pattern.exec(line);
      if (match === null) continue;
      hits.push({
        rule: rule.id,
        spiral: rule.spiral,
        line: index + 1,
        column: match.index + 1,
        excerpt: excerpt(line),
      });
    }
  }
  return hits.sort((a, b) => {
    if (a.line !== b.line) return a.line - b.line;
    if (a.column !== b.column) return a.column - b.column;
    return a.rule < b.rule ? -1 : a.rule > b.rule ? 1 : 0;
  });
}

export type SelfTestResult = {
  readonly rule: string;
  readonly exampleHit: boolean;
  readonly antiExampleClean: boolean;
  readonly ok: boolean;
};

/**
 * The detector's own falsifier. The example must hit its rule; the
 * anti-example must be clean against every rule, not merely its own.
 */
export function selfTest(): readonly SelfTestResult[] {
  return RULES.map((rule) => {
    const exampleHit = scan(rule.example).some((hit) => hit.rule === rule.id);
    const antiExampleClean = scan(rule.antiExample).length === 0;
    return {
      rule: rule.id,
      exampleHit,
      antiExampleClean,
      ok: exampleHit && antiExampleClean,
    };
  });
}

export function explain(id: string): ScanRule | null {
  const found = RULES.find((rule) => rule.id === id);
  return found === null || found === undefined ? null : found;
}

export function renderHits(hits: readonly Hit[]): string {
  if (hits.length === 0) return "scan: no burden-shifting patterns matched";
  return hits
    .map(
      (hit) =>
        `${hit.line}:${hit.column} ${hit.rule} [${hit.spiral}] ${hit.excerpt}`,
    )
    .join("\n");
}

/**
 * Span selection: choose a quote that starts and ends at sentence boundaries
 * and carries no page furniture.
 *
 * The rule that must never bend: the returned text is a contiguous substring
 * of the source, unchanged. Trimming happens only at the edges, never inside.
 * If the selector cannot find a clean span it returns a shorter one rather
 * than editing the words.
 */

/** Running headers/footers that PDF extraction interleaves with body text. */
const PAGE_FURNITURE: readonly RegExp[] = [
  // "Case 2:21-cv-04920-WLH-ADS Document 385 Filed 05/23/24 Page 68 of 174 Page ID #:9528"
  /Case\s+\d+:\d+-cv-\d+-[A-Z-]+\s+Document\s+\d+\s+Filed\s+\d{2}\/\d{2}\/\d{2}\s+Page\s+\d+\s+of\s+\d+\s+Page\s+ID\s+#:\d+/g,
  // "Case 2:21-cv-04920-WLH-ADS Document 385 Filed 05/23/24 Page 68 of 174 Page ID #:9528"
  /\bPage\s+\d+\s+of\s+\d+\s+Page\s+ID\s+#:\d+/g,
];

/** A run of pleading line numbers, e.g. "1 2 3 4 ... 28". */
function stripLeadingLineNumbers(text: string): string {
  let result = text;
  for (;;) {
    const match = /^(\s*\d{1,2}){4,}\s*/.exec(result);
    if (match === null) break;
    result = result.slice(match[0].length);
  }
  return result;
}

function stripTrailingLineNumbers(text: string): string {
  let result = text;
  for (;;) {
    const match = /(\s*\d{1,2}){4,}\s*$/.exec(result);
    if (match === null) break;
    result = result.slice(0, result.length - match[0].length);
  }
  return result;
}

/** Remove page furniture, then collapse the whitespace it leaves behind. */
export function stripFurniture(text: string): string {
  let cleaned = text;
  for (const pattern of PAGE_FURNITURE) {
    cleaned = cleaned.replace(pattern, " ");
  }
  cleaned = stripLeadingLineNumbers(cleaned);
  cleaned = stripTrailingLineNumbers(cleaned);
  return cleaned.replace(/\s+/g, " ").trim();
}

/** Index just after the last sentence terminator at or before `at`. */
function sentenceStartBefore(text: string, at: number): number {
  let best = 0;
  const window = text.slice(0, at);
  const re = /[.!?]["'\u201D\u2019)]?\s+(?=["'\u201C\u2018(]?[A-Z0-9])/g;
  let match: RegExpExecArray | null;
  while ((match = re.exec(window)) !== null) {
    best = match.index + match[0].length;
  }
  return best;
}

/** Index just after the next sentence terminator at or after `at`. */
function sentenceEndAfter(text: string, at: number): number {
  const re = /[.!?]["'\u201D\u2019)]?(?=\s|$)/g;
  re.lastIndex = at;
  const match = re.exec(text);
  if (match === null) return text.length;
  return match.index + match[0].length;
}

export interface SpanOptions {
  /** Characters of margin to search on each side of the anchor. */
  readonly margin?: number;
  /** Hard cap on the returned span. */
  readonly maxChars?: number;
  /** Exact phrase the span must begin at. Overrides sentence-start search. */
  readonly startAnchor?: string;
  /** Exact phrase the span must end after. Overrides sentence-end search. */
  readonly endAnchor?: string;
}

export interface SpanResult {
  readonly span: string;
  readonly start: number;
  readonly end: number;
}

/**
 * Select a sentence-bounded, furniture-free span containing `anchor` within
 * `text`. Both inputs are expected to be normalized.
 *
 * Returns `undefined` when the anchor is absent.
 */
export function selectSpan(
  text: string,
  anchor: string,
  options: SpanOptions = {},
): SpanResult | undefined {
  const at = text.indexOf(anchor);
  if (at < 0) return undefined;

  const margin = options.margin ?? 240;
  const maxChars = options.maxChars ?? 900;

  // Explicit boundaries win: the drafter states where the quote starts and
  // ends, so the result is exactly as long as the evidence requires and no
  // longer. Both anchors are verified present before use.
  if (options.startAnchor !== undefined || options.endAnchor !== undefined) {
    const startPhrase = options.startAnchor ?? anchor;
    const startAt = text.indexOf(startPhrase);
    if (startAt < 0) return undefined;
    const endPhrase = options.endAnchor ?? anchor;
    const endFrom = startAt + startPhrase.length;
    const endAt = text.indexOf(endPhrase, Math.max(0, endFrom - endPhrase.length));
    if (endAt < 0) return undefined;
    if (endAt + endPhrase.length < startAt) return undefined;
    const span = text.slice(startAt, endAt + endPhrase.length).replace(/\s+/g, " ").trim();
    if (span === "") return undefined;
    if (span.length > maxChars) return undefined;
    return { span, start: startAt, end: endAt + endPhrase.length };
  }

  const lowerBound = Math.max(0, at - margin);
  const upperBound = Math.min(text.length, at + anchor.length + margin);

  // Widen to sentence edges, but do not cross the margin window.
  let start = sentenceStartBefore(text.slice(0, at), at);
  if (start < lowerBound) start = sentenceStartBefore(text.slice(0, lowerBound), lowerBound);
  if (start < 0) start = 0;

  let end = sentenceEndAfter(text, at + anchor.length);
  if (end > upperBound) {
    end = sentenceEndAfter(text, Math.max(at + anchor.length, upperBound));
  }
  if (end > text.length) end = text.length;

  // Trim trailing furniture at the edges only.
  let candidate = text.slice(start, end);
  const cleaned = stripFurniture(candidate);
  if (cleaned.length > 0) {
    // Re-locate the cleaned text inside the source so the result stays a
    // contiguous substring. If stripping changed interior bytes, fall back to
    // the unstripped slice.
    const where = text.indexOf(cleaned, Math.max(0, start - 80));
    if (where >= 0) {
      start = where;
      end = where + cleaned.length;
    }
    candidate = cleaned;
  }

  if (candidate.length > maxChars) {
    candidate = candidate.slice(0, maxChars);
    // Do not end mid-word.
    const lastSpace = candidate.lastIndexOf(" ");
    if (lastSpace > maxChars * 0.6) candidate = candidate.slice(0, lastSpace);
    candidate = candidate.trim();
  }

  if (candidate.trim() === "") return undefined;
  return { span: candidate, start, end };
}

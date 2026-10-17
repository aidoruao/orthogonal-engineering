import { readFileSync } from "node:fs";
import { createRequire } from "node:module";

/**
 * Local PDF text extraction for the admission workbench.
 *
 * SCOPE: this module runs only on a machine that holds the L0 corpus. It is
 * never used by CI and never used to publish text. Its single job is to let
 * `admit` check that a quoted span actually appears on the page it cites.
 *
 * pdfjs-dist is loaded lazily so that the structural gate (tsc, the tests,
 * CI) works without the PDF dependency resolved at import time.
 */

export interface PageText {
  /** 1-based page number. */
  readonly page: number;
  readonly text: string;
}

export interface ExtractedDocument {
  readonly pages: readonly PageText[];
  readonly totalPages: number;
}

/**
 * Normalize text for comparison only. Verbatim means verbatim after
 * whitespace and ligature normalization — PDF extraction inserts line breaks
 * and hyphenation that are artifacts of layout, not of the document.
 */
export function normalizeForComparison(text: string): string {
  return text
    .replace(/\r\n?/g, "\n")
    .replace(/\uFB01/g, "fi")
    .replace(/\uFB02/g, "fl")
    .replace(/\uFB00/g, "ff")
    .replace(/\uFB03/g, "ffi")
    .replace(/\uFB04/g, "ffl")
    .replace(/[\u2018\u2019\u201A\u201B]/g, "'")
    .replace(/[\u201C\u201D\u201E]/g, '"')
    .replace(/[\u2013\u2014]/g, "-")
    .replace(/\u00A0/g, " ")
    .replace(/-\n(?=[a-z])/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

interface PdfTextItem {
  readonly str?: string;
  readonly hasEOL?: boolean;
}

interface PdfPageProxy {
  getTextContent(): Promise<{ items: readonly PdfTextItem[] }>;
}

interface PdfDocumentProxy {
  numPages: number;
  getPage(pageNumber: number): Promise<PdfPageProxy>;
}

/** Extract text per page from a PDF file. Throws only on I/O or parse failure. */
export async function extractPdf(path: string): Promise<ExtractedDocument> {
  const require = createRequire(import.meta.url);
  // The legacy build ships a CommonJS entry that runs under Node 22.
  const pdfjs = require("pdfjs-dist/legacy/build/pdf.mjs") as {
    getDocument(options: {
      data: Uint8Array;
      useSystemFonts: boolean;
      disableFontFace: boolean;
      isEvalSupported: boolean;
    }): { promise: Promise<PdfDocumentProxy> };
  };

  const data = new Uint8Array(readFileSync(path));
  const doc = await pdfjs.getDocument({
    data,
    useSystemFonts: true,
    disableFontFace: true,
    isEvalSupported: false,
  }).promise;

  const pages: PageText[] = [];
  for (let pageNumber = 1; pageNumber <= doc.numPages; pageNumber += 1) {
    const page = await doc.getPage(pageNumber);
    const content = await page.getTextContent();
    let text = "";
    for (const item of content.items) {
      if (typeof item.str === "string") {
        text += item.str;
      }
      if (item.hasEOL === true) {
        text += "\n";
      } else {
        text += " ";
      }
    }
    pages.push({ page: pageNumber, text });
  }

  return { pages, totalPages: doc.numPages };
}

export interface QuoteCheck {
  readonly found: boolean;
  readonly page: number;
  /** Why the check failed, when it did. */
  readonly reason?: string;
}

/**
 * Check that `quote` appears verbatim on the given page of the document.
 *
 * This is the falsifier for a claim: if the words are not on the page, the
 * claim is rejected. Extraction artifacts are normalized on both sides, so a
 * line break inside a quoted sentence is not treated as a mismatch.
 */
export function checkQuoteOnPage(
  doc: ExtractedDocument,
  page: number,
  quote: string,
): QuoteCheck {
  if (page < 1 || page > doc.totalPages) {
    return {
      found: false,
      page,
      reason: `page ${page} is outside 1..${doc.totalPages}`,
    };
  }
  const target = normalizeForComparison(quote);
  if (target === "") {
    return { found: false, page, reason: "quote is empty after normalization" };
  }
  const pageText = doc.pages[page - 1];
  if (pageText === undefined) {
    return { found: false, page, reason: `page ${page} was not extracted` };
  }
  if (normalizeForComparison(pageText.text).includes(target)) {
    return { found: true, page };
  }
  return {
    found: false,
    page,
    reason: `quote not found on page ${page} after normalization`,
  };
}

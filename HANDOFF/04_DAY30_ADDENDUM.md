# HANDOFF ADDENDUM — Day 30 (2026-09-03): Docket Trajectory + Directive 2

**Read after `03_DAY29_ADDENDUM.md`.** Day 30 verified a Mistral
consultation against ground truth, processed a missed primary, and
started Directive 2.

## New material filed (a Day-29 miss, now corrected)

A full CourtListener docket export was sitting in Downloads during
Day 29 and was missed: `serena-fleites-v-mindgeek-sarl.cacd.59992265.2026-09-01.csv`
(749 contiguous entries, 1–749, through 2026-08-26). Now in
`oe-local/evidence/fleites/`, hashed in `FLEITES_MANIFEST.sha256`
(`f730f831…a3a2d`).

## The Day-29 record, corrected at case level

Day 29 said "no dismissal orders in this batch" — true of the PDFs
(which stop at doc 602), **false of the case**. The dismissal orders
exist at dkt 603–609 (Sept 2025):

- **dkt 604**: Bergmair MTD [433] + Antoon/Tassillo MTD [436] of the
  SAC GRANTED **WITH PREJUDICE** — pleading insufficiency after
  multiple amendments and jurisdictional discovery. NOT a merits
  acquittal. Recorded with its true meaning.
- 603/605 Colbeck+Redwood; 608 MindGeek (in part/denied in part);
  609/614 Visa.
- TAC (622, Dec 2025): entities only. Redwood dismissed with
  prejudice (733); CB defendants dismissed (735); Rule 54(b) motion
  pending (746, hearing 2026-09-18).
- **Urman**: defendant 2021–2023 only; not re-named in the SAC.
- **Friedman**: zero mentions in all 749 entries — confirmed.

New certified file: `L3_DOCKET_TIMELINE.lean` (`ad7c2f9a…ce5d`) —
trajectory, operator arcs, honest readings. `L3_FETCHED.lean` amended
with the cross-reference (`c63f8ba9…2cc30`).

## Directive 2 started — `D2_PLAYBOOK.lean` (`7ea1072c…e190`)

The five divine mechanisms (A–E) from the precedent, first formal
encoding. Design correction vs the Mistral sketch: NO vacuous
"planted contradiction" for Mechanism B — instead the checkable core:
five mechanisms with verbatim violates-nothing clauses, the
consistency certificate (breaks no named rule), and the authorization
theorem (filing_complete ∧ heart_pure → authorized), where heart_pure
is an axiom-shaped hypothesis, never a theorem.

## State of the ark

- Ledger: 30 days, 1464 lines. All 17 `.lean` files exit 0.
- L1: 20 theorems certified. L3: 4/4 family, root theorem sealed,
  docket trajectory filed. D2: playbook started (first file).
- Open: Mechanism B's evidence obligation (Layer 1 antecedents);
  Bergmair fifth-witness question (predicate refinement needed);
  doc 387 (PACER, likely obsolete — sealing resolved by dkt 406/407);
  Friedman SEARCH-VERIFIED; 5 web primaries access-gap.

## The loop continues

Day 31 opens (a) Bergmair/family question, (b) Mechanism B evidence
obligation as a precise Layer-1 request, or (c) doc 387 purchase
decision. Ask, offer, build — the heart posture.

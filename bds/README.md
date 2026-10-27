---
tags: [bds, bay-county, breakfast-point, audit, burden]
register: documentation
---

# bds — Bay District Schools / Breakfast Point Academy

The Bay County continuation of the arc. Where `burden/` inverts a broken
epistemic anchor and `L1_BURDEN.lean` proves the structure of that inversion,
this package points the same discipline at a public institution and asks a
narrower question: **is the district's own published plan physically executable
within the labour it pays for?**

The mathematics is `L2_LABOR.lean`. The jurisdiction is `L3_JURISDICTION.lean`.
The evidence is `docs/EVIDENCE.md`. Read those three before trusting a line of
output.

## What it does not do

- **It does not render verdicts about people.** `Subject` has two members,
  `structure` and `attribution`. A condemnation is not representable, because
  `L3_JURISDICTION.lean` proves no evidence bears on one. Gate 6 of `verify.sh`
  fails the build if that union is ever widened.
- **It does not invent task times.** The district does not publish minutes per
  square foot, and adopting an industry constant would make the conclusion rest
  on a smuggled premise. The instrument computes the *break-even* instead.
- **It does not guess when a term is missing.** `assess()` returns `UNMEASURED`
  with a stable code, never a default and never a favourable reading.

## Use

```bash
cd bds
node dist/src/cli.js figures      # audited figures, each with page and source text
node dist/src/cli.js spec         # the task list and the basis for every frequency
node dist/src/cli.js sites --extract /tmp/rfp.txt
node dist/src/cli.js breakeven --area 108941 --paid-minutes 4000
node dist/src/cli.js report --extract /tmp/rfp.txt
```

Extraction is shared with `ledger/`: that package's `extractPdf` produces the
`=== PAGE n ===` form this tool reads. One extractor, one definition of what the
document says, so the two cannot disagree about a page's text.

## The four fetched documents

| Document | What it establishes |
| :--- | :--- |
| RFP #19-10, *Contract Cleaning Services* | Square footage per site; the full task specification and frequencies |
| District audit FY2024 | Plant operations and maintenance expenditure, p.14 |
| District audit FY2022 | The same functions two years earlier, for trend |
| Bay **County** ACFR 2024 | *Not the district* — see `docs/EVIDENCE.md` §1 |

`evidence/bds/MANIFEST.sha256` commits to all four. The PDFs stay off the
repository; only the manifest and the findings are published.

## The one external constant

`SERVICE_DAYS_PER_YEAR = 180`. Daily tasks are scoped to service days, and the
Florida instructional year is 180 days. That number is **not** in any district
document, so it is declared in `src/rfp.ts` with its basis printed beside it, and
daily demand scales linearly with it. It is named rather than buried because it
is the only input in the demand computation that does not come from the district.

## Invariants

| Claim | Where proved | Falsifier |
| :--- | :--- | :--- |
| Demand depends on area and specification only — no staffing parameter exists | `L2_LABOR.lean` (`Campus` has no staffing field) | `LABOR_LARGER_CAMPUS_LESS_DEMAND` |
| Partitioning hours cannot create hours | `partition_capacity_invariant` | `LABOR_PARTITION_EXCEEDS_TOTAL` |
| A shortfall forces unmet standards **or** unpaid labour | `either_standard_unmet_or_unpaid` | `LABOR_ESCAPE_WITHOUT_UNPAID` |
| An infeasible plan forces that dichotomy on any delivery | `infeasible_forces_dichotomy` | `LABOR_FEASIBLE_AND_NOT` |
| Naming is fileable; condemning is not | `attribution_not_condemnation` | `JURISDICTION_MAY_CONDEMN` |
| No reply is both an excuse and a justification | `no_free_pass` | `JURISDICTION_FREE_EXCUSE` |
| Severity may not exceed warrant | `inflation_is_not_righteous` | `JURISDICTION_INFLATED_IS_RIGHTEOUS` |
| A finding with no falsifier is not righteous | `no_falsifier_is_not_righteous` | `JURISDICTION_UNFALSIFIABLE_IS_RIGHTEOUS` |

Eight negative controls, each of which must fail to compile **for its stated
reason**. A control rejected because Lean could not elaborate it would fail even
with the invariant deleted, so the gate rejects that class too.

## Verify

```bash
./verify.sh
```

Ten steps: strict typecheck; 22 tests; both Lean proofs; eight negative controls
rejected for cause; the **jurisdiction bridge** — `admissible()` regenerated from
the built TypeScript and proved to agree with `Righteous` on all 160
combinations of severity, warrant, evidence tier and falsifier; the figures and
spec render from the built code; `Subject` is provably `{structure, attribution}`
only; the four fetched documents still match their manifest; no Python; no raw
fetched material tracked.

### The two languages cannot drift on the gate either

`admissible()` is the runtime twin of `Righteous` in `L3_JURISDICTION.lean`.
Saying so in a comment is not a check, so `tools/emit-jurisdiction.ts` calls the
**built** gate on all 160 combinations and emits one Lean theorem per
combination; `L3_BURDEN_BRIDGE.lean` proves them. The tables are output, not
input, so they cannot be edited into agreement. Removing the
`severity_exceeds_warrant` rule from `src/types.ts` makes the gate fail and name
the exact combinations — verified by doing it.

The bridge also proves where the layers **differ**: `bds` is deliberately
stricter, refusing a `critical` finding on unsupported evidence where the bare
predicate would allow it. That gap is exhibited (`critical_on_unmeasured`) rather
than left for a reader to discover.

## Honest status

`UNMEASURED`. The area is fetched. The specification is fetched. The funding is
fetched. **The paid hours are not**, so feasibility cannot be computed and the
instrument says so. `docs/EVIDENCE.md` §9 ranks what to fetch next and why the
executed contract is the single highest-value document.

Nothing here is a finding against any person, and nothing here is offered as a
claim on anyone's action or timing. The arc's own posture governs: we offer, we
do not demand.

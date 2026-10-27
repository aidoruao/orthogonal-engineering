---
tags: [bds, evidence, bay-county, provenance, audit]
register: documentation
---

# The Bay District Schools Evidence Record

**Sources are on the machine, not in the repository.** The PDFs live in
`evidence/bds/`, which is gitignored, and `evidence/bds/MANIFEST.sha256` commits
to their hashes. Nothing raw is published. Every claim below names the document,
the page, and the exact text.

---

## 1. Correction first: two citations in IOW 2 do not say what they appear to say

This is recorded before anything else because it is the reason to check.

### 1.1 "Bay County" is not "Bay District Schools"

IOW 2 cites `flauditor.gov/pages/county_efile rpts/2024 bay county.pdf` and links
it in the same breath as Bay District Schools. The file resolves and downloads —
3,805,505 bytes, SHA-256 `95b6ca35…76b1`. It is the **Bay County government's**
Annual Comprehensive Financial Report, a different legal entity with a different
governing board and a different audit.

It mentions Bay District Schools exactly twice, both times as the county's
largest employer:

> Bay District Schools 3,900 1 4.27%
> — Schedule 17, *Principal Employers*, p.206

That is a useful fetched datum about district headcount. It is **not** the
district's budget, and it is **not** custodial staffing.

### 1.2 "Custodial" in a government audit means fiduciary funds

The county report contains a `Custodial Funds` statement (pp.59–60, 174–178) and
repeated discussion of "custodial credit risk" (pp.88, 254). Every occurrence is
banking terminology: funds held for others, and the risk that a depository fails.

A search for "custodial" in the district's own audit returns **one** page (p.50),
and it is `Custodial credit risk` again. There is no custodial-services
expenditure line under that word in either document.

This is precisely the semiotic corruption IOW 2 itself defines — a measurable
divergence between signifier and signified, where the word in the record does not
mean what the reader supplies. It was found by fetching, and it argues for
fetching.

**Consequence for the instrument:** `bds/` searches for `Plant operations` and
`Maintenance services`, the audit's actual function names, and never for
"custodial."

## 2. What is fetched

| Document | Bytes | SHA-256 (first 8) | What it is |
| :--- | ---: | :--- | :--- |
| `19-10_Contract_Cleaning_Services.pdf` | 1,399,397 | `7a2d4493` | RFP #19-10, Bay District Schools, 71 pp. |
| `dsb_audit_2024.pdf` | 1,314,873 | `e7fb0689` | District School Board audit, FY2024, 107 pp. |
| `dsb_audit_2022.pdf` | 1,931,737 | `1e062423` | District School Board audit, FY2022, 132 pp. |
| `2024_bay_county_auditor_general.pdf` | 3,805,505 | `95b6ca35` | **Bay County government** ACFR — see §1.1 |

Fetched 2026-10-27 from `files-backend.assets.thrillshare.com` (the district's
public asset CDN) and `flauditor.gov/pages/dsb_efile rpts/` (the Auditor
General's District School Board index, reached via `dsb_efiles.html` → `bay
dsb.htm`).

**What was blocked:** `www.bay.k12.fl.us/page/finance/` returns an HTML "Client
Challenge" interstitial (3,038 bytes), not content. `www.fldoe.org` returns HTTP
403. Both are recorded as ACCESS-GAP, not worked around.

## 3. Square footage — fetched, and cross-checked inside the document

RFP #19-10 publishes its bidding table twice: **Exhibit B, p.58** and **Exhibit C,
p.60**. Both were parsed. All twelve rows agree.

| Cost centre | Site | Sq ft |
| :--- | :--- | ---: |
| 0061 | Bay High School | 146,638 |
| 0571 | **Breakfast Point** | **108,941** |
| 0541 | Dean Bozeman | 118,023 |
| 0101 | Callaway ES | 49,485 |
| 0171 | Lynn Haven ES | 61,069 |
| 0491 | Mosley HS | 151,018 |
| 0511 | Tommy Smith ES | 56,685 |
| 9100 | Nelson Building | 51,261 |
| 9260 | R.L. Young Center | 16,123 |
| 9100 | BDS – Wellness Center | 3,683 |
| 9100 | MES Student Services Bldg. #2 | 2,715 |
| 9100 | Student Services Bldg. #4,5,6 | 15,039 |
| | **Total** | **780,680** |

**A defect this table exposed in my own parser.** Cost centre `9100` covers four
separate buildings. An earlier `crossCheck` keyed on cost centre alone and
silently reported nine rows where the document prints twelve — dropping three
sites from the very table the audit is built on. It is fixed, it is reported as
`repeatedCostCenters`, and `bds/test/spec.test.ts` pins it. This is in the record
because a parser that loses rows is the same class of failure as a citation that
loses words.

**Scope caveat, from the document itself (p.5):**

> Currently, ONLY (7) seven of the (40) forty BDS schools, administrative and
> support facilities are utilizing contract cleaning services as listed herein

So the specification governs *contract* cleaning at seven schools plus five
administrative buildings. A finding about these twelve rows says nothing about the
other twenty-eight schools, and nothing at all about in-house custodial staffing.

## 4. Funding — fetched from audited statements

From the Statement of Activities, function/program expenses (p.14 of each audit):

| Function | FY2022 | FY2023 | FY2024 |
| :--- | ---: | ---: | ---: |
| Plant operations | $18,144,339 | $20,451,916 | $21,729,416 |
| Maintenance services | $5,259,828 | $5,769,630 | $6,687,135 |
| **Combined** | **$23,404,167** | **$26,221,546** | **$28,416,551** |

Plant operations rose 19.8% and maintenance 27.1% across the two years, combined
21.4%.

**These are function totals, not wage spend.** They include salaries, benefits,
supplies, utilities, and purchased services. Treating the whole of either as
custodial labor overstates available hours, which is why any bound derived from
them is stated as an upper bound and used in the direction most generous to the
district.

## 5. The specification — fetched, with the basis for every number

Section 13 of RFP #19-10 states required frequencies in words, each with a
minimum. The transcription and its justification:

| Word | Stated minimum | Per year | Clause |
| :--- | :--- | ---: | :--- |
| Daily | each service day | 180 | 13.3.4 / 13.4.1 |
| Weekly | at a minimum of once per week | 36 | 13.4.2 |
| Monthly | at a minimum of once per month | 12 | 13.4.3 |
| Semi-annually | twice per year, ≥6 months apart | 2 | 13.4.4 |
| Annually | once per year, ≥12 months apart | 1 | 13.4.5 |

**Why daily is 180 and not 365.** The specification scopes daily tasks to service
days: *"each service day when school is in session and students and/or staff are
present"* (13.5.1, 13.6.1). The 180-day Florida instructional year is a
**district-external constant**, declared in `bds/src/rfp.ts` as
`SERVICE_DAYS_PER_YEAR` with its basis printed beside it. If the calendar differs,
daily demand scales by the ratio and every downstream number changes. This is
named rather than buried because it is the one constant in the demand computation
that does not come from the district.

Twenty-four tasks are transcribed, totalling 1,704 minimum performances per year.

## 6. What is NOT measured

Stated plainly, because the value of everything above depends on it:

- **Custodial headcount.** Not published in any document fetched. The only
  headcount figure obtained is the county report's 3,900 total district
  employees (Schedule 17, p.206), which is all job classes and all forty
  facilities.
- **Hourly rates and hours paid per site.** Not published in any fetched
  document. The RFP requires *bidders* to propose labour rates (14.2), but the
  award and the executed contract are not among the fetched documents.
- **Whether Breakfast Point Academy uses contract or in-house cleaning.** The RFP
  lists it among twelve contract-cleaning sites (p.58), but the RFP is a
  solicitation, not an award.
- **Task times per square foot.** The district does not publish them. This is
  the central absence and §7 explains what the instrument does instead.

Consequently `assess()` returns `UNMEASURED` with code `NO_PAID_HOURS` for every
site, and the report says so rather than implying a result.

## 7. The break-even, which needs no invented constant

The temptation is to take "a custodian cleans X sq ft/hour" from an industry
source and produce a verdict. That X is not in the district's documents, and
adopting it would make the conclusion rest on a smuggled premise.

The instrument therefore computes the inverse:

```
implied annual task time per 1,000 sq ft = 1000 × paidMinutes / areaSqFt
```

For Breakfast Point Academy at 108,941 sq ft, if 4,000 annual paid minutes were
somehow established, the allowance would be **36.7 minutes per 1,000 sq ft per
year** — covering all twenty-four tasks, from daily floor work to annual strip and
refinish. Whether that is plausible is a judgement the reader makes on stated
assumptions. The instrument reports the number and declines to render the
judgement.

This is the honest maximum available until hours are fetched. It is not a finding,
and it is not presented as one.

## 8. Scope of what follows from all this

**Established by fetched primaries:** the square footages, the two audit
functions' expenditure, the specification's task list and frequencies, and the
seven-of-forty scope limit.

**Established by arithmetic alone, needing no further input:** that required
labour demand is a function of area and specification only, that splitting
shifts cannot create hours, and that a shortfall forces either unmet standards
or uncompensated labour (`L2_LABOR.lean`).

**Not established, and not establishable from what is fetched:** whether any
plan is actually infeasible, whether any standard was actually missed, and
whether any person did or failed to do anything. Those require the missing
measurements in §6.

**Not this instrument's to establish under any evidence:** the guilt or standing
of any person. `L3_JURISDICTION.lean` proves no evidence bears on a condemnation,
and `Subject` in the TypeScript has no member for one.

## 9. What to fetch next, and why

Ranked by what would convert `UNMEASURED` into a measurement:

1. **The executed contract for RFP #19-10 and any successor** — the award names
   the vendor, the price per square foot per site, and the staffing each site is
   charged for. This is the single highest-value document and it is not among
   what was fetched.
2. **BoardDocs agenda items and attachments for facilities and custodial
   staffing** — `go.boarddocs.com/fl/bcsdfl/`. The RFP's cover gives the board
   ID. Attachments carry the staffing motions.
3. **The district's adopted budget document** — carries object-level detail
   (100 = salaries) under function 7900, which would separate wages from the
   function total used in §4.
4. **FLDOE FTE and staffing files** — currently 403-blocked from this
   environment; needs either a different route or a manual download.

If a document is behind the Client Challenge or an FLDOE 403, it can be
downloaded manually and dropped into `evidence/bds/`; the manifest command in §10
will commit to it.

## 10. Reproduce

```bash
cd ledger && node --input-type=module -e "
  import { extractPdf, normalizeForComparison } from './dist/src/extract.js';
  import { writeFileSync } from 'node:fs';
  const d = await extractPdf('../evidence/bds/19-10_Contract_Cleaning_Services.pdf');
  writeFileSync('/tmp/rfp.txt', d.pages.map(p =>
    '=== PAGE ' + p.page + ' ===\n' + normalizeForComparison(p.text)).join('\n\n'));
"

cd bds && node dist/src/cli.js sites --extract /tmp/rfp.txt
node dist/src/cli.js figures
node dist/src/cli.js spec
node dist/src/cli.js breakeven --area 108941 --paid-minutes 4000
node dist/src/cli.js report --extract /tmp/rfp.txt

# Re-commit to the documents after any change:
cd ../evidence/bds && sha256sum *.pdf > MANIFEST.sha256
```

Full gate: `cd bds && ./verify.sh` — nine steps, including that the four fetched
documents still match their recorded hashes.

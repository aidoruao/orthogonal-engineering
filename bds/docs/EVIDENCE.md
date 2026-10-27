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

---

# Addendum 1 and the FISH reports — 2026-10-27, second fetch

Four more files arrived from the district's archived-bids page. One of them
**changes an earlier conclusion in this document**, so it comes first.

## 10. Correction: the base RFP was already superseded when I read it

RFP 19-10 §5 says addenda are the only official method of clarification and that
failure to acknowledge one "may result in rejection of the bid." I read the base
RFP and reported twelve sites. **Addendum No. 1, dated 2019-05-16, deletes one of
them:**

> Change original RFP 19-10, page 5 of 71, delete Bay High School from services.
> Change original RFP 19-10 Exhibit B, page 58 of 71, delete Bay High School from
> pricing sheet. Change original RFP 19-10 Exhibit C, page 60 of 71, delete Bay
> High School from pricing sheet

`RFP-19-10-ADDENDUM-1-Contract-Cleaning-Services.pdf`, 271,775 bytes,
SHA-256 `373aef5a…ea10e`, pp.1–2.

**Operative scope is therefore 11 sites, not 12**, and excludes Bay High School
(0061, 146,638 sq ft). `bds scope` now applies the amendment and reports both the
base table and the removal:

```
base table rows:      12
removed by addendum:  1
  - 0061 Bay High School (146,638 sq ft) by RFP-19-10-ADDENDUM-1
operative sites:      11
operative area:       634,042 sq ft
```

The instrument was reporting a site the district had already removed. That is
recorded here because it is the exact failure this project exists to catch, and
it was caught in my own instrument rather than in someone else's.

**General lesson for the next session:** the base document is not the operative
document. Where a solicitation warns that addenda exist, the audit is incomplete
until they are fetched. `AMENDMENTS` in `bds/src/addendum.ts` is the register.

## 11. The FISH reports — what Q2 of the addendum was pointing at

Addendum 1 Q2 asks for "FISH reports of facilities" and answers that they were
uploaded to the district site. `refishreports.zip` (1,292,110 bytes,
`eb4614fb…8293`) contains **eight** FISH reports, one per site, all dated
2019-05-16.

FISH is the **Florida Inventory of School Houses** — the state facility
inventory. Each report gives, per building and room by room: room number, net
square footage, FISH design code, room function, student and staff stations,
**floor covering**, year of construction, and condition.

| Report | Bytes | SHA-256 (8) |
| :--- | ---: | :--- |
| `B. Point 5-16-19.pdf` | 217,794 | `c9bd3d90` |
| `Bozeman 5-16-19.pdf` | 345,595 | `f32d46b1` |
| `Callaway 5-16-19.pdf` | 185,020 | `1a49eed8` |
| `Lynn Haven 5-16-19.pdf` | 168,329 | `0c3b6439` |
| `Mosley 5-16-19.pdf` | 276,516 | `d56aab9c` |
| `Nelson Bldg 5-16-19.pdf` | 119,586 | `6a12b573` |
| `Tommy Smith 5-16-19.pdf` | 182,365 | `758eca81` |
| `Wellness, RL Young Service, SS Bldg 2,4,5,6.pdf` | 162,230 | `1425d294` |

`31.1-Tommy-Smith-ES.pdf` (803,937 bytes, `9eb2519e…d9b3`) is the **floorplan**
requested in Addendum 1 Q1. It is a single-page image with no extractable text,
so it is recorded as LOCATED and not parsed.

### Breakfast Point Academy, room by room

`B. Point 5-16-19.pdf`, 33 pages, MSID **571**, "BREAKFAST POINT SCHOOL",
PK–08, FTE 1087.89 (2017/18), capacity 1,617, on 40 acres.

**388 rooms parsed. The parse is validated against the report's own printed
subtotals, building by building, and reconciles exactly:**

| Building | Name | Printed subtotal | Parsed rooms |
| :--- | :--- | ---: | ---: |
| 1 | Administration/Media | 30,186 | 30,186 |
| 2 | Food Service/Multi-Purpose | 25,281 | 25,281 |
| 3 | Middle School Classrooms | 22,577 | 22,577 |
| 4 | Elementary Classrooms | 73,280 | 73,280 |
| 5 | Gymnasium | 24,351 | 24,351 |
| 100 | MODULARS | (no subtotal printed) | 9,837 |
| | **Total** | **175,675** | **185,512** |

That reconciliation is the reason to trust the row parse. It did not hold on the
first two attempts — the parser lost 26 rows to a repeated column caption and 87
more to a three-digit-only design-code rule — and the subtotals are what exposed
it. Both repairs are pinned in `bds/test/fish.test.ts`.

Floor coverings, which is what the RFP's task list actually operates on:

| Covering | Area |
| :--- | ---: |
| Composition tile | 120,030 |
| Carpet | 21,843 |
| Concrete | 21,108 |
| Ceramic tile | 9,386 |
| Other | 8,722 |
| Quarry tile | 4,423 |

Task surfaces: **86 restrooms**, **68 classrooms**, 24 circulation areas.

## 12. A second discrepancy, and why it is left unresolved

The pricing sheet gives **108,941 sq ft** for Breakfast Point Academy (Exhibit B
p.58, Exhibit C p.60 — the two pages agree with each other). The FISH report,
from the same solicitation period, gives **185,512** net sq ft for the same
campus, MSID 571.

I tried to close that gap rather than assume wrongdoing, by excluding space a
cleaning contract would not normally service:

| Exclusion | Area excluded | Remaining |
| :--- | ---: | ---: |
| — (gross net) | — | 185,512 |
| Covered walkways | 10,882 | 174,630 |
| Mechanical rooms | 9,335 | 165,295 |
| Storage | 8,290 | 157,005 |
| Covered play area | 6,670 | **150,335** |

**The gap does not close.** Best-case for reconciliation, 150,335 sq ft against a
bid area of 108,941 — still 38% larger, a residual of 41,394 sq ft.

I stopped there deliberately. Continuing to remove categories until the two
numbers meet would be fitting the data to a conclusion, which is exactly the
motivated reasoning this project forbids. The instrument reports the residual and
names what would settle it:

> RFP 19-10 §14.1.2 describes the bid area only as "the most recent and up to
> date information available to BDS", and §12.2.2 says it is accurate "to the
> best knowledge of BDS" and "for contract and bidding purposes only." Settling
> this needs either the executed contract's scope schedule or a district
> statement of which rooms the bid area excludes.

**What is established:** two documents the district published for the same
solicitation state areas for the same campus that differ by 76,571 sq ft gross
(66,734 against the printed subtotals), and the difference survives every
exclusion that is defensible without further information.

**What is not established:** which figure governs, whether either is wrong, and
whether anything follows from it. An area figure being inconsistent is not
evidence that anyone did anything.

## 13. The staffing question is still open

The FISH reports contain no hours, no staffing, and no custodial data. A search
of the Breakfast Point report for hour/shift/staff/custodial returns nothing but
"FTE" in the enrolment table.

So `assess()` still returns `UNMEASURED` / `NO_PAID_HOURS`. Five documents have
been fetched and the figure that would convert this into a measurement is still
not among them. `§9` remains the fetch list and its priority order is unchanged:
the executed contract is first.

## 14. Reproduce the second fetch

```bash
cd bds
node dist/src/cli.js scope     --extract /tmp/rfp.txt      # 11 operative sites
node dist/src/cli.js fish      --fish '../evidence/bds/site-reports/B. Point 5-16-19.txt'
node dist/src/cli.js reconcile --fish '../evidence/bds/site-reports/B. Point 5-16-19.txt' \
                                --bid-sqft 108941          # exits 1: gap not closed
```

`reconcile` exits 1 by design when the gap does not close. That exit is the
finding, not a failure of the tool.

---

# §15. Where the money went — and what the auditor said about it

Everything above measured quantities. None of it asked whether anyone who
examined the books concluded that something was wrong. The answer is in the
auditors' own schedules: **six findings across two audit cycles, four with dollar
amounts, totalling $3,666,230.**

These are the strongest evidence in this package. They are not this
instrument's inferences; they are findings by Carr, Riggs & Ingram, LLC under
Government Auditing Standards, dated 24 March 2025 (FY2024), with statutory
citations.

## The findings

### FY2022 — `dsb_audit_2022.pdf`

| Finding | Type | Amount | Subject |
| :--- | :--- | ---: | :--- |
| 2022-001 | Material weakness | — | Lack of appropriate staffing and journal entry review |
| 2022-002 | Material weakness | $530,000 | Capital outlay misstated across various funds |
| 2022-005 | Noncompliance | $1,200,000 | Federal awards misclassified (84.425E vs 84.425F) |

The stated cause of all three is the same sentence, in the auditor's words:

> The District lost two key employees in the finance department during the Spring
> of 2022. The loss of these employees resulted in a lack of staffing needed for
> appropriate review, a lack of knowledge in some areas due to limited
> documentation of procedures, as well as a lack of time necessary to perform
> procedures appropriately. **Replacement staff were not as knowledgeable as
> expected resulting in errors not being identified.**

### FY2024 — `dsb_audit_2024.pdf`

| Finding | Type | Amount | Subject |
| :--- | :--- | ---: | :--- |
| 2024-001 | Material weakness | — | Lack of appropriate staffing leading to audit entries |
| 2024-002 | Significant deficiency | **$773,629** | Wage rate compliance — Davis-Bacon clauses and certified payrolls |
| 2024-003 | Noncompliance | $1,162,601 | Expenditures exceeded budget without the board amendment state law requires |

## 2024-002 is the one that bears on labour

This is the finding closest to the question "is the money going to human beings
appropriately". The auditor's condition, verbatim:

> There were no controls over the wage rate compliance requirements which
> resulted in the District being unaware that **two of the contractors did not
> have the required Davis-Bacon wage rate clause in their contracts and were not
> submitting the required certified payrolls.**

Known questioned costs: **$773,629.** Criteria: 2 CFR §200.303 and 2 CFR Part 176
Subpart C, which require wage-rate provisions in federally funded construction
contracts over $2,000 and weekly certified payrolls.

The auditor's cause: projects originally funded from non-federal sources had
their funding changed mid-process, and the district had no review to check the
agreements against federal grant requirements when that happened.

**What this establishes:** $773,629 was paid under two contracts that lacked the
wage-rate clause the law requires, with no certified payrolls, so there is no
documentary evidence those workers were paid the required wage.

**What it does not establish:** that any worker was underpaid. The auditor
reports the absence of proof of compliance, not proof of violation. And these
were *construction* contractors — not custodial staff, and not the cleaning
contract in RFP 19-10.

## The recurring finding — the structural one

`2022-001` and `2024-001` are the **same deficiency, in two consecutive audit
cycles**, still open. Both are material weaknesses. The FY2024 schedule marks it
as previously reported.

A deficiency reported once is an incident. The same deficiency reported twice,
still open, is a condition. That judgement is the auditor's — the schedule's own
"previously reported" marking — not this instrument's.

The FY2024 recommendation names the departments directly:

> The District should work to appropriately staff the departments within the
> District which impact the financial statements including but not limited to
> **finance, facilities**, management information systems, **payroll**, and human
> resources.

`facilities` and `payroll` are named by the auditor as understaffed departments.

## How this bears on the labour question — and where it stops

IOW 2's thesis is that the operation depends on unpaid or under-compensated
labour. Three facts converge with it:

1. A **repeat material weakness** for lack of appropriate staffing, with
   `facilities` and `payroll` named in the corrective recommendation.
2. **$773,629** paid to contractors with no wage-rate clause and no certified
   payrolls.
3. **$1,162,601** spent over budget without the board amendment state law
   requires — money moving without the control that is supposed to authorise it.

That is convergence, not proof. **None of these findings concerns custodial
labour.** None establishes the cleaning specification is infeasible. The
instrument records the link as `CONVERGENT, NOT PROVEN` and prints it that way.

What would convert convergence into the claim:

- Per-site custodial hours actually paid — from the executed contract or payroll.
- Task times per square foot — from a district standard or a time study.
- A finding or admission that cleaning was performed outside paid hours.

None of the three is in any fetched document. The gap is unchanged.

## Verification

Every condition quoted above is checked against the extracted page it cites, by
`verifyQuotes` in `bds/src/findings.ts`. The comparison strips PDF extraction
artifacts — `Davis - Bacon` for `Davis-Bacon`, `requirement s` for
`requirements` — and preserves case, so the check is on characters present, not
on layout.

Two weaknesses in that check were found by testing it rather than trusting it:

- The first version verified only the first 110 characters of each condition, so
  a mutated dollar figure passed. It now verifies the whole quotation.
- The first normalisation glued real word boundaries together
  (`budgeted amounts in` → `budgeted amountsin`) and produced a false failure. It
  now removes whitespace entirely rather than guessing which spaces are real.

Both repairs are pinned. Mutating `$32,706` to `$32,707` in a transcription now
fails the check, as it should.

## Reproduce

```bash
cd bds && node dist/src/cli.js findings     # all six, with amounts and limits
```

Gate step 11 renders the findings and fails the build if the output contains a
verdict the auditor did not state.

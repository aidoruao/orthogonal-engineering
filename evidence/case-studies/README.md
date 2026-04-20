---
tags: [evidence, case-studies, readme]
register: audit
---

# Evidence — Case Studies

This directory is the landing page for Orthogonal Engineering case-study
evidence packages. Each case study is a self-contained folder whose name
encodes the domain and the date-of-record (for example
`commonwealth-sabbath-2025-11-19/`) and which MUST contain at minimum:

- a `README.md` frontmatter block with `register: audit`,
- a `claim.md` stating the invariant that was put under test,
- a `falsifiers.md` enumerating the conditions that would refute the claim,
- a `witness.jsonl` append-only record of the ProofObjects produced during
  the case study, and
- a `verdict.md` summarising whether the invariant survived its falsifier
  gauntlet.

New case studies SHOULD be added here rather than buried inside individual
domain folders so that readers can scan the full audit record from one
location.

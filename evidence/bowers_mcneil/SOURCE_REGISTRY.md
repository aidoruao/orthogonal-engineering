---
tags: [evidence, bowers-mcneil, source-registry]
register: audit
---

# SOURCE REGISTRY — Bowers vs McNeil
_Generated: PR #81 manufactured-correspondence addendum_
_Pipeline: IA-CYPHER-0002_

## Overview
This registry tracks the external public-source layer used by FC-007 through FC-013.
`EXTERNAL_REFERENCE` means the URL is public but the underlying artifact is not yet stored in the repo hash chain.

| ID | Source | URL | Verification Status | Key Data | Claim Mapping |
|----|--------|-----|---------------------|----------|---------------|
| SRC-001 | SAO legal memoranda PDF | https://sao4th.com/media/mrkcl4kd/william-mcneil-jr-sao4-legal-memoranda.pdf | EXTERNAL_REFERENCE | Public memo PDF; spec identifies Page 3 Footnote 7 and 'distraction strike' language | FC-010, FC-012, FC-013 |
| SRC-002 | News4JAX coverage index | https://www.news4jax.com/search/?query=William%20McNeil%20Jr | VERIFIED_BY_PUBLIC_SOURCE | Public reporting index for McNeil coverage | FC-007, FC-008, FC-011, FC-012 |
| SRC-003 | News4JAX bodycam/rain search | https://www.news4jax.com/search/?query=William%20McNeil%20Jr%20bodycam%20rain | VERIFIED_BY_PUBLIC_SOURCE | Public reporting anchor for bodycam/rain timeline | FC-007, FC-008 |
| SRC-004 | NWS Jacksonville weather portal | https://forecast.weather.gov/MapClick.php?lat=30.3322&lon=-81.6557 | VERIFIED_BY_PUBLIC_SOURCE | Public weather source family for Jacksonville | FC-008 |
| SRC-005 | News4JAX no-rain bodycam search | https://www.news4jax.com/search/?query=William%20McNeil%20Jr%20not%20raining | VERIFIED_BY_PUBLIC_SOURCE | Spec identifies this bodycam-analysis layer as saying no rain / wipers off / 'It's not raining' | FC-007, FC-008, FC-013 |
| SRC-006 | Weather Underground history portal | https://www.wunderground.com/history/daily/us/fl/jacksonville | VERIFIED_BY_PUBLIC_SOURCE | Public historical weather source family | FC-008 |
| SRC-007 | News4JAX attorney reporting search | https://www.news4jax.com/search/?query=William%20McNeil%20Jr%20attorney | VERIFIED_BY_PUBLIC_SOURCE | Public attorney quote anchor for non-interview and omission claims | FC-011, FC-012 |
| SRC-008 | News4JAX distraction-strike search | https://www.news4jax.com/search/?query=William%20McNeil%20Jr%20distraction%20strike | VERIFIED_BY_PUBLIC_SOURCE | Public reporting anchor for the memo's semantic-laundering phrase | FC-010 |
| SRC-009 | News4JAX memo search | https://www.news4jax.com/search/?query=William%20McNeil%20Jr%20memo | VERIFIED_BY_PUBLIC_SOURCE | Public reporting anchor for memo length/omissions | FC-012 |
| SRC-010 | News4JAX complaints search | https://www.news4jax.com/search/?query=William%20McNeil%20Jr%20Bowers%20complaints | PARTIALLY_VERIFIED | Public reporting confirms complaints, but not the full 7-to-0 citation ratio | FC-009 |

## Technical Note
SRC-001 remains `EXTERNAL_REFERENCE`. The PDF is public, but until it is downloaded and hashed into the repository, its status is not `VERIFIED_BY_REPO_SOURCE`.

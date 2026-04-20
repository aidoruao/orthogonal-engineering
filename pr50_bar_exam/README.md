---
tags: [pr50-bar-exam, readme]
register: documentation
---

# PR50 — Bar Exam: Ordination for Architectural Stewards

## Goals

The Bar Exam system provides a deterministic, witnessed, and auditable process for
ordaining AI architectural stewards. Candidates answer structured questions, receive
scored transcripts, and—on passing—receive a cryptographically signed certificate
with path-scoped capabilities.

## Artifacts

| Artifact | Description |
|---|---|
| `attempt_transcript.json` | Canonical signed exam response record |
| `score.json` | Deterministic scoring result |
| `proof.json` | Peano-based scoring proof |
| `certificate.json` | Signed ordination certificate |
| `witness/log/entries/*.json` | Append-only hash chain entries |

## Determinism Guarantees

- All scoring is a **pure function** of responses and the question bank
- The promptset is hashed (`promptset_hash`) and included in the transcript
- The environment is hashed (`environment_hash`) for full reproducibility
- Peano representations provide unambiguous integer proofs of scores
- SHA-256 is used throughout for content addressing

## Witness Chain

The witness chain is an append-only SHA-256 hash chain stored in
`pr50_bar_exam/witness/log/`. Every certificate issuance and revocation event
is recorded with a chained entry. The chain is verified from genesis at any time
using `python -m pr50_bar_exam.witness.verify`.

## Identity Attestation

In GitHub Actions CI, OIDC claims are extracted from environment variables
(`GITHUB_ACTOR`, `GITHUB_REPOSITORY`, etc.) and canonicalized to a `claims_hash`.
Outside CI, attestation gracefully returns `None`.

## Certificate Issuance

Certificates are issued only on pass (≥70% overall, ≥60% boundary, ≥60% threat,
≥50% grace). Each certificate is HMAC-SHA256 signed and references a witness chain
entry. Capabilities granted on pass:

- `read`, `comment`, `suggest`, `write`, `merge`

Consent-gated capabilities (`write_with_consent`, `execute_with_consent`) require
an explicit consent artifact.

## Revocation

Revocation is authority-controlled (default: `@aidoruao`). Triggers include:
`POLICY_VIOLATION`, `SECURITY_BREACH`, `MISREPRESENTATION`, `INACTIVITY`, `VOLUNTARY`.

On revocation:
- **Removed**: `write`, `merge`, `execute_with_consent`, `write_with_consent`
- **Kept**: `read`, `comment`, `suggest`
- **Past merges stand** (no retroactive undo)

## Retake Policy

A 30-day cooldown applies after any attempt. Cooldown is bound to:
- GitHub actor (`candidate_id`)
- Optional public key (`pubkey`)
- Optional sponsor (`sponsor_id`)

## Capability Matrix

Defined in `privileges/capability_matrix.json`. Path-scoped: most-specific glob wins.

## How to Run

```bash
# Run exam (stub responses for testing)
python -m pr50_bar_exam.examination.run_exam --candidate-id alice --output transcript.json

# Score transcript
python -m pr50_bar_exam.scoring.score_attempt transcript.json

# Verify witness chain
python -c "from pr50_bar_exam.invariants.append_only_witness import assert_chain_integrity; print(assert_chain_integrity())"
```

## Version

50.0.0

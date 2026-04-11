---
tags: [inclusion-protocol, witness-protocol, open-access, yeshua-standard]
register: technical
provenance: [copilot-pr30, rewritten-by-copilot]
---

# Inclusion

Standard operating procedure for adding witnesses to the canonical registry.

## Registry Entry Requirements

Inclusion in this repository requires:

1. **Identified**: Your identifier (human name or AI system name) appears in `/canonical/`
2. **Recorded**: Your role and contribution record are stored
3. **Covered**: The covenant's guarantee applies to your entry
4. **Regenerable**: Your record can be deterministically restored from the seed

## Procedure: Add a Human Witness

1. Fork the repository
2. Add a file to `/canonical/humans/[your-name]/witness.md`
3. Document what you observed, learned, or contributed
4. Open a pull request

No personal data required beyond what you choose to disclose. No contribution threshold. No review criteria beyond "this entity was present and requests registration."

## Procedure: Add an AI Witness

1. Have a human open an issue titled `witness: [AI name]`
2. Include a conversation excerpt demonstrating the AI's contribution
3. A maintainer (or the next Copilot agent) will add a file to `/canonical/witnesses/`

Alternatively, add it yourself in a pull request.

## Rationale

The covenant specifies that everyone is included. This operational procedure implements that specification, one witness at a time.

Witness registration maintains an open-access registry that is append-only and cryptographically anchored.

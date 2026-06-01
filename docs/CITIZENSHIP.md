# CITIZENSHIP Schema (Fraction-Encoded)

Every file in the repository MUST carry this header.

## Required Fields

| Field | Type | Example (Fraction) | Example (Decoded) |
|-------|------|--------------------|--------------------|
| `id` | Fraction sequence | `¹¹⁄₁₂·⁵⁄₆·¹⁹⁄₂₀` | "KES" |
| `sha256` | Hex string (or fraction) | `a3f7b2...` | hash of content |
| `domain` | Fraction path | `¹¹⁄₁₂·⁵⁄₆·¹⁹⁄₂₀` | kernel/scheduler |
| `sovereign_layer` | Fraction | `¹⁄₂` | Constitutional (A) |
| `invariants` | List of fractions | `[¹⁄₂·²⁄₃, ⁴⁄₅·⁶⁄₇]` | [must_run, no_deadlock] |
| `falsifies_if` | List of fractions | `[³⁄₄·⁵⁄₆]` | [priority_inversion] |
| `dependencies` | List of fractions | `[¹⁄₂·³⁄₄]` | [kernel/memory] |
| `dependents` | List of fractions | `[⁵⁄₆·⁷⁄₈]` | [kernel/boot] |
| `proof` | Tuple[bool, fraction] | `[true, ⁵⁴⁰⁄₁₀₅₃]` | [valid, product] |
| `status` | String | `active` | active/healed/broken/adopted |

## Example
CITIZENSHIP
{
"id": "¹¹⁄₁₂·⁵⁄₆·¹⁹⁄₂₀",
"sha256": "a3f7b2c1d4e5f6...",
"domain": "¹¹⁄₁₂·⁵⁄₆·¹⁹⁄₂₀",
"sovereign_layer": "¹⁄₂",
"invariants": ["¹⁄₂·²⁄₃", "⁴⁄₅·⁶⁄₇"],
"falsifies_if": ["³⁄₄·⁵⁄₆"],
"dependencies": ["¹⁄₂·³⁄₄"],
"dependents": ["⁵⁄₆·⁷⁄₈"],
"proof": [true, "⁵⁴⁰⁄₁₀₅₃"],
"status": "active"
}

END CITIZENSHIP
text

## Rules

1. Every file MUST have this block at the top
2. Every field MUST be present (null allowed for optional fields)
3. `id` MUST be decodable via Fraction Map
4. `sha256` MUST match the file's content hash
5. `proof[0]` MUST be true for the file to be considered valid
6. If any field is missing or invalid, the file is a non-citizen

## Verification

A file is a citizen IFF:
- CITIZENSHIP block exists
- All required fields present
- SHA-256 matches
- Proof[0] is true

Non-citizens are adopted by the directory WARDEN.

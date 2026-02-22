/*
 * yeshua_math/pure_reference_runtime/arithmetic_core.c
 *
 * Pure Reference Runtime — Arithmetic Core
 * PR #37 — Yeshua Mathematics Layer (YML)
 * Standard: Yeshua
 * Version: 1.0.0
 *
 * Hardware-agnostic, deterministic integer arithmetic.
 * No floats.  No hardware-specific instructions.
 * Fully inspectable.  Identical output across x86, ARM, and minimal nodes.
 *
 * Peano Arithmetic Invariants:
 *   P1: 0 is a natural number.
 *   P2: n' (successor of n) is a natural number.
 *   P3: n' != 0 for all n (zero has no predecessor).
 *   P4: m' == n' implies m == n (successor is injective).
 *   P5: Induction schema.
 */

#include <stdint.h>
#include <string.h>

/* ---------------------------------------------------------------------------
 * Peano Natural Number Representation
 * We use uint64_t as a machine-width Peano natural.
 * All operations are bounded and checked against overflow.
 * --------------------------------------------------------------------------- */

typedef uint64_t peano_nat;

#define PEANO_ZERO ((peano_nat)0)
#define PEANO_MAX  UINT64_MAX

/* P2: Successor — n' = n + 1 (with overflow guard) */
static peano_nat peano_successor(peano_nat n) {
    if (n == PEANO_MAX) return PEANO_MAX; /* saturating: bounded arithmetic */
    return n + 1;
}

/* P1/P3: Predecessor — defined only for n > 0 */
static peano_nat peano_predecessor(peano_nat n) {
    if (n == PEANO_ZERO) return PEANO_ZERO; /* floor at zero */
    return n - 1;
}

/* Peano addition: add(m, 0) = m; add(m, n') = add(m, n)' */
peano_nat peano_add(peano_nat m, peano_nat n) {
    peano_nat result = m;
    peano_nat count  = n;
    while (count != PEANO_ZERO) {
        result = peano_successor(result);
        count  = peano_predecessor(count);
    }
    return result;
}

/* Peano multiplication: mul(m, 0) = 0; mul(m, n') = mul(m, n) + m */
peano_nat peano_mul(peano_nat m, peano_nat n) {
    peano_nat result = PEANO_ZERO;
    peano_nat count  = n;
    while (count != PEANO_ZERO) {
        result = peano_add(result, m);
        count  = peano_predecessor(count);
    }
    return result;
}

/* P4: Successor injectivity check */
int peano_successor_injective(peano_nat m, peano_nat n) {
    return (peano_successor(m) == peano_successor(n)) ? (m == n) : 1;
}

/* ---------------------------------------------------------------------------
 * Canonical Hash (FNV-1a, 64-bit, portable)
 * Produces identical results across all platforms.
 * --------------------------------------------------------------------------- */

#define FNV_OFFSET_BASIS UINT64_C(14695981039346656037)
#define FNV_PRIME        UINT64_C(1099511628211)

uint64_t canonical_hash(const uint8_t *data, size_t len) {
    uint64_t hash = FNV_OFFSET_BASIS;
    for (size_t i = 0; i < len; i++) {
        hash ^= (uint64_t)data[i];
        hash *= FNV_PRIME;
    }
    return hash;
}

/* Hash a Peano natural */
uint64_t hash_peano_nat(peano_nat n) {
    uint8_t buf[8];
    /* Little-endian serialisation for canonical byte order */
    for (int i = 0; i < 8; i++) {
        buf[i] = (uint8_t)(n & 0xFF);
        n >>= 8;
    }
    return canonical_hash(buf, 8);
}

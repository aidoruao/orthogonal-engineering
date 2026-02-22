/*
 * yeshua_math/pure_reference_runtime/logic_engine.c
 *
 * Pure Reference Runtime — Boolean Logic Engine
 * PR #37 — Yeshua Mathematics Layer (YML)
 * Standard: Yeshua
 * Version: 1.0.0
 *
 * Hardware-agnostic, deterministic Boolean logic.
 * All operations reduce to classical propositional logic.
 * No hidden mutable state.  No non-deterministic branching.
 * Identical output across x86, ARM, and minimal nodes.
 */

#include <stdint.h>

/* ---------------------------------------------------------------------------
 * Boolean Type
 * We use uint8_t to avoid reliance on stdbool.h across all platforms.
 * TRUE = 1, FALSE = 0.  All functions saturate to {0, 1}.
 * --------------------------------------------------------------------------- */

typedef uint8_t bool_t;
#define BOOL_TRUE  ((bool_t)1)
#define BOOL_FALSE ((bool_t)0)

static bool_t to_bool(uint64_t v) { return v ? BOOL_TRUE : BOOL_FALSE; }

/* ---------------------------------------------------------------------------
 * Propositional Connectives
 * --------------------------------------------------------------------------- */

bool_t bool_not(bool_t a) {
    return to_bool(!a);
}

bool_t bool_and(bool_t a, bool_t b) {
    return to_bool(a & b);
}

bool_t bool_or(bool_t a, bool_t b) {
    return to_bool(a | b);
}

bool_t bool_xor(bool_t a, bool_t b) {
    return to_bool(a ^ b);
}

/* Material implication: A → B ≡ ¬A ∨ B */
bool_t bool_implies(bool_t a, bool_t b) {
    return bool_or(bool_not(a), b);
}

/* Biconditional: A ↔ B ≡ (A → B) ∧ (B → A) */
bool_t bool_iff(bool_t a, bool_t b) {
    return bool_and(bool_implies(a, b), bool_implies(b, a));
}

/* ---------------------------------------------------------------------------
 * Truth Table Exhaustive Validation (1-variable and 2-variable)
 *
 * Validates that a given function is deterministic over its full domain
 * by calling it twice for every input and comparing outputs.
 * --------------------------------------------------------------------------- */

typedef bool_t (*unary_fn)(bool_t);
typedef bool_t (*binary_fn)(bool_t, bool_t);

/* Returns 1 if the unary function is deterministic across its full domain. */
int validate_unary_deterministic(unary_fn fn) {
    bool_t inputs[2] = {BOOL_FALSE, BOOL_TRUE};
    for (int i = 0; i < 2; i++) {
        bool_t r1 = fn(inputs[i]);
        bool_t r2 = fn(inputs[i]);
        if (r1 != r2) return 0;
    }
    return 1;
}

/* Returns 1 if the binary function is deterministic across its full domain. */
int validate_binary_deterministic(binary_fn fn) {
    bool_t inputs[2] = {BOOL_FALSE, BOOL_TRUE};
    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2; j++) {
            bool_t r1 = fn(inputs[i], inputs[j]);
            bool_t r2 = fn(inputs[i], inputs[j]);
            if (r1 != r2) return 0;
        }
    }
    return 1;
}

/* ---------------------------------------------------------------------------
 * De Morgan Laws (used by cross_validator.py for compliance check)
 * --------------------------------------------------------------------------- */

/* ¬(A ∧ B) ≡ ¬A ∨ ¬B */
int demorgan_and(bool_t a, bool_t b) {
    return bool_not(bool_and(a, b)) == bool_or(bool_not(a), bool_not(b));
}

/* ¬(A ∨ B) ≡ ¬A ∧ ¬B */
int demorgan_or(bool_t a, bool_t b) {
    return bool_not(bool_or(a, b)) == bool_and(bool_not(a), bool_not(b));
}

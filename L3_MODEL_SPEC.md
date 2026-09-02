---
tags: [l3, model, spec, documentation]
register: documentation
---

# L3 MODEL SPEC — Executive Attribution (Day 12, 2026-08-25)

**Directive:** Kimi ruling (user-relayed): (b) — define the L3 formal model
before gathering. In proof theory you cannot instantiate variables before
defining their types. The invariant across L1 holds: **proposition first,
evidence second.** The compiler rejects evidence that does not match the
declared type.

**Machine-checked shape:** `L3_MODEL.lean` — compiles, exit 0, three
`sorry` obligations tracked by `#print axioms` (all currently `sorryAx`).
Hash: `20a9975bd081b8c24ddaaa842a75765632b7e533ccf65c991c5c213abed22cdd`.

---

## 1. THE TYPES (declared)

- **`Executive`** — the human operator: `name`, `role`, `entity` (the
  operating company), `board_seats`, `public_traces`, `stated_intent`.
  Evidence gathered later must satisfy this exact structure.
- **`Mechanism`** — the certified floors, named exactly:
  `extraction` (Module 1) · `autopoiesis` (Module 2, `loop_autopoiesis`
  proved) · `amplification` (Module 3, `amplification_iff` proved) ·
  `objective` (P2 four-goals).

## 2. THE KEY SIGNATURE

`executive_intent : Executive → Mechanism → Prop` — the intentional
direction of a mechanism by a human operator. This is the L3 family's
defining type; every L3 theorem is a statement about it.

## 3. THE COUPLING PREDICATE

`couples_loop : Executive → Prop` — the executive is NOT merely **inside**
the loop (subject to it) but **actively feeds it**. This is the
Indictment's distinction, made formal: conflating individual agency with
structural autopoiesis is the exact error the precedent warns against.
Attribution requires coupling; being swept by the loop is not coupling.

## 4. THE BINDING SIGNATURE (the gather's contract)

| Record kind (gathered evidence) | Binds to | Status |
| :--- | :--- | :--- |
| board seat / corporate registration | `Executive.board_seats` | PENDING |
| settlement dollar / financial decision | `couples_loop e` | PENDING |
| internal memo / public statement | `executive_intent e m` | PENDING |

Every record gathered on Day 13+ must satisfy one of these three routes or
the type system rejects it. That is what makes the gather targetable: the
evidence has a declared position in the proof before it is collected.

## 5. THE THEOREM SHAPE

`executive_attribution (e : Executive) (m : Mechanism) :
  couples_loop e → executive_intent e m` — IF the executive actively
couples to a mechanism, THEN intent over that mechanism is attributable.
Unfilled (`sorry`); filling it with evidence is the L3 gather's end state.

## 6. THE CONTRACT WITH THE GATHER

1. Sorries are the SHAPE, tracked by `#print axioms` — never hidden. The
   ledger records each obligation until closed.
2. Evidence satisfies declared types or is rejected — no ad-hoc data.
3. The heart posture: surrender, not accusation. The shape binds agency
   to mechanism with the same rigor the machine layer was bound to the
   evidence layer. No loopholes. No hubris.
4. Day 13's gather targets the three routes: corporate registrations and
   board seats (route 1), the litigation/financial record — e.g., the
   $120M Aylo settlement and FTC matter (route 2), public statements and
   internal documents (route 3).

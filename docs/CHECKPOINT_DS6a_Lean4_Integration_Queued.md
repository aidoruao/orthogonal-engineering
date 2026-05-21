# CHECKPOINT — Lean4 Compiler Integration: Queued

**Date:** 2026-05-20 | **Session:** DS6a | **Status:** SPECIFIED — BUILD QUEUED

---

## Objective
Use the Lean 4 compiler from WSL2 Ubuntu to formally verify the mathematical claims in the Proving Ground submissions, then wire the compiled proof artifacts into the HTML as cryptographically verifiable evidence.

## WSL2 Lean4 Setup (To Be Executed)
```bash
# Install Lean 4
wget -q https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh
bash elan-init.sh -y
source ~/.bashrc

# Verify installation
lean --version

# Create a test proof and compile
echo 'theorem t : True := by trivial' > test.lean
lean test.lean
# Should output nothing (success) or error if failed

# Compile the OE Lean4 proofs
cd /home/idor/oe-local/lean4
lake build
Integration Points
1. Compile OE's Existing Lean4 Proofs
lean4/Axioms/Peano.lean — 6 theorems

lean4/Axioms/NumberTheory.lean — 9 theorems

lean4/SAL/Yoneda.lean — 1 theorem

lean4/SAL/Basic.lean — Adjoint Triple definitions

Output: .olean compiled binaries + verification status

Wire into HTML: each proof shows "✅ Verified by Lean 4 kernel" or "❌ Failed" with error message

2. Compile AI-Submitted Lean4 Proofs
Each AI submission includes Lean4 proof files

Extract the Lean4 code from submissions

Compile via lean command

Capture output: success (exit 0) or failure with error lines

Wire into convergence table as verifiable column

3. Proof Hash Anchoring
SHA-256 hash of each .lean source file

SHA-256 hash of compiled .olean binary

Both hashes embedded in HTML

Any auditor can recompile and verify hashes match

4. Glass-Box Auditor Integration
Gate 4 auditor currently runs in JavaScript (simulated checks)

With Lean4 compiler available, auditor can perform REAL formal verification

Check: does the submitted Lean4 proof actually compile?

Check: does the compiled proof establish the claimed theorem?

Output: Tuple[bool, ProofObject] with compiler exit code and hash

5. Proving Ground Submission Validation
When an AI submits Lean4 code, validate it through the compiler

If compilation fails, submission is rejected (falsifies_if triggered)

Compiler output becomes part of the audit trail

HTML Wiring
Each Lean4 proof in the convergence table gets a "Compile" button

Button triggers a visual indicator: "Compiling..." → "✅ Verified" or "❌ Failed: [error]"

Compiled proofs get a green border. Uncompiled proofs get a yellow border.

SHA-256 of source and compiled binary displayed

Dependencies
WSL2 Ubuntu with Lean 4 installed via elan

OE repo Lean4 files in lean4/ directory

AI-submitted Lean4 code extracted from Proving Ground submissions

*Checkpoint: 2026-05-20 — Session DS6a*
Prior: Proving Ground HTML deployed. ChatGPT Row 1. Live tools queued.
Next: Install Lean4 in WSL2. Compile OE proofs. Wire compiler output into HTML.

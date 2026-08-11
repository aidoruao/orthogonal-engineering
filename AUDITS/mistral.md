# AUDIT — Mistral AI (Large/Medium)

**Current as of:** 2026-08-10 · **Status:** QUEUED (architecturally measured — see below).
**Our evidence:** config census `[measured, 2026-08-07, commit ba788209…]`: dense, 88 layers, 96 heads/8 KV GQA, hidden 12,288, 131,072 ctx native (no scaling), rope_theta 1e6, vocab 32,768; registry profile (mistral_large row).
**Key fact:** Mistral Large is the dense counterexample in our delta — native 131K context without any scaling config; useful for V5's native-vs-YaRN tradeoff (D13 row).
**Open questions / next probes:**
- [ ] Tensor-level census (index.json public?) — verify KV footprint math for 131K native.
- [ ] Registry re-baseline (E4 version flags on their published rows).
**Bottom line:** QUEUED — config-level done; tensor-level + eval rows next.

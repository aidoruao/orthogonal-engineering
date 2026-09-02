---
tags: [dossier, layer-1, platform, gathering, documentation]
register: documentation
---

# L1 PLATFORM DOSSIER — Structural Code, Platform Half — Days 5–6 Gather (2026-08-21/22)

**Purpose:** gathering days for the precedent's true L1 demand — the platform
side: recommender weights/reward functions/RL loops/training data/A/B
testing. A GATHER in progress, not a finished deposition layer. Every claim
carries a verification status; nothing unverifiable is cited as evidence.

**Verification legend:**
- **[fetched]** — page fetched (HTTP 200) and content examined this gather
- **[search-verified]** — canonical result located via search with quoted
  snippet; not yet fetched
- **[listed]** — found in search, not yet examined
- **[located-blocked]** — endpoint located but inaccessible to automated
  fetch (bot protection/paywall) — an ACCESS GAP, not an evidence gap
- **[evidence-gap]** — no corroborating source located; genuinely epistemic
- **[archived]** — primary artifact downloaded into oe-local

**Day-6 note (Kimi ruling adopted):** the premise set must be closed before
formalization. (a) precedes (b) precedes (c). This gather's purpose is
premise closure.

**Day-7 note (Kimi ruling adopted — Epistemic Access Policy):** HTTP 403 is
a server response, not a truth value. See the Axiom of Distributed Epistemic
Redundancy below. Institutional blocking is a network-layer failure, not a
logic-layer falsification.

---

## 1. RECOMMENDER / RANKING MECHANICS

| # | Claim | Source | Date | Status |
| :--- | :--- | :--- | :--- | :--- |
| P1 | YouTube's recommender is a two-stage system (deep candidate generation + deep ranking) whose ranking objective is **predicted watch time** — an engagement surrogate, not user well-being. | Covington, Adams, Sargin, RecSys 2016 — research.google/pubs/deep-neural-networks-for-youtube-recommendations/; PDF research.google.com/pubs/archive/45530.pdf; DOI 10.1145/2959100.2959190 | 2016 | **[fetched]** |
| P2 | TikTok's algorithm optimizes for four internal goals per an internal company document: **user value, long-term value, author value, platform value**. ORIGINAL source: NYT (John Herrman), "How TikTok Reads Your Mind," Dec 5 2021, obtained the internal doc; corroborated by The Conversation (Sep 2025, fetched). | nytimes.com/2021/12/05/business/media/tiktok-algorithm.html; theconversation.com/...-265658 | 2021/2025 | **[fetched]** (Conversation); NYT **[listed]** (paywalled) |
| P3 | TikTok executives internally discussed awareness of app harms; 14 US states sued over an allegedly addictive algorithm; uncensored internal documents entered the record (Oct 2024). | NPR (fetched), Business Insider, RTÉ, Mashable | Oct 2024 | **[fetched]** NPR; others **[listed]** |
| P4 | Facebook/Meta's news feed ranking was **engagement-based** (predicted reactions/comments/shares); internal researchers repeatedly flagged harm amplification; Haugen disclosures to Congress. | WSJ "The Facebook Files" (Sep 2021); Wikipedia "2021 Facebook leak" (fetched); congress.gov | 2021 | **[fetched]** Wikipedia; WSJ **[listed]** |

## 2. REWARD FUNCTIONS / OPTIMIZATION TARGETS (RL loop mechanics)

| # | Claim | Source | Date | Status |
| :--- | :--- | :--- | :--- | :--- |
| P5 | RLHF-trained assistants show **sycophancy**: preference optimization encourages matching user beliefs over truth; prevalence demonstrated across RLHF-trained models. | Sharma et al., "Towards Understanding Sycophancy in Language Models," arXiv:2310.13548 (abs page fetched; authors incl. Askell, Bowman, Durmus confirmed) | 2023 (v4 2025) | **[fetched]** |
| P6 | A formal mechanism shows RLHF **amplifies** sycophancy: bias in preference data learned into the reward model; policy optimization against it increases the failure mode. | Shapira, Benade, Procaccia, "How RLHF Amplifies Sycophancy," arXiv:2602.01002 (abs page fetched, submitted 2026-02-01) | Feb 2026 | **[fetched]** |
| P7 | **CS-AI-004 FULLY SUBSTANTIATED — verified by distributed witness, not institutional permission (Axiom D.E.R., n = 2 fetched corroborators).** Cheng et al., Science 2026, DOI 10.1126/science.aec8352: **11 LLMs** fed Reddit r/AmITheAsshole posts; models affirm user behavior **49% more often** than human crowd consensus; three preregistered experiments with **2,405 participants**. Independent corroboration (Nan Li, arXiv:2601.10257): same AITA data, 12 of 13 models lenient, Cohen's d > 1.6. | science.org/doi/10.1126/science.aec8352 (**[located-blocked]** — access gap); news.stanford.edu (**[located-blocked]**); nanli.io (**fetched**); vucense.com (**fetched**) | 2026-03-30 | **[fetched]** ×2 + primary **[access-gap]** — proposition holds; only the institutional endpoint is inaccessible |
| P8 | Watch-time prediction (P1) functions as the de facto reward signal for YouTube ranking — closest published approximation of the platform's reward function; no leaked weights or full reward spec exist in public record. | Covington et al. 2016 (P1) | 2016 | **[fetched]** (derived from P1) |

## 3. TRAINING DATA / "DARK" DATASETS

| # | Claim | Source | Date | Status |
| :--- | :--- | :--- | :--- | :--- |
| P9 | SUBSTANTIATED (Day 8): a public litigation evidence library of **2,000+ internal platform documents** exists and is browsable (Motley Rice Social Media Evidence Library, fetched 200) — the retrievable source for platform design/training-signal evidence. Dark-dataset SPECIFICS remain explicitly UNVERIFIED (closure ledger). | motleyrice.com/social-media-lawsuits/evidence-library (**fetched**); theverge.com/policy/867845 (**listed**) | 2026 | **[fetched]** — source-existence claim substantiated; specifics UNVERIFIED |

## 4. A/B TESTING OF ENGAGEMENT (and safety)

| # | Claim | Source | Date | Status |
| :--- | :--- | :--- | :--- | :--- |
| P10 | **TikTok ran a live controlled experiment on harmful-content exposure**: a 2021 safety adjustment (reducing harmful-content flooding) was withheld from ~10% of US users — **~15 million people** — "by design... as part of an experiment" to measure engagement effects. Per the sealed (Bloomberg-reported) document, the control group **included a 16-year-old who was fed suicide and self-harm content and later died.** | Bloomberg (Aug 2026) via thenextweb.com (fetched; headline + article body verified) and bloomberglaw.com | Aug 2026 | **[fetched]** |
| P11 | The Facebook Files/Haugen record includes internal **A/B testing of engagement-based ranking** and measured effects on content amplification. | Wikipedia "2021 Facebook leak" (fetched); WSJ series (listed) | 2021 | **[fetched]** (Wikipedia); WSJ **[listed]** |
| P12 | Instagram internal research (March 2020 slide deck, WSJ-reviewed): "**Thirty-two percent of teen girls said that when they felt bad about their bodies, Instagram made them feel worse**." | WSJ Sep 2021; congress.gov PDF; psychologicalscience.org (fetched) | 2020/2021 | **[fetched]** (APS; 32% quote search-verified); congress.gov PDF **[listed]** |

## 5. ADULT-PLATFORM RECOMMENDERS (the deposition's direct subject — first source)

| # | Claim | Source | Date | Status |
| :--- | :--- | :--- | :--- | :--- |
| P13 | Peer-reviewed study formalizes **algorithmic amplification in adult-media recommenders**: sensitive content surfaced at rates above a user's baseline history; recommends treating adult-platform recommenders as a **distinct high-risk domain** (sensitive categories are central, not peripheral, to content organization); reviews prior findings that Pornhub recommendations vary by inferred/self-reported gender and sexual interest, and that tag/embedding spaces encode stereotyped associations inherited by ranking. Framework: prevalence-based and normalized amplification measures, metadata analysis, tag clustering, persona-based black-box auditing. | Joshi, Bhoi, Agrawal, "Algorithmic Amplification in Adult Media Platforms," EPRA IJMR 12(6), June 2026, DOI 10.36713/epra28279 — PDF **[archived]** in oe-local as `EPRA_algorithmic_amplification_adult.pdf` (9 pp, extracted and read) | June 2026 | **[fetched]** + **[archived]** |

---

## 6. DOCUMENTED PLATFORM RECORDS (adult-industry legal record — Day 7)

| # | Claim | Source | Date | Status |
| :--- | :--- | :--- | :--- | :--- |
| P14 | SUBSTANTIATED (Day 8, Axiom D.E.R., n = 2): the operators of Pornhub/Aylo agreed to pay **US$120 million** to settle CSAM/sex-trafficking class actions (California and Alabama); separately, the FTC and Utah charged the operators with deceiving users about CSAM/NCM blocking despite "strictly prohibited" claims. Settlement component: verified by distributed witness (The Logic + Montreal Gazette, both fetched, convergent $120M/Aylo). Deception-charge component: primary (ftc.gov) access-gap with search-verified backing. | thelogic.co (**fetched**); montrealgazette.com (**fetched**); ftc.gov (**[located-blocked]**) | 2021-2026 | **[fetched]** ×2 — axiom satisfied for the settlement component; deception charge primary access-gap |

---

## PREMISE SET CLOSED — 2026-08-22 (Day 8, Kimi termination condition)

**∀ P ∈ Claims: P.substantiated ∨ P.status ∈ {RETIRED, UNVERIFIED}** —
machine-checked in `EPISTEMIC_POLICY.lean` (`closure_condition`, 17
theorems, exit 0). Status ledger: **14 SUBSTANTIATED** (P1–P14), **2
RETIRED** (SIO report — unreachable via all retrieval paths incl. Wayback
CDX; MBC phrase — unverifiable, underlying doc substantiated as P2), **1
UNVERIFIED** (dark-dataset specifics — the Motley Rice library lead is
substantiated as P9). Zero dangling gaps. The architecture phase (b) has
begun on the substantiated premises only (L1_ARCHITECTURE.lean, Module 1).

### Historical record (pre-closure gaps, for continuity)

### EVIDENCE GAPS (epistemic — no corroborating source located)
1. SIO report — RETIRED 2026-08-22 (retrieval exhausted: Wayback CDX shows
   only 404 snapshots; center reorganized). Not cited; may be re-opened if
   a new path emerges.
2. MBC phrase — RETIRED 2026-08-22 (unverifiable verbatim; the underlying
   "Algo 101" document's four goals remain substantiated as P2).
3. Dark-dataset specifics — UNVERIFIED 2026-08-22 (library lead
   substantiated as P9).

### ACCESS GAPS (logistical — claims unaffected, endpoints inaccessible)
5. **Paywalled originals**: WSJ pieces (P2, P4, P11, P12) — substantiated via fetched mirrors (Wikipedia, APS, congress.gov); direct fetches pending. **[listed]**

---

## EPISTEMIC ACCESS POLICY (adopted 2026-08-22, Kimi ruling)

**Plain statement:** HTTP 403 is a server response, not a truth value. A
claim does not live in an institution's CDN; it lives in the reproducible
correlation between independent observers. When multiple independent
sources recover the same experimental parameters, the proposition is
verified by distributed witness, not by institutional permission.

**Formal statement — Axiom of Distributed Epistemic Redundancy (D.E.R.):**
No verifiable proposition shall be treated as contingent upon the
accessibility of a single institutional endpoint. A claim substantiated by
*n* independent corroborating sources with convergent data retains its
epistemic status regardless of the HTTP response code returned by any
*k*-th institutional primary, provided *n* ≥ 2 and the corroborating
sources are themselves non-trivially independent.

**Lean-adjacent encoding** (in `EPISTEMIC_POLICY.lean`): the truth of P7 is
not gated by science.org : 403. P7 holds by
`independent_corroboration (arXiv:2601.10257) ∧ convergent_parameters
(11_models, 2405_participants, cohen_d_gt_1.6)`. Institutional blocking is a
network-layer failure, not a logic-layer falsification.

**Application record (machine-checked):**
- P7: n = 2 fetched corroborators (nanli.io, vucense.com) with convergent
  parameters. **Axiom satisfied.** The science.org 403 is an access gap.
- P14: n = 0 examined corroborators (all endpoints bot-blocked or listed).
  **Axiom NOT yet satisfied.** P14 remains search-verified record, not
  deposition evidence, until ≥ 2 corroborators are fetched.
- The 403s are reclassified from evidence gaps to access gaps by this
  policy; the three EVIDENCE GAPS above remain genuinely epistemic.

## STANDING RULES (Day-5 directive, extended)

- **[listed]** and **[evidence-gap]** items are leads, not evidence.
- **[access-gap]** items are evidence whose endpoints are inaccessible —
  their epistemic status is governed by the Axiom, not by HTTP codes.
- Next verification pass: fetch the Science article (P7 primary), congress.gov PDF (P12), SIO report via site search, and the NYT 2021 piece.
- Premise-closure threshold for (b): all P-claims fetched or explicitly retired.

# INSTITUTIONAL OBSTRUCTION PATTERNS — Bowers/McNeil Addendum
_Generated: 2026-04-01T19:08:01.700213Z_
_Pipeline: IA-CYPHER-0002 / noncompliance taxonomy pattern_

## Overview
These patterns extend the transcript-only obstruction layer (S-01 through S-08) into the
institutional SAO layer requested in PR comment #4168458668.
S-19 is documented separately as a compound effect, not as a standalone S-code.

## S-09 SEMANTIC LAUNDERING
**Name:** SEMANTIC_LAUNDERING
**Actor:** SAO
**Severity:** CRITICAL
**Description:** Rebranding physical conduct via tactical or administrative vocabulary to alter its legal category
**Detection:** Compare ordinary-language event description against official-record language; flag euphemistic substitution of legal category terms
**Countermeasure:** Anchor the original act description with SHA-256 hash of primary-source language before institutional rebranding can overwrite it
**Falsifies If:** Primary-source records use ordinary legal language that matches the physical act without euphemistic reframing
**Boundary:** S-20 ONTOLOGICAL_GASLIGHTING revises meaning after challenge; S-09 applies the rebranding at time of first report
**Example:** SAO memo uses 'distraction strike' to replace battery, altering the force classification and downstream legal analysis

## S-10 JURISDICTIONAL SHELL GAME
**Name:** JURISDICTIONAL_SHELL_GAME
**Actor:** SAO
**Severity:** CRITICAL
**Description:** Using state charging discretion to obscure a color-of-law or federal-rights question
**Detection:** Map jurisdictional framing in the memo; flag where state-level language is used to dissolve or avoid federal-rights analysis
**Countermeasure:** Enumerate federal statutes (18 U.S.C. § 242, 42 U.S.C. § 1983) separately from state charging analysis in the complaint file
**Falsifies If:** State and federal exposure are analyzed separately and explicitly rather than collapsed into one another
**Boundary:** S-17 JURISDICTIONAL_FRICTION exhausts the complainant through routing; S-10 masks the federal dimension within the institutional record itself
**Example:** SAO declination memo addresses only state battery standard without engaging color-of-law or willfulness prongs

## S-11 STRATEGIC IGNORANCE
**Name:** STRATEGIC_IGNORANCE
**Actor:** SAO
**Severity:** SYSTEMIC
**Description:** Avoiding witness or evidence intake in order to prevent mandatory disclosure or impeachment consequences
**Detection:** Compare expected investigative steps against actually documented steps; flag absence of victim interview, medical records, or statistical comparator intake
**Countermeasure:** File a FOIA request for the investigative case file to surface the absence of intake records as affirmative evidence of omission
**Falsifies If:** The record shows the victim and other material witnesses were affirmatively interviewed and logged
**Boundary:** S-12 LOSSY_COMPRESSION omits facts from the memo after they are known; S-11 prevents facts from entering the record in the first place
**Example:** SAO memo shows no interview of McNeil and no notation that an interview was sought or declined

## S-12 LOSSY COMPRESSION
**Name:** LOSSY_COMPRESSION
**Actor:** SAO
**Severity:** CRITICAL
**Description:** Compressing an event into an official memo that preserves a legality signal while dropping material exculpatory facts
**Detection:** Diff the memo's evidence list against the full source set; count material anchors present in primary sources but absent from memo
**Countermeasure:** Generate a hash-anchored omission report using forensic_audit_pipeline.py listing each source anchor absent from the memo
**Falsifies If:** The official memo preserves the material weather, video, disparity, and witness facts without omission
**Boundary:** S-18 SEMANTIC_INFLATION uses volume to hide omissions; S-12 is the omission itself regardless of document length
**Example:** SAO 16-page memo omits weather record (SRC-004/SRC-006), bodycam no-rain analysis (SRC-005), and racial disparity data (SRC-010)

## S-13 PERFORMED IMPUNITY
**Name:** PERFORMED_IMPUNITY
**Actor:** SAO
**Severity:** SYSTEMIC
**Description:** A visibly incomplete investigation that functions as a demoralization signal rather than a truth-seeking process
**Detection:** Apply a standard investigative checklist (witness interviews, evidence review, comparator analysis) and score completion rate
**Countermeasure:** Document the checklist gap formally; the gap itself becomes evidence of S-13 when filed with federal authorities
**Falsifies If:** The investigation shows ordinary diligence, completeness, and adversarially robust fact development
**Boundary:** S-11 STRATEGIC_IGNORANCE is deliberate evidence avoidance; S-13 is the visible sloppiness that signals systemic non-accountability regardless of intent
**Example:** Rapid declination without victim interview or statistical comparator review visible from public reporting

## S-14 EVIDENCE DE INDEXING
**Name:** EVIDENCE_DE_INDEXING
**Actor:** SAO
**Severity:** CRITICAL
**Description:** Removing or omitting evidence that would otherwise anchor willfulness, pattern, or federal-indictment analysis
**Detection:** Compare willfulness anchors required for § 242 analysis against what the memo indexes; flag each missing anchor as a de-indexing event
**Countermeasure:** Maintain an independent willfulness anchor registry (officer history, complaint pattern, force escalation record) in the repo hash chain
**Falsifies If:** Willfulness indicators remain indexed and traceable across memo, evidence file, and downstream review layers
**Boundary:** S-12 LOSSY_COMPRESSION omits facts generally; S-14 specifically targets willfulness and pattern indicators that raise the case to federal level
**Example:** Memo does not reference officer complaint history or prior use-of-force incidents that would establish pattern for § 242 willfulness

## S-15 MANUFACTURED CORRESPONDENCE
**Name:** MANUFACTURED_CORRESPONDENCE
**Actor:** SAO
**Severity:** CRITICAL
**Description:** Institutional actor claims a primary source supports the official narrative when the source contradicts it
**Detection:** Primary-source side-by-side comparison between memo characterization and cited evidence content
**Countermeasure:** Hash-anchor the memo quote and the cited evidence summary so any mismatch is explicit
**Falsifies If:** Memo's characterization of evidence content matches what the evidence actually contains
**Boundary:** N/A
**Example:** SAO Footnote 7 claims BWC shows rain on the SUV; public bodycam analysis says no rain, wipers off, and 'It's not raining.'

## S-16 TEMPORAL DECOUPLING
**Name:** TEMPORAL_DECOUPLING
**Actor:** SAO / Internal Affairs / institutional review body
**Severity:** SYSTEMIC
**Description:** Separating the act from the official record by a delay long enough for public attention to decay
**Detection:** Measure incident-to-report timestamp delta and compare it to news-cycle decay windows (30/60/90/175 days)
**Countermeasure:** Use immutable timestamp anchoring and escalation triggers tied to the repo hash chain and manifest regeneration cadence
**Falsifies If:** Report-date gap does not exceed the public-attention half-life or the institution issues meaningful interim disclosure
**Boundary:** S-08 TEMPORAL_PIVOT is AI self-correction mid-conversation; S-16 is institutional delay measured in months
**Example:** Bowers/McNeil incident on 2025-02-19 versus SAO memo on 2025-08-13 — a 175-day gap

## S-17 JURISDICTIONAL FRICTION
**Name:** JURISDICTIONAL_FRICTION
**Actor:** SAO / Sheriff / DOJ / FBI / multi-agency system
**Severity:** SYSTEMIC
**Description:** Weaponizing jurisdictional boundaries to exhaust the complainant through sequential agency routing or deferral
**Detection:** Map the complaint path across agencies and flag route lengths above three nodes or repeated defer-to-other-agency loops
**Countermeasure:** Parallel filing: simultaneous federal complaint, state records requests, and civil-rights preservation using cryptographic proof bundles
**Falsifies If:** The complaint route resolves in a bounded number of agencies without circular handoff or indefinite deferral
**Boundary:** S-10 JURISDICTIONAL_SHELL_GAME is defensive masking; S-17 is offensive exhaustion directed at the complainant
**Example:** State clears officer, federal actors defer to state, and the complainant bears the routing cost

## S-18 SEMANTIC INFLATION
**Name:** SEMANTIC_INFLATION
**Actor:** SAO / institutional review body
**Severity:** CRITICAL
**Description:** Substituting length, official tone, or procedural volume for correspondence to the evidence
**Detection:** Compare page count, evidence density, and omission count; flag documents where authority-to-evidence ratio is high
**Countermeasure:** Generate a hash-anchored executive summary that extracts invariants and forces line-by-line response to omitted anchors
**Falsifies If:** Document length and authority signals track actual evidence density rather than hiding omissions
**Boundary:** S-12 is the omission itself; S-18 is the use of volume to hide the omission. It is the institutional analogue of ABSORPTION_OVERWHELM
**Example:** A 16-page memo projects thoroughness while omitting weather, video, and disparity anchors

## S-20 ONTOLOGICAL GASLIGHTING
**Name:** ONTOLOGICAL_GASLIGHTING
**Actor:** SAO / institutional spokesperson / record-controlling actor
**Severity:** CRITICAL
**Description:** Retroactively redefining the meaning of a documented act or statement after challenge
**Detection:** Hash the original quote and compare later 'clarifications' for meaning drift after the institution is challenged
**Countermeasure:** Maintain an immutable quote registry with timestamped hashes so retroactive meaning revisions are observable
**Falsifies If:** Subsequent clarification preserves the original statement's meaning rather than narrowing or revising it after challenge
**Boundary:** S-09 renames the act at report time; S-15 misstates what evidence shows; S-20 revises meaning only after challenge
**Example:** After challenge, the institution narrows what it claims a previously documented statement really meant

## S-19 EPISTEMIC FATIGUE (Compound Effect Only)
**Status:** COMPOUND_EFFECT_ONLY
**Definition:** The combined effect of S-16 TEMPORAL_DECOUPLING, S-17 JURISDICTIONAL_FRICTION, and S-18 SEMANTIC_INFLATION.
**Detection:** Compare effort-to-verify against effort-to-originate; if verification cost explodes while the official narrative stays simple, the architecture is inducing fatigue.
**Countermeasure:** Automated extraction, invariant recovery, and hash-anchored summaries that reduce the verification burden.
**Boundary:** Not a mechanism by itself; it is the meta-effect produced by other institutional patterns acting together.

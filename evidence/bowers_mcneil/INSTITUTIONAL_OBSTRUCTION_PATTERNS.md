# INSTITUTIONAL OBSTRUCTION PATTERNS — Bowers/McNeil Addendum
_Generated: 2026-04-01T12:41:12.495386Z_
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
**Detection:** N/A
**Countermeasure:** N/A
**Falsifies If:** Primary-source records use ordinary legal language that matches the physical act without euphemistic reframing
**Boundary:** N/A
**Example:** N/A

## S-10 JURISDICTIONAL SHELL GAME
**Name:** JURISDICTIONAL_SHELL_GAME
**Actor:** SAO
**Severity:** CRITICAL
**Description:** Using state charging discretion to obscure a color-of-law or federal-rights question
**Detection:** N/A
**Countermeasure:** N/A
**Falsifies If:** State and federal exposure are analyzed separately and explicitly rather than collapsed into one another
**Boundary:** N/A
**Example:** N/A

## S-11 STRATEGIC IGNORANCE
**Name:** STRATEGIC_IGNORANCE
**Actor:** SAO
**Severity:** SYSTEMIC
**Description:** Avoiding witness or evidence intake in order to prevent mandatory disclosure or impeachment consequences
**Detection:** N/A
**Countermeasure:** N/A
**Falsifies If:** The record shows the victim and other material witnesses were affirmatively interviewed and logged
**Boundary:** N/A
**Example:** N/A

## S-12 LOSSY COMPRESSION
**Name:** LOSSY_COMPRESSION
**Actor:** SAO
**Severity:** CRITICAL
**Description:** Compressing an event into an official memo that preserves a legality signal while dropping material exculpatory facts
**Detection:** N/A
**Countermeasure:** N/A
**Falsifies If:** The official memo preserves the material weather, video, disparity, and witness facts without omission
**Boundary:** N/A
**Example:** N/A

## S-13 PERFORMED IMPUNITY
**Name:** PERFORMED_IMPUNITY
**Actor:** SAO
**Severity:** SYSTEMIC
**Description:** A visibly incomplete investigation that functions as a demoralization signal rather than a truth-seeking process
**Detection:** N/A
**Countermeasure:** N/A
**Falsifies If:** The investigation shows ordinary diligence, completeness, and adversarially robust fact development
**Boundary:** N/A
**Example:** N/A

## S-14 EVIDENCE DE INDEXING
**Name:** EVIDENCE_DE_INDEXING
**Actor:** SAO
**Severity:** CRITICAL
**Description:** Removing or omitting evidence that would otherwise anchor willfulness, pattern, or federal-indictment analysis
**Detection:** N/A
**Countermeasure:** N/A
**Falsifies If:** Willfulness indicators remain indexed and traceable across memo, evidence file, and downstream review layers
**Boundary:** N/A
**Example:** N/A

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

# Domain Invariant Deepening Status

**Generated:** 2026-04-08  
**Context Usage:** ~157k/262k (60%)

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total domains | 141 | 100% |
| Deepened (50+ lines) | 60 | 42.6% |
| Stubs (<50 lines) | 81 | 57.4% |

## Deepened Domains (Real Regulatory Logic)

These domains have comprehensive invariants testing real legal/regulatory/scientific constraints:

### Layer 0-2 (Constitutional/Statutory) — Complete
- d_bill_of_rights (194 lines)
- d_citizenship (219 lines)
- d_constitutional_law — base layer
- d_criminal_law (250 lines)
- d_federalism (184 lines)
- d_habeas_corpus (232 lines)
- d_amendment_process (192 lines)
- d_judicial_review (206 lines)
- d_separation_of_powers (201 lines)
- d_un_charter (110 lines)

### Layer 3 (Regulatory) — Partially Complete
- d_banking_regulation (282 lines) — Basel III, Dodd-Frank
- d_consumer_protection (272 lines) — FTC, TILA
- d_disability_rights (327 lines) — ADA, IDEA
- d_drug_regulation (268 lines) — FDA
- d_employment_law (302 lines) — FLSA, Title VII
- d_environmental_law (276 lines) — EPA, NEPA
- d_family_law (260 lines)
- d_food_safety (279 lines) — FSMA, HACCP
- d_housing_law (201 lines) — Fair Housing
- d_immigration (284 lines) — INA
- d_intellectual_property (257 lines) — Patent/Copyright
- d_medical (232 lines) — FDA QSR, HIPAA
- d_privacy_law (220 lines) — GDPR, CCPA
- d_securities_law (241 lines) — SEC 1933/1934
- d_telecommunications_law (246 lines) — FCC
- d_transportation (220 lines) — FMCSA
- d_voting_rights (208 lines)
- d_weapons_regulation (276 lines) — NFA, Brady

### Layer 4 (Institutional) — Partially Complete
- d_building_codes (360 lines) — IBC, ADA
- d_corporate_compliance (355 lines)
- d_corporate_law (251 lines)
- d_curriculum (353 lines)
- d_education — stub
- d_school_districts (317 lines)
- d_school_funding (340 lines)
- d_urban_planning (352 lines)
- d_zoning (305 lines)

### Technical/Sectoral — Partially Complete
- d_aerospace (259 lines) — DO-178C
- d_ai_ontological_status (273 lines)
- d_antitrust (252 lines)
- d_aviation (160 lines)
- d_civil_law (234 lines)
- d_crypto (101 lines)
- d_dh_standalone (265 lines)
- d_election_law (255 lines)
- d_elder_law (215 lines)
- d_energy (209 lines) — FERC, pipelines
- d_financial (136 lines)
- d_iso_standards (200 lines) — ISO 9001/27001
- d_labor_rights (165 lines)
- d_police_procedure (360 lines)
- d_real_estate (360 lines)
- d_road_standards (327 lines)
- d_robotics (195 lines) — ISO 10218
- d_space (223 lines) — NASA-STD
- d_tax_law (181 lines)
- d_websec (317 lines) — OWASP

### International — Partially Complete
- d_diplomatic (136 lines)
- d_intl_criminal (146 lines)
- d_intl_humanitarian (154 lines)
- d_treaties (140 lines)
- d_trade_agreements (185 lines)

## Stub Domains (Need Deepening)

These 81 domains have generic stub invariants (9-48 lines each):

### Critical Priority (Legal Foundations)
- d_administrative_law (19 lines) — APA
- d_bankruptcy (9 lines) — Chapter 7/11/13
- d_contract_law (19 lines) — UCC, common law
- d_evidence_law (19 lines) — FRE
- d_healthcare_law (19 lines) — Stark, Anti-Kickback
- d_insurance (19 lines) — state regulation
- d_procedure_civil (19 lines) — FRCP
- d_procedure_criminal (19 lines) — FRCrimP
- d_property_law (19 lines) — real estate, IP

### High Priority (Public Safety/Sectoral)
- d_agriculture (28 lines) — USDA
- d_automotive (28 lines) — NHTSA
- d_chemical (28 lines) — EPA TSCA
- d_construction (28 lines) — OSHA
- d_emergency (48 lines)
- d_government (48 lines)
- d_industrial (48 lines)
- d_military (28 lines)
- d_occupational_safety (48 lines) — OSHA
- d_public_health (48 lines)
- d_utility_regulation (48 lines)

### Medium Priority (Economic/Social)
- d_education (48 lines)
- d_environmental_planning (28 lines)
- d_hospitality (28 lines)
- d_platform (48 lines)
- d_retail (28 lines)
- d_transit (28 lines)

### Lower Priority (Specialized/Niche)
- d_arc_agi_3 (28 lines)
- d_architecture_proof (28 lines)
- d_axioms (28 lines)
- d_biotech (28 lines)
- d_bluecollar (28 lines)
- d_boring (28 lines)
- d_capability_benchmark (28 lines)
- d_child_welfare (28 lines)
- d_combinatorics (28 lines)
- d_communications (28 lines)
- d_computability (28 lines)
- d_creative (28 lines)
- d_cross_model_benchmarks (28 lines)
- d_crusader (28 lines)
- d_digital_governance (28 lines)
- d_economic_mobility (28 lines)
- d_elder_care (28 lines)
- d_epistemic_logic (28 lines)
- d_ethics (28 lines)
- d_fractals (28 lines)
- d_fun (28 lines)
- d_game_theory (28 lines)
- d_gamemods (28 lines)
- d_gaming (28 lines)
- d_geographic_information (28 lines)
- d_graphics (28 lines)
- d_indigenous_rights (28 lines)
- d_legal (40 lines)
- d_licensing (28 lines)
- d_luxury (28 lines)
- d_maritime (28 lines)
- d_media_law (28 lines)
- d_minecraft_spatial (28 lines)
- d_mining (28 lines)
- d_necessity (28 lines)
- d_neighborhood_equity (28 lines)
- d_noncreative (28 lines)
- d_number_theory (28 lines)
- d_oilgas (28 lines)
- d_paraconsistent_logic (28 lines)
- d_pattern_recognition (28 lines)
- d_peano_ext (28 lines)
- d_pharma (28 lines)
- d_psychology (28 lines)
- d_rail (28 lines)
- d_religious_liberty (28 lines)
- d_restorative_justice (28 lines)
- d_school_equity (28 lines)
- d_sharding (28 lines)
- d_sociology (28 lines)
- d_water (28 lines)
- d_whitecollar (28 lines)

## Work Remaining

### Immediate Next Session (Batch D2)
Target: 10 critical stub domains
1. d_administrative_law — APA procedures
2. d_bankruptcy — Chapter 7/11/13
3. d_contract_law — UCC Article 2
4. d_evidence_law — Federal Rules
5. d_healthcare_law — Stark, Anti-Kickback
6. d_insurance — state regulatory
7. d_procedure_civil — FRCP
8. d_procedure_criminal — FRCrimP
9. d_property_law — real property
10. d_occupational_safety — OSHA standards

### Following Sessions
- **Batch D3:** Public safety (automotive, chemical, emergency, military)
- **Batch D4:** Economic sectors (agriculture, construction, hospitality, retail)
- **Batch D5-D10:** Specialized domains (math, AI, niche sectors)

## Completion Criteria

The SOVEREIGN TOPOS Phase 3 halt condition requires:
> Every domain invariant is falsifiable (not just structurally correct)

Current state: 60/141 domains (42.6%) meet this criterion.
Target: 141/141 domains (100%).

## Session Continuity

Each Kimi CLI session should:
1. Deepen 10 domain invariants
2. Update this status document
3. Commit with message: "Deepen 10 domain invariants (Batch DX)"
4. Push to main
5. Save session transcript to repo as `Kimi Code t[N] session cli.txt`

**Next Session:** Batch D2 — 10 critical legal foundation domains

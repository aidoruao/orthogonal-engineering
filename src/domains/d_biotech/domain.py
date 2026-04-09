"""D_BIOTECH domain definition — Biotechnology

Layer: 3
CardinalStrength: PREDICATIVE

Biotechnology applies biological systems and organisms for technological applications.
Genomic sequencing, CRISPR gene editing, lab automation, and biosafety are core domains.
Deterministic reproducibility is critical for clinical diagnostics and research.
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_BIOTECH"
DOMAIN_NAME = "Biotechnology"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    'sequencing',
    'variant-calling',
    'CRISPR',
    'gene-editing',
    'lab-automation',
    'biosafety',
    'PCR',
    'qPCR',
    'NGS',
    'proteomics',
    'metabolomics',
    'bioinformatics',
    'FASTQ',
    'VCF',
    'BAM',
    'alignment',
    'base-calling',
    'phred-scores',
    'quality-control',
    'contamination-detection',
    'biosafety-level',
    'pathogen-containment',
]

INVARIANTS = [
    'VCF (Variant Call Format) output is identical for identical FASTQ input with same pipeline version.',
    'Reagent dispensing accuracy within ±2% for liquid handling robotics.',
    'PCR amplification cycles deterministic given template concentration and primer design.',
    'qPCR quantification cycle (Cq) reproducible within ±0.5 cycles for technical replicates.',
    'NGS (Next-Generation Sequencing) base-calling Phred scores calibrated to error rates (Q30 = 0.1% error).',
    'Read alignment reproducible: same aligner version and reference genome yield identical BAM files.',
    'CRISPR on-target efficiency >80% for validated guide RNAs in standard cell lines.',
    'CRISPR off-target detection: <1% off-target edits for high-specificity guides.',
    'Lab automation: plate transfers maintain sample identity with <10^-6 swap rate.',
    'Biosafety Level 2: double-door autoclave, BSC (biosafety cabinet) with HEPA filtration.',
    'Biosafety Level 3: negative pressure, personnel protective equipment, respiratory protection.',
    'Contamination detection: <0.01% cross-contamination between samples in automated workflows.',
    'Proteomics: mass spec identification with <1% false discovery rate (FDR).',
    'Metabolomics: compound identification with m/z accuracy <5 ppm.',
    'Bioinformatics pipelines: hash-anchored reference genomes and annotation databases.',
]

FALSIFICATION_TESTS = ["F_BIOTECH_001"]
ONTOLOGICAL_ISSUES = ["OI_BIOTECH_001"]

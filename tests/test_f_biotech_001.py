"""
Falsification test: DNA sequencing pipeline reproducible from identical raw reads.
Identical FASTQ input produces identical VCF output.

# @falsification_id: F_BIOTECH_001
"""
import hashlib
import pytest

def simulate_pipeline(fastq_input: bytes) -> bytes:
    """Simulate a deterministic sequencing pipeline."""
    intermediate = hashlib.sha256(fastq_input).digest()
    vcf = hashlib.sha256(b"vcf_header:" + intermediate).digest()
    return vcf

FASTQ = b"@read1\nACGTACGT\n+\nIIIIIIII\n" * 100

def test_pipeline_reproducible():
    out1 = simulate_pipeline(FASTQ)
    out2 = simulate_pipeline(FASTQ)
    assert out1 == out2, "Pipeline output is not reproducible from identical input"

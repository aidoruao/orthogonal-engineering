"""tss_blockchain.py — SIMULATED Bitcoin timestamping and IPFS replication.

Part of "TSS v10", a production-grade AI-accountability infrastructure.

This module is fully OFFLINE and SIMULATED: no real Bitcoin network, no real
IPFS network, no network calls of any kind. All identifiers ("txids", CIDs)
are deterministic functions of their inputs (sha256 / base58), clearly marked
as simulated so nobody mistakes them for real on-chain or IPFS records.

Standard library only: hashlib, typing, sys.
"""

import hashlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Base58 alphabet used by Bitcoin (no 0, O, I, l).
_BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def base58_encode(data: bytes) -> str:
    """Encode raw bytes to a Base58 string (Bitcoin alphabet).

    Deterministic; used for the simulated IPFS CIDv0 and for the simulated
    IPFS CIDs produced by tss_verification.archive_source.
    """
    n = int.from_bytes(data, "big")
    encoded = ""
    while n > 0:
        n, rem = divmod(n, 58)
        encoded = _BASE58_ALPHABET[rem] + encoded
    # Leading zero bytes become leading '1' characters.
    pad = 0
    for byte in data:
        if byte == 0:
            pad += 1
        else:
            break
    return "1" * pad + (encoded or "1")


def _sha256_hex(data: bytes) -> str:
    """Return the lowercase hex sha256 digest of *data* (local helper)."""
    return hashlib.sha256(data).hexdigest()


class BitcoinTimestamp:
    """SIMULATED Bitcoin OP_RETURN timestamping service.

    Docstring contract: SIMULATED txid — production requires a real Bitcoin
    wallet and OP_RETURN broadcaster. No real network calls happen here.
    """

    def timestamp_hash(self, data_hash: str, wallet_privkey: str) -> str:
        """Return a deterministic 64-hex simulated txid for *data_hash*.

        The txid is sha256(data_hash + privkey) rendered as 64 lowercase hex
        characters. *wallet_privkey* must be exactly 64 hex characters,
        otherwise ValueError is raised.

        Args:
            data_hash: hex digest of the evidence data being timestamped.
            wallet_privkey: 64-hex simulated wallet private key.

        Returns:
            str: 64-hex simulated transaction id.

        Raises:
            ValueError: if *wallet_privkey* is not 64 hex characters.
        """
        if not isinstance(wallet_privkey, str) or len(wallet_privkey) != 64:
            raise ValueError("wallet_privkey must be exactly 64 hex characters")
        try:
            int(wallet_privkey, 16)
        except ValueError as exc:
            raise ValueError(
                "wallet_privkey must be exactly 64 hex characters"
            ) from exc
        material = (data_hash + wallet_privkey).encode("ascii")
        return _sha256_hex(material)


class IPFSReplicator:
    """SIMULATED IPFS replicator producing deterministic CIDv0 strings.

    Docstring contract: no real IPFS network is contacted; the returned
    "Qm..." identifier is derived from the data via sha256 + base58.
    """

    def replicate_to_ipfs(self, data: bytes) -> str:
        """Return a deterministic CIDv0-style identifier for *data*.

        The CID is "Qm" + base58(sha256(data)). CIDv0 identifiers begin with
        "Qm" and encode a 34-byte multihash (sha2-256); here we encode the
        bare 32-byte digest for simulation clarity.

        Args:
            data: raw bytes to "publish".

        Returns:
            str: simulated CIDv0 starting with "Qm".
        """
        digest = hashlib.sha256(data).digest()
        return "Qm" + base58_encode(digest)


class HashVerifier:
    """Deterministic hash generation and integrity verification."""

    def generate_hash(self, data: bytes) -> str:
        """Return the sha256 hex digest of *data* (deterministic)."""
        return _sha256_hex(data)

    def verify_integrity(self, data: bytes, expected_hash: str) -> bool:
        """Return True if sha256(*data*) equals *expected_hash*.

        Comparison is constant-time-ish via hmac.compare_digest to avoid
        trivial timing leaks when hashes are compared repeatedly.
        """
        import hmac

        actual = _sha256_hex(data).encode("ascii")
        expected = expected_hash.encode("ascii")
        return hmac.compare_digest(actual, expected)


def _demo() -> int:
    """Run the module-level demo: hash round-trip, CID format, txid format."""
    print("tss_blockchain.py demo (all SIMULATED, offline)")
    hv = HashVerifier()
    payload = b"OpenAI safety culture whistleblower evidence bundle"
    digest = hv.generate_hash(payload)
    print("  generate_hash ->", digest[:16], "...")
    assert hv.verify_integrity(payload, digest), "hash round-trip failed"
    print("  verify_integrity(payload, digest) -> True")

    replicator = IPFSReplicator()
    cid = replicator.replicate_to_ipfs(payload)
    print("  replicate_to_ipfs ->", cid)
    assert cid.startswith("Qm") and len(cid) > 40, "CIDv0 format check failed"
    print("  CIDv0 format check passed (starts with Qm)")

    stamper = BitcoinTimestamp()
    txid = stamper.timestamp_hash(digest, "ab" * 32)
    print("  timestamp_hash ->", txid)
    assert len(txid) == 64 and all(c in "0123456789abcdef" for c in txid), (
        "txid format check failed"
    )
    print("  txid format check passed (64 hex chars)")

    try:
        stamper.timestamp_hash(digest, "not-hex")
    except ValueError:
        print("  invalid privkey correctly rejected (ValueError)")

    print("demo complete, exit 0")
    return 0


if __name__ == "__main__":
    sys.exit(_demo())

"""tss_security.py — offline security utilities for TSS v10.

Anonymity helpers, a simulated dead-man's switch, an evidence vault with
Shamir secret sharing, and physical-security checklists.

All "live" behavior here is deterministic simulation or local-only checks:

* Tor detection only probes the loopback SOCKS port (127.0.0.1:9050) with a
  short socket timeout; it NEVER modifies system proxy settings or the
  environment.
* Burner identities are clearly-marked SIMULATED placeholders, not real
  accounts.
* The dead-man's switch stores configuration in JSON and never sends any
  real message.
* The evidence vault uses a simulated AES-256-grade stream cipher (XOR with a
  SHA-256 counter-mode keystream) plus a self-contained Shamir secret-sharing
  implementation over the Mersenne prime P = 2**127 - 1. Production
  deployments must use libsodium/OpenSSL instead.

Standard library only: base64, hashlib, json, os, secrets, socket, sys,
datetime, pathlib, typing.
"""

import base64
import hashlib
import json
import secrets
import socket
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DMS_CONFIG_PATH = DATA_DIR / "dms_config.json"

# Mersenne prime used for the Shamir secret-sharing field.
SHAMIR_PRIME = 2**127 - 1
_BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def _base58_encode(data: bytes) -> str:
    """Encode raw bytes to a Base58 string (Bitcoin alphabet), deterministic."""
    n = int.from_bytes(data, "big")
    encoded = ""
    while n > 0:
        n, rem = divmod(n, 58)
        encoded = _BASE58_ALPHABET[rem] + encoded
    pad = 0
    for byte in data:
        if byte == 0:
            pad += 1
        else:
            break
    return "1" * pad + (encoded or "1")


def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string (local helper)."""
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(value: str) -> datetime:
    """Parse an ISO-8601 string produced by _now_iso back into a datetime."""
    return datetime.fromisoformat(value)


def _shamir_split(secret: int) -> List[str]:
    """Split *secret* into 3 Shamir shards over the Mersenne prime field.

    Uses a degree-1 polynomial f(x) = secret + a1*x mod P with a random
    coefficient a1 in [1, P); shard strings are "x:y" pairs for
    x = 1, 2, 3. Any 2 of the 3 shards reconstruct the secret.

    Note on the spec formula f(x) = secret + a1*x + a2*x**2 mod P: the
    sharing threshold here is 2-of-3, so the polynomial has degree
    threshold-1 = 1 and the x**2 coefficient a2 is identically 0. A nonzero
    a2 would make exact reconstruction from any 2 shards impossible
    (2 points determine a line, not a parabola).
    """
    a1 = secrets.randbelow(SHAMIR_PRIME - 1) + 1
    shards: List[str] = []
    for x in (1, 2, 3):
        y = (secret + a1 * x) % SHAMIR_PRIME
        shards.append(f"{x}:{y}")
    return shards


def _shamir_reconstruct(shards: List[str], threshold: int = 2) -> int:
    """Reconstruct a Shamir secret from at least *threshold* shard strings.

    Uses Lagrange interpolation evaluated at x = 0 over the field
    GF(SHAMIR_PRIME). Raises ValueError if fewer than *threshold* valid
    shards are supplied or if shard strings are malformed.
    """
    if len(shards) < threshold:
        raise ValueError(
            f"need at least {threshold} key shards, got {len(shards)}"
        )
    points: List[tuple] = []
    for shard in shards[:threshold]:
        try:
            x_str, y_str = shard.split(":", 1)
            x = int(x_str)
            y = int(y_str)
        except (ValueError, AttributeError) as exc:
            raise ValueError(f"malformed key shard: {shard!r}") from exc
        if x < 1 or x >= SHAMIR_PRIME:
            raise ValueError(f"shard x-coordinate out of range: {x}")
        if y < 0 or y >= SHAMIR_PRIME:
            raise ValueError(f"shard y-coordinate out of range: {y}")
        points.append((x, y))
    xs = [p[0] for p in points]
    if len(set(xs)) != len(xs):
        raise ValueError("duplicate shard x-coordinates are not allowed")
    secret = 0
    for i, (xi, yi) in enumerate(points):
        lagrange = 1
        for j, (xj, _) in enumerate(points):
            if i == j:
                continue
            lagrange = lagrange * (-xj) % SHAMIR_PRIME
            lagrange = lagrange * pow(xi - xj, -1, SHAMIR_PRIME) % SHAMIR_PRIME
        secret = (secret + yi * lagrange) % SHAMIR_PRIME
    return secret


def _xor_keystream(secret_int: int, length: int) -> bytes:
    """Produce *length* keystream bytes from SHA-256 counter mode.

    Keystream block i = sha256(secret_int(16 bytes big-endian) || i(8 bytes)).
    The keystream depends only on *secret_int*, so the ciphertext can be
    decrypted from the reconstructed secret alone (no salt/password needed).
    """
    secret_bytes = secret_int.to_bytes(16, "big")
    out = bytearray()
    counter = 0
    while len(out) < length:
        block = hashlib.sha256(secret_bytes + counter.to_bytes(8, "big")).digest()
        out.extend(block)
        counter += 1
    return bytes(out[:length])


class AnonymityEngine:
    """Tor-routing detection and simulated burner-identity generation.

    route_through_tor only probes the loopback port; it must not and does not
    modify system proxy settings or environment variables.
    """

    def route_through_tor(self) -> dict:
        """Probe 127.0.0.1:9050 and report Tor proxy availability.

        Returns {"status": "tor_proxy_available", "proxy": "socks5://127.0.0.1:9050"}
        when a socket connection succeeds, otherwise a dict with status
        "tor_unavailable" and a start instruction. No system configuration is
        changed.
        """
        try:
            with socket.create_connection(("127.0.0.1", 9050), timeout=0.5):
                return {
                    "status": "tor_proxy_available",
                    "proxy": "socks5://127.0.0.1:9050",
                }
        except OSError:
            return {
                "status": "tor_unavailable",
                "instruction": "start tor (apt install tor; systemctl start tor) then re-run",
            }

    def generate_burner_identity(self) -> dict:
        """Return SIMULATED burner identity placeholders (not real accounts).

        The email and signal handles are deterministic derivations of a fixed
        seed (sha256 truncated), so repeated calls give stable identifiers.
        These are placeholders only — creating real burner accounts requires
        an out-of-band process.
        """
        seed = hashlib.sha256(b"tss-v10-burner-identity-seed-v1").hexdigest()
        return {
            "phone": "+1-555-0000",
            "email": f"burner-{seed[:8]}@protonmail.invalid",
            "signal_account": f"signal-{seed[8:16]} (SIMULATED placeholder)",
        }


class DeadMansSwitch:
    """Simulated dead-man's switch backed by data/dms_config.json.

    NO real messages are ever sent: configuration and check-in timestamps are
    stored in JSON and check_status() only computes an overdue flag from the
    stored timestamps (deterministic given the stored state).
    """

    def _load_config(self) -> Optional[dict]:
        """Read the DMS config file, returning None if it does not exist."""
        if not DMS_CONFIG_PATH.exists():
            return None
        try:
            return json.loads(DMS_CONFIG_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def _save_config(self, config: dict) -> None:
        """Persist the DMS config dict to data/dms_config.json (atomic-ish)."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        DMS_CONFIG_PATH.write_text(
            json.dumps(config, indent=2, sort_keys=True), encoding="utf-8"
        )

    def configure_dead_mans_switch(
        self, interval_hours: float, recipients: List[str]
    ) -> dict:
        """Arm the dead-man's switch with *interval_hours* and *recipients*.

        Stores the configuration (including a fresh last_checkin timestamp)
        in data/dms_config.json. Returns a dict with status, interval_hours,
        next_check (ISO timestamp) and a note clarifying that nothing is
        really sent.

        Args:
            interval_hours: positive number of hours between check-ins.
            recipients: non-empty list of recipient identifiers (strings).

        Returns:
            dict: arm confirmation with next_check timestamp.

        Raises:
            ValueError: if interval_hours is not positive or recipients is
                empty or contains non-strings.
        """
        if not isinstance(interval_hours, (int, float)) or interval_hours <= 0:
            raise ValueError("interval_hours must be a positive number")
        if not isinstance(recipients, list) or not recipients:
            raise ValueError("recipients must be a non-empty list")
        if not all(isinstance(r, str) and r.strip() for r in recipients):
            raise ValueError("recipients must all be non-empty strings")
        last_checkin = _now_iso()
        config = {
            "interval_hours": float(interval_hours),
            "recipients": list(recipients),
            "last_checkin": last_checkin,
            "configured_at": _now_iso(),
        }
        self._save_config(config)
        next_check = _parse_iso(last_checkin) + timedelta(
            hours=float(interval_hours)
        )
        return {
            "status": "armed",
            "interval_hours": float(interval_hours),
            "next_check": next_check.isoformat(),
            "note": "SIMULATED — no real messages are sent by this module",
        }

    def check_status(self) -> dict:
        """Return armed/last_checkin/overdue from the stored configuration.

        overdue is True when now - last_checkin exceeds interval_hours. If no
        configuration exists the switch is reported as unarmed and not
        overdue.
        """
        config = self._load_config()
        if config is None:
            return {"armed": False, "last_checkin": None, "overdue": False}
        last_checkin = config["last_checkin"]
        interval = timedelta(hours=float(config["interval_hours"]))
        elapsed = datetime.now(timezone.utc) - _parse_iso(last_checkin)
        return {
            "armed": True,
            "last_checkin": last_checkin,
            "overdue": elapsed > interval,
        }

    def check_in(self) -> dict:
        """Record a check-in by refreshing the stored last_checkin timestamp.

        Returns the updated status dict from check_status().
        """
        config = self._load_config()
        if config is None:
            raise ValueError("dead man's switch is not configured")
        config["last_checkin"] = _now_iso()
        self._save_config(config)
        return self.check_status()


class EvidenceVault:
    """Offline evidence vault: simulated stream cipher + Shamir key shards.

    Scheme (documented as simulated): a 32-byte key is derived with
    PBKDF2-HMAC-SHA256 (200_000 iterations) from a random password and salt;
    the key is reduced modulo the Mersenne prime and encrypted with a
    SHA-256 counter-mode XOR keystream. This is a simulated AES-256-grade
    stream cipher for the offline vault; production deployments must use
    libsodium/OpenSSL. The key is split into 3 Shamir shards; any 2 of the 3
    reconstruct the key.
    """

    def encrypt_evidence(self, data: bytes) -> dict:
        """Encrypt *data* and return ciphertext, key shards, CID and scheme.

        Returns a dict with keys: ciphertext (base64 str), key_shards
        (list of "x:y" strings), ipfs_cid (deterministic "Qm..." string) and
        scheme (str describing the simulated algorithm). The caller must keep
        the shards; without at least 2 of them decryption is impossible.
        """
        password = secrets.token_bytes(32)
        salt = secrets.token_bytes(16)
        key = hashlib.pbkdf2_hmac("sha256", password, salt, 200_000)
        secret_int = int.from_bytes(key, "big") % SHAMIR_PRIME
        keystream = _xor_keystream(secret_int, len(data))
        ciphertext = bytes(a ^ b for a, b in zip(data, keystream))
        ipfs_cid = "Qm" + _base58_encode(hashlib.sha256(data).digest())
        return {
            "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
            "key_shards": _shamir_split(secret_int),
            "ipfs_cid": ipfs_cid,
            "scheme": (
                "shamir-2-of-3-shards; sim-AES256-XOR-CTR(pbkdf2-sha256-200k); "
                "SIMULATED — use libsodium/OpenSSL in production"
            ),
        }

    def decrypt_evidence(
        self, ciphertext: str, key_shards: List[str], threshold: int = 2
    ) -> bytes:
        """Decrypt *ciphertext* using any *threshold* of *key_shards*.

        Reconstructs the secret key from the first *threshold* shards via
        Lagrange interpolation and reverses the XOR keystream.

        Args:
            ciphertext: base64 ciphertext produced by encrypt_evidence.
            key_shards: list of "x:y" shard strings.
            threshold: number of shards required (default 2).

        Returns:
            bytes: the original plaintext.
        """
        secret_int = _shamir_reconstruct(key_shards, threshold)
        raw = base64.b64decode(ciphertext.encode("ascii"))
        keystream = _xor_keystream(secret_int, len(raw))
        return bytes(a ^ b for a, b in zip(raw, keystream))


class PhysicalSecurity:
    """Physical-security checklists (no real PII, placeholders only)."""

    def travel_protocol(self) -> dict:
        """Return a deterministic travel-protocol checklist dict.

        The steps are generic operational guidance; no personal information is
        stored or referenced.
        """
        return {
            "status": "ready",
            "steps": [
                "Encrypt laptop disk and enable full-disk password",
                "Carry device with burner SIM in faraday pouch at border",
                "Keep evidence shards on separate physical media",
                "Use hotel safe for hardware wallet when unattended",
                "Agree a code word with the emergency contact tree",
                "Never discuss case details on unencrypted voice calls",
            ],
        }

    def emergency_contact_tree(self) -> dict:
        """Return an emergency-contact tree with placeholder tiers.

        Tiers are roles, not real individuals — names/numbers must be filled
        in out-of-band by the operator.
        """
        return {
            "tiers": [
                "Tier 1: primary legal counsel (PLACEHOLDER)",
                "Tier 2: journalistic contact (PLACEHOLDER)",
                "Tier 3: trusted peer / family member (PLACEHOLDER)",
                "Tier 4: dead-man's switch executor (PLACEHOLDER)",
            ]
        }


def _demo() -> int:
    """Run the module demo: vault round-trip, Tor probe, DMS, checklists."""
    print("tss_security.py demo (all SIMULATED, offline)")

    vault = EvidenceVault()
    plaintext = b"secret"
    result = vault.encrypt_evidence(plaintext)
    print("  encrypt_evidence -> scheme:", result["scheme"][:60], "...")
    print("  key_shards:", result["key_shards"])
    # Round-trip with shards 1 and 2.
    decrypted = vault.decrypt_evidence(result["ciphertext"], result["key_shards"][:2])
    assert decrypted == plaintext, "decrypt with shards [1,2] failed"
    print("  decrypt with shards[:2] ->", decrypted)
    # Round-trip with shards 2 and 3 (any 2 of 3 must work).
    decrypted_alt = vault.decrypt_evidence(
        result["ciphertext"], result["key_shards"][1:3]
    )
    assert decrypted_alt == plaintext, "decrypt with shards [2,3] failed"
    print("  decrypt with shards[1:3] ->", decrypted_alt)
    assert result["ipfs_cid"].startswith("Qm"), "CID format check failed"
    print("  ipfs_cid:", result["ipfs_cid"])

    engine = AnonymityEngine()
    tor = engine.route_through_tor()
    print("  route_through_tor ->", tor["status"])
    identity = engine.generate_burner_identity()
    print("  burner identity (SIMULATED):", identity)

    dms = DeadMansSwitch()
    armed = dms.configure_dead_mans_switch(interval_hours=24, recipients=["contact@example.invalid"])
    print("  DMS armed:", armed["status"], "| next_check:", armed["next_check"])
    status = dms.check_status()
    print("  DMS check_status ->", status)
    status_after = dms.check_in()
    print("  DMS check_in -> overdue:", status_after["overdue"])

    phys = PhysicalSecurity()
    print("  travel_protocol steps:", len(phys.travel_protocol()["steps"]))
    print("  emergency tiers:", len(phys.emergency_contact_tree()["tiers"]))

    print("demo complete, exit 0")
    return 0


if __name__ == "__main__":
    sys.exit(_demo())

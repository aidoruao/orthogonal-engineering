"""Number-theory helpers with proof objects for PR #83."""

from __future__ import annotations

from typing import List, Sequence, Tuple

from axioms.logic import ProofObject
from axioms.peano import peano_mul


def mod_peano(a: int, modulus: int) -> int:
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    sign = -1 if a < 0 else 1
    remainder = abs(a)
    while remainder >= modulus:
        remainder -= modulus
    if sign > 0:
        return remainder
    return 0 if remainder == 0 else modulus - remainder


def is_prime(n: int) -> Tuple[bool, ProofObject]:
    if n < 2:
        return False, ProofObject("IsPrime", [f"n = {n} < 2"], f"{n} is not prime")
    divisor = 2
    factors: List[int] = []
    while divisor * divisor <= n:
        if mod_peano(n, divisor) == 0:
            factors.append(divisor)
        divisor += 1
    result = not factors
    premises = [f"checked divisors up to floor(sqrt({n}))"]
    premises.extend(f"divides by {factor}" for factor in factors)
    conclusion = f"{n} is {'prime' if result else 'composite'}"
    return result, ProofObject("IsPrime", premises, conclusion)


def gcd_extended(a: int, b: int) -> Tuple[Tuple[int, int, int], ProofObject]:
    old_r, r = abs(a), abs(b)
    old_s, s = 1, 0
    old_t, t = 0, 1
    steps = [f"start: r0={old_r}, r1={r}"]
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
        steps.append(f"q={quotient}, r={old_r}, next={r}, s={old_s}, t={old_t}")
    coeff_a = old_s if a >= 0 else -old_s
    coeff_b = old_t if b >= 0 else -old_t
    result = (old_r, coeff_a, coeff_b)
    return result, ProofObject(
        "ExtendedGCD",
        steps,
        f"gcd({a}, {b}) = {old_r} with coefficients ({coeff_a}, {coeff_b})",
    )


def bezout(a: int, b: int) -> Tuple[Tuple[int, int], ProofObject]:
    (gcd_value, x, y), proof = gcd_extended(a, b)
    identity = a * x + b * y
    return (x, y), ProofObject(
        "BezoutIdentity",
        [proof, f"{a}*{x} + {b}*{y} = {identity}"],
        f"Bezout identity holds with gcd {gcd_value}",
    )


def euler_totient(n: int) -> Tuple[int, ProofObject]:
    if n <= 0:
        raise ValueError("n must be positive")
    coprimes = [k for k in range(1, n + 1) if gcd_extended(k, n)[0][0] == 1]
    return len(coprimes), ProofObject(
        "EulerTotient",
        [f"coprimes to {n}: {coprimes}"],
        f"phi({n}) = {len(coprimes)}",
    )


def modular_exponentiation(base: int, exponent: int, modulus: int) -> Tuple[int, ProofObject]:
    if exponent < 0:
        raise ValueError("exponent must be non-negative")
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    result = 1 % modulus
    factor = mod_peano(base, modulus)
    power = exponent
    steps = [f"start result={result}, factor={factor}, exponent={power}"]
    while power > 0:
        if power & 1:
            result = mod_peano(peano_mul(result, factor), modulus)
            steps.append(f"multiply -> {result}")
        factor = mod_peano(peano_mul(factor, factor), modulus)
        power >>= 1
        steps.append(f"square factor -> {factor}, exponent -> {power}")
    return result, ProofObject(
        "ModularExponentiation",
        steps,
        f"{base}^{exponent} mod {modulus} = {result}",
    )


def fermat_little(a: int, p: int) -> Tuple[bool, ProofObject]:
    prime, prime_proof = is_prime(p)
    if not prime:
        return False, ProofObject("FermatLittle", [prime_proof], f"{p} is not prime")
    if mod_peano(a, p) == 0:
        return True, ProofObject(
            "FermatLittle",
            [prime_proof, f"{a} ≡ 0 (mod {p})"],
            "Trivial Fermat case holds because a is divisible by p",
        )
    value, exp_proof = modular_exponentiation(a, p - 1, p)
    result = value == 1
    return result, ProofObject(
        "FermatLittle",
        [prime_proof, exp_proof],
        f"a^(p-1) mod p = {value}; theorem is {'verified' if result else 'falsified'}",
    )


def chinese_remainder_theorem(residues: Sequence[int], moduli: Sequence[int]) -> Tuple[int, ProofObject]:
    if len(residues) != len(moduli) or not residues:
        raise ValueError("residues and moduli must be non-empty and the same length")
    product = 1
    for modulus in moduli:
        product *= modulus
    x = 0
    steps: List[str] = [f"product={product}"]
    for residue, modulus in zip(residues, moduli):
        partial = product // modulus
        (gcd_value, inverse, _), gcd_proof = gcd_extended(partial, modulus)
        if gcd_value != 1:
            raise ValueError("moduli must be pairwise coprime")
        inverse %= modulus
        contribution = residue * partial * inverse
        x += contribution
        steps.extend([gcd_proof.conclusion, f"contribution={contribution}"])
    solution = x % product
    return solution, ProofObject(
        "ChineseRemainderTheorem",
        steps,
        f"CRT solution = {solution} mod {product}",
    )

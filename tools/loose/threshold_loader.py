"""
Threshold configuration loader.

Reads YAML threshold configs and CLI overrides, returning Fraction objects.
"""

from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional


def _parse_fraction(value: str) -> Fraction:
    """Parse a rational string (e.g., '247/1' or '3/2') into a Fraction."""
    value = value.strip()
    if "/" in value:
        num, den = value.split("/", 1)
        return Fraction(int(num.strip()), int(den.strip()))
    return Fraction(int(value), 1)


def load_thresholds(
    path: Optional[str] = None,
    overrides: Optional[List[str]] = None,
) -> Dict[str, Fraction]:
    """
    Load thresholds from config file and apply CLI overrides.

    Precedence: overrides > config file > hard-coded defaults.

    Args:
        path: Path to YAML config file.
        overrides: List of "key=value" strings from CLI.

    Returns:
        Dictionary mapping threshold names to Fraction values.
    """
    defaults = {
        "certain": Fraction(247, 1),
        "high_confidence": Fraction(200, 1),
        "probable": Fraction(150, 1),
        "unknown": Fraction(100, 1),
        "suspicious": Fraction(50, 1),
        "invalid": Fraction(0, 1),
    }

    result = dict(defaults)

    if path:
        config_path = Path(path)
        if config_path.exists():
            try:
                import yaml

                with open(config_path, "r") as f:
                    data = yaml.safe_load(f)
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, str):
                            result[key] = _parse_fraction(value)
                        elif isinstance(value, (int, float)):
                            # Avoid float if possible; but if given as float, convert via str
                            result[key] = Fraction(str(value))
            except Exception:
                # If YAML fails, fall back to defaults
                pass

    if overrides:
        for override in overrides:
            if "=" not in override:
                continue
            key, value = override.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key and value:
                result[key] = _parse_fraction(value)

    return result

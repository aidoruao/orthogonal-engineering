# pr47_stewardship/identification/sensitivity_classifier.py
# PR #47 — Sanctified Remembrance
# Standard: Yeshua
#
# SensitivityClassifier: maps reason codes to recommended actions.
# Actions determine what the WitnessMover will do with a Candidate.

from __future__ import annotations

from enum import Enum


class Action(str, Enum):
    """Recommended disposition for an artifact."""
    KEEP_PUBLIC = "keep_public"
    MOVE_LOCAL = "move_local"
    ENCRYPT_LOCAL = "encrypt_local"
    DELETE_WITH_WITNESS = "delete_with_witness"


# Default mapping from reason code to action.
# Codes with no explicit mapping default to MOVE_LOCAL.
DEFAULT_ACTION_MAP: dict[str, Action] = {
    "R1": Action.MOVE_LOCAL,
    "R2": Action.MOVE_LOCAL,
    "R3": Action.MOVE_LOCAL,
    "R4": Action.MOVE_LOCAL,
    "R5": Action.ENCRYPT_LOCAL,
}


class SensitivityClassifier:
    """
    Maps opaque reason codes to dispositions.

    Parameters:
      action_map — override or extend the default code→action mapping.
      default    — fallback action when a code is not in action_map.
    """

    def __init__(
        self,
        action_map: dict[str, Action] | None = None,
        default: Action = Action.MOVE_LOCAL,
    ) -> None:
        self._map: dict[str, Action] = dict(DEFAULT_ACTION_MAP)
        if action_map:
            self._map.update(action_map)
        self._default = default

    def classify(self, reason_code: str) -> Action:
        """Return the recommended Action for reason_code."""
        return self._map.get(reason_code, self._default)

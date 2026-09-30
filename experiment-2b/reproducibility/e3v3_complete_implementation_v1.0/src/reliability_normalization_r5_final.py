
"""
E3-v3 R5 — deterministic reliability normalization.

Scope
-----
Normalize/reconcile explicitly source-grounded reliability values onto
the canonical CIR [0,1] scale.

This module:
* does not perform service extraction;
* does not resolve qualitative requirements;
* does not modify source analysis;
* does not modify R4;
* does not invent reliability values;
* does not mutate the input CIR.

R5 is applied after R4 reconciliation and before source-to-CIR
preservation.

The source-bound constraint representation remains authoritative for
comparison operators. CIR stores only the scalar reliability threshold.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import math
import re


EPSILON = 1e-12


@dataclass(frozen=True)
class ReliabilityEvidence:
    value: float
    operator: Optional[str]
    source_text: Optional[str]
    explicit_percent: bool


def _finite_number(value: Any) -> Optional[float]:
    """
    Convert an int/float numeric value to finite float.

    bool is deliberately excluded because bool is a subclass of int.
    """

    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        value = float(value)

        if math.isfinite(value):
            return value

    return None


def _parse_numeric_string(value: Any) -> Optional[float]:
    """
    Parse a plain numeric string.

    Percentage signs are handled separately because their interpretation
    requires source evidence.
    """

    if not isinstance(value, str):
        return None

    text = value.strip()

    if not re.fullmatch(
        r"[+-]?(?:\d+(?:\.\d+)?|\.\d+)",
        text
    ):
        return None

    try:
        number = float(text)
    except ValueError:
        return None

    if not math.isfinite(number):
        return None

    return number


def _parse_percentage_string(value: Any) -> Optional[float]:
    """
    Parse a literal percentage string such as '99.9%'.

    Returns the raw percentage number (99.9), not 0.999.
    """

    if not isinstance(value, str):
        return None

    text = value.strip()

    match = re.fullmatch(
        r"([+-]?(?:\d+(?:\.\d+)?|\.\d+))\s*%",
        text
    )

    if not match:
        return None

    try:
        number = float(match.group(1))
    except ValueError:
        return None

    if not math.isfinite(number):
        return None

    return number


def _constraint_field(constraint: Any) -> Optional[str]:
    if isinstance(constraint, dict):
        return constraint.get("field")

    return getattr(constraint, "field", None)


def _constraint_value(constraint: Any) -> Any:
    if isinstance(constraint, dict):
        return constraint.get("value")

    return getattr(constraint, "value", None)


def _constraint_operator(constraint: Any) -> Optional[str]:
    if isinstance(constraint, dict):
        return constraint.get("operator")

    return getattr(constraint, "operator", None)


def _constraint_source_text(constraint: Any) -> Optional[str]:
    if isinstance(constraint, dict):
        return constraint.get("source_text")

    return getattr(constraint, "source_text", None)


def _constraints(source_intent: Any) -> List[Any]:
    if source_intent is None:
        return []

    if isinstance(source_intent, dict):
        value = source_intent.get("constraints", [])
    else:
        value = getattr(source_intent, "constraints", [])

    if not isinstance(value, (list, tuple)):
        return []

    return list(value)


def _source_reliability_evidence(
    source_intent: Any
) -> List[ReliabilityEvidence]:
    """
    Collect deterministic reliability evidence.

    Current source analysis already normalizes explicit percentages to
    [0,1]. The source_text is retained to distinguish whether the
    original expression used '%'.
    """

    evidence = []

    for constraint in _constraints(source_intent):

        if _constraint_field(constraint) != "reliability":
            continue

        raw = _constraint_value(constraint)
        number = _finite_number(raw)

        if number is None:
            continue

        source_text = _constraint_source_text(constraint)

        explicit_percent = (
            isinstance(source_text, str)
            and "%" in source_text
        )

        # Source analyzer normally already produces [0,1].
        #
        # For defensive compatibility, if the deterministic source
        # representation still contains the percentage magnitude and
        # the literal source proves percentage semantics, normalize it.
        if explicit_percent and number > 1.0:
            number = number / 100.0

        if number < 0.0 or number > 1.0:
            continue

        evidence.append(
            ReliabilityEvidence(
                value=number,
                operator=_constraint_operator(constraint),
                source_text=source_text,
                explicit_percent=explicit_percent,
            )
        )

    return evidence


def _unique_source_value(
    evidence: List[ReliabilityEvidence]
) -> Optional[float]:
    """
    Return one unambiguous source threshold.

    Multiple constraints with materially different thresholds are not
    collapsed by R5.
    """

    if not evidence:
        return None

    values = []

    for item in evidence:
        if not any(
            math.isclose(
                item.value,
                existing,
                rel_tol=0.0,
                abs_tol=EPSILON
            )
            for existing in values
        ):
            values.append(item.value)

    if len(values) != 1:
        return None

    return values[0]


def _same_value(a: float, b: float) -> bool:
    return math.isclose(
        a,
        b,
        rel_tol=0.0,
        abs_tol=EPSILON
    )


def normalize_reliability(
    source_intent: Any,
    cir: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Return a new CIR with deterministic R5 reliability normalization.

    Policy
    ------
    1. No source reliability evidence -> no repair.
    2. Multiple distinct source reliability thresholds -> no repair.
    3. Missing CIR reliability -> fill from unambiguous source.
    4. Canonical CIR reliability already matching source -> preserve.
    5. CIR numeric percentage magnitude (e.g. 99.9) -> convert only if
       source evidence proves the corresponding value is 0.999.
    6. CIR percentage string (e.g. '99.9%') -> convert only if source
       evidence proves the corresponding value.
    7. CIR numeric string in canonical [0,1] -> canonicalize to float
       only if it matches source evidence.
    8. A different semantic value is never overwritten merely to make
       validation pass.
    """

    if not isinstance(cir, dict):
        raise TypeError("cir must be a dictionary")

    out = deepcopy(cir)

    evidence = _source_reliability_evidence(
        source_intent
    )

    source_value = _unique_source_value(
        evidence
    )

    if source_value is None:
        return out

    current = out.get("reliability")

    # --------------------------------------------------------------
    # Missing CIR reliability
    # --------------------------------------------------------------

    if current is None:
        out["reliability"] = source_value
        return out

    # --------------------------------------------------------------
    # Numeric CIR
    # --------------------------------------------------------------

    numeric = _finite_number(current)

    if numeric is not None:

        # Already canonical and semantically matching.
        if 0.0 <= numeric <= 1.0:

            if _same_value(
                numeric,
                source_value
            ):
                return out

            # Different semantic value: do not overwrite.
            return out

        # Percentage-like numeric magnitude.
        if 1.0 < numeric <= 100.0:

            candidate = numeric / 100.0

            if _same_value(
                candidate,
                source_value
            ):
                out["reliability"] = candidate

            return out

        return out

    # --------------------------------------------------------------
    # Literal percentage string
    # --------------------------------------------------------------

    percent = _parse_percentage_string(
        current
    )

    if percent is not None:

        if 0.0 <= percent <= 100.0:

            candidate = percent / 100.0

            if _same_value(
                candidate,
                source_value
            ):
                out["reliability"] = candidate

        return out

    # --------------------------------------------------------------
    # Plain numeric string
    # --------------------------------------------------------------

    parsed = _parse_numeric_string(
        current
    )

    if parsed is not None:

        if (
            0.0 <= parsed <= 1.0
            and _same_value(
                parsed,
                source_value
            )
        ):
            out["reliability"] = parsed

        return out

    # Unknown representation -> fail closed by leaving unchanged.
    return out


def reliability_changed(
    before: Dict[str, Any],
    after: Dict[str, Any],
) -> bool:
    """
    Whether R5 changed only the reliability representation/value.
    """

    if not isinstance(before, dict):
        return False

    if not isinstance(after, dict):
        return False

    return (
        before.get("reliability")
        != after.get("reliability")
    )


# ================================================================
# Final R5 residual repair
# ================================================================

_R5_OPERATOR_WORDS = {
    "above": ">",
    "over": ">",
    "greater than": ">",
    "at least": ">=",
    "no lower than": ">=",
    "below": "<",
    "under": "<",
    "less than": "<",
    "at most": "<=",
    "no more than": "<=",
    "exactly": "=",
}


def _r5_constraint_to_dict(value):
    if isinstance(value, dict):
        return value
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return None


def _r5_source_constraints(source_intent):
    if source_intent is None:
        return []

    if isinstance(source_intent, dict):
        values = source_intent.get("constraints", [])
    else:
        values = getattr(source_intent, "constraints", [])

    out = []

    for value in values:
        item = _r5_constraint_to_dict(value)
        if item is not None:
            out.append(item)

    return out


def _r5_parse_operator_reliability(value):
    """
    Parse only explicit operator-bearing reliability text.

    Examples:
        above 99.9%
        at least 99.99%
        exactly 99.5%

    Returns:
        (operator, canonical_value) or None
    """

    if not isinstance(value, str):
        return None

    text = value.strip().lower()

    operator_terms = sorted(
        _R5_OPERATOR_WORDS,
        key=len,
        reverse=True,
    )

    for term in operator_terms:
        pattern = (
            r"^"
            + re.escape(term)
            + r"\s+"
            + r"(?P<value>\d+(?:\.\d+)?)"
            + r"\s*(?P<percent>%)?"
            + r"$"
        )

        match = re.match(pattern, text)

        if match is None:
            continue

        numeric = float(match.group("value"))

        if match.group("percent"):
            numeric = numeric / 100.0

        return (
            _R5_OPERATOR_WORDS[term],
            numeric,
        )

    return None


def _r5_operator_compatible(source_op, cir_op):
    return source_op == cir_op


def normalize_reliability_final(source_intent, cir):
    """
    Final R5 normalization wrapper.

    1. Apply the previously frozen R5 normalization.
    2. If reliability remains operator-bearing text, canonicalize it
       only when matching deterministic source evidence exists.
    3. Never normalize conflicting operator/value evidence.
    """

    normalized = normalize_reliability(
        source_intent,
        cir,
    )

    if not isinstance(normalized, dict):
        return normalized

    current = normalized.get("reliability")

    parsed = _r5_parse_operator_reliability(current)

    if parsed is None:
        return normalized

    cir_op, cir_value = parsed

    source_rel = [
        c
        for c in _r5_source_constraints(source_intent)
        if c.get("field") == "reliability"
    ]

    if len(source_rel) != 1:
        return normalized

    source = source_rel[0]

    source_op = (
        source.get("operator")
        or source.get("op")
        or source.get("relation")
    )

    source_value = source.get("value")

    try:
        source_value = float(source_value)
    except (TypeError, ValueError):
        return normalized

    if not _r5_operator_compatible(
        source_op,
        cir_op,
    ):
        return normalized

    if abs(source_value - cir_value) > 1e-12:
        return normalized

    result = dict(normalized)
    result["reliability"] = source_value

    return result

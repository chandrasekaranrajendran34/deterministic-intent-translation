"""
R4 — Source-Grounded CIR Reconciliation
=======================================

Experiment 2B / E3-v3.

Purpose
-------
Repair a narrow semantic-construction failure:

    explicit source constraint
            +
    LLM CIR field == None
            ->
    deterministically restore the explicit source threshold

This module does NOT perform general semantic inference.

Safety properties
-----------------
1. Never overwrite a non-null CIR value.
2. Never invent a threshold.
3. Never resolve ambiguous/conflicting same-field thresholds.
4. Never modify service_type.
5. Never modify qualitative fields.
6. Never add fields outside the canonical CIR.
7. Operator semantics remain in the R3 source-bound sidecar.
"""

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Optional


CANONICAL_CIR_FIELDS = (
    "service_type",
    "latency_ms",
    "bandwidth_mbps",
    "reliability",
    "device_count",
    "coverage",
    "objective",
)


RECONCILABLE_NUMERIC_FIELDS = {
    "latency_ms",
    "bandwidth_mbps",
    "reliability",
    "device_count",
}


def _constraint_field(constraint: Any):

    if isinstance(constraint, dict):
        return constraint.get("field")

    return getattr(
        constraint,
        "field",
        None,
    )


def _constraint_value(constraint: Any):

    if isinstance(constraint, dict):
        return constraint.get("value")

    return getattr(
        constraint,
        "value",
        None,
    )


def _constraints(source_intent: Any):

    if source_intent is None:
        return []

    if isinstance(source_intent, dict):

        value = source_intent.get(
            "constraints",
            [],
        )

        return (
            value
            if isinstance(value, list)
            else []
        )

    value = getattr(
        source_intent,
        "constraints",
        [],
    )

    return (
        list(value)
        if value is not None
        else []
    )


def _normalize_threshold(
    field_name: str,
    value: Any,
):

    if value is None:
        return None

    if field_name == "device_count":

        numeric = float(value)

        if not numeric.is_integer():
            return None

        return int(numeric)

    return float(value)


def _unique_thresholds(
    source_intent: Any,
    field_name: str,
):

    values = []

    for constraint in _constraints(
        source_intent
    ):

        if (
            _constraint_field(constraint)
            != field_name
        ):
            continue

        try:

            value = _normalize_threshold(
                field_name,
                _constraint_value(
                    constraint
                ),
            )

        except (
            TypeError,
            ValueError,
        ):

            continue

        if value is None:
            continue

        # Numeric equality is appropriate here because
        # these values originate from deterministic
        # source parsing rather than approximate
        # floating-point computation.

        if value not in values:
            values.append(value)

    return values


def reconcile_cir(
    source_intent: Any,
    cir: Dict[str, Any],
):
    """
    Return a reconciled COPY of the canonical CIR.

    A missing numeric CIR field is filled only when the
    deterministic SourceIntent contains exactly one
    distinct explicit threshold for that field.

    Existing non-null LLM values are never overwritten.
    """

    if not isinstance(cir, dict):

        raise TypeError(
            "cir must be a dict"
        )

    # Preserve only the canonical contract.
    #
    # This prevents R4 from introducing metadata into
    # the closed seven-field CIR schema.

    result = {
        field:
            deepcopy(
                cir.get(field)
            )
        for field in CANONICAL_CIR_FIELDS
    }

    for field_name in (
        "latency_ms",
        "bandwidth_mbps",
        "reliability",
        "device_count",
    ):

        # Never overwrite a non-null LLM value.

        if (
            result.get(field_name)
            is not None
        ):
            continue

        thresholds = _unique_thresholds(
            source_intent,
            field_name,
        )

        # Fail closed on:
        #
        #   0 thresholds
        #   >1 distinct thresholds

        if len(thresholds) != 1:
            continue

        result[field_name] = (
            thresholds[0]
        )

    return result


def reconciliation_diff(
    original_cir: Dict[str, Any],
    reconciled_cir: Dict[str, Any],
):
    """
    Return fields filled by R4.

    Intended for audit logging only.
    """

    changes = []

    for field_name in (
        "latency_ms",
        "bandwidth_mbps",
        "reliability",
        "device_count",
    ):

        before = original_cir.get(
            field_name
        )

        after = reconciled_cir.get(
            field_name
        )

        if (
            before is None
            and after is not None
        ):

            changes.append({
                "field":
                    field_name,

                "before":
                    None,

                "after":
                    after,

                "action":
                    "filled_from_explicit_source_threshold",
            })

    return changes

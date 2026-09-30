
"""
Source-to-CIR preservation checker for Experiment 2B / E3-v2.

Purpose:
Detect when information explicitly represented in the deterministic
source-intent representation disappears or conflicts with the CIR.

Scope:
- service type preservation
- numeric constraint preservation
- exact-value consistency

This is an experimental consistency check, not a standards-
compliance certification mechanism.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from source_intent import (
    SourceIntent,
    NUMERIC_FIELDS,
)


@dataclass(frozen=True)
class PreservationError:

    code: str
    field: str
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PreservationResult:

    valid: bool
    errors: List[PreservationError]

    def to_dict(self) -> Dict[str, Any]:

        return {
            "valid": self.valid,
            "errors": [
                e.to_dict()
                for e in self.errors
            ],
        }


def _get_cir_value(
    cir: Any,
    field_name: str,
) -> Any:
    """
    Supports either dictionary CIRs or objects with attributes.
    """

    if isinstance(cir, dict):
        return cir.get(field_name)

    return getattr(
        cir,
        field_name,
        None,
    )


def _to_float(
    value: Any,
) -> Optional[float]:

    if value is None:
        return None

    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    try:
        return float(value)

    except (TypeError, ValueError):
        return None


def _value_satisfies_constraint(
    cir_value: float,
    operator: str,
    source_value: float,
) -> bool:

    if operator == "=":
        return cir_value == source_value

    if operator == "<":
        return cir_value < source_value

    if operator == "<=":
        return cir_value <= source_value

    if operator == ">":
        return cir_value > source_value

    if operator == ">=":
        return cir_value >= source_value

    return False


def check_preservation(
    source_intent: SourceIntent,
    cir: Any,
) -> PreservationResult:

    errors: List[PreservationError] = []

    # -------------------------------------------------
    # 1. Service-type preservation
    # -------------------------------------------------

    if source_intent.service_type is not None:

        cir_service = _get_cir_value(
            cir,
            "service_type",
        )

        if cir_service is None:

            errors.append(
                PreservationError(
                    code=(
                        "SOURCE_SERVICE_MISSING_FROM_CIR"
                    ),
                    field="service_type",
                    message=(
                        "Source service type "
                        f"{source_intent.service_type!r} "
                        "is missing from CIR."
                    ),
                )
            )

        elif (
            str(cir_service).lower()
            !=
            str(
                source_intent.service_type
            ).lower()
        ):

            errors.append(
                PreservationError(
                    code=(
                        "SOURCE_SERVICE_CONFLICTS_WITH_CIR"
                    ),
                    field="service_type",
                    message=(
                        "Source service type "
                        f"{source_intent.service_type!r} "
                        "conflicts with CIR service type "
                        f"{cir_service!r}."
                    ),
                )
            )

    # -------------------------------------------------
    # 2. Numeric constraint preservation
    # -------------------------------------------------

    for field_name in sorted(
        NUMERIC_FIELDS
    ):

        source_constraints = (
            source_intent.constraints_for(
                field_name
            )
        )

        if not source_constraints:
            continue

        cir_raw = _get_cir_value(
            cir,
            field_name,
        )

        if cir_raw is None:

            errors.append(
                PreservationError(
                    code=(
                        "SOURCE_CONSTRAINT_MISSING_FROM_CIR"
                    ),
                    field=field_name,
                    message=(
                        f"Source contains "
                        f"{len(source_constraints)} "
                        f"constraint(s) for {field_name}, "
                        "but the CIR value is null/missing."
                    ),
                )
            )

            continue

        cir_value = _to_float(
            cir_raw
        )

        if cir_value is None:

            errors.append(
                PreservationError(
                    code="CIR_VALUE_NOT_NUMERIC",
                    field=field_name,
                    message=(
                        f"CIR value for {field_name} "
                        f"is not numeric: {cir_raw!r}"
                    ),
                )
            )

            continue

        for constraint in source_constraints:

            source_value = _to_float(
                constraint.value
            )

            if source_value is None:

                errors.append(
                    PreservationError(
                        code=(
                            "SOURCE_CONSTRAINT_NOT_NUMERIC"
                        ),
                        field=field_name,
                        message=(
                            f"Source constraint for "
                            f"{field_name} is not numeric: "
                            f"{constraint.value!r}"
                        ),
                    )
                )

                continue

            if not _value_satisfies_constraint(
                cir_value,
                constraint.operator,
                source_value,
            ):

                errors.append(
                    PreservationError(
                        code=(
                            "SOURCE_CONSTRAINT_NOT_PRESERVED"
                        ),
                        field=field_name,
                        message=(
                            f"CIR value {cir_value:g} "
                            f"does not satisfy source "
                            f"constraint "
                            f"{constraint.operator} "
                            f"{source_value:g}."
                        ),
                    )
                )

    return PreservationResult(
        valid=(len(errors) == 0),
        errors=errors,
    )

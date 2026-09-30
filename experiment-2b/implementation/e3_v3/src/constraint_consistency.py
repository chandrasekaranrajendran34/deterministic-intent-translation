
"""
Deterministic source-constraint consistency engine
for Experiment 2B / E3-v2.

Purpose:
Detect contradictions among numeric constraints that
have already been preserved from the source intent.

This module performs deterministic logical checks only.
It does not make standards-compliance claims.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from source_intent import (
    SourceIntent,
    SourceConstraint,
    NUMERIC_FIELDS,
)


@dataclass(frozen=True)
class ConsistencyError:

    code: str
    field: str
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConsistencyResult:

    valid: bool
    errors: List[ConsistencyError]

    def to_dict(self) -> Dict[str, Any]:

        return {
            "valid": self.valid,
            "errors": [
                e.to_dict()
                for e in self.errors
            ],
        }


def _numeric_value(
    constraint: SourceConstraint,
) -> Optional[float]:

    value = constraint.value

    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _validate_numeric_types(
    field_name: str,
    constraints: List[SourceConstraint],
) -> List[ConsistencyError]:

    errors = []

    for c in constraints:

        if _numeric_value(c) is None:

            errors.append(
                ConsistencyError(
                    code="NON_NUMERIC_CONSTRAINT",
                    field=field_name,
                    message=(
                        f"{field_name} has non-numeric "
                        f"value {c.value!r}"
                    ),
                )
            )

    return errors


def _check_field(
    field_name: str,
    constraints: List[SourceConstraint],
) -> List[ConsistencyError]:

    errors = []

    type_errors = _validate_numeric_types(
        field_name,
        constraints,
    )

    if type_errors:
        return type_errors

    exact_values = []

    lower_bounds = []
    upper_bounds = []

    for c in constraints:

        value = _numeric_value(c)

        if c.operator == "=":
            exact_values.append(value)

        elif c.operator == ">":
            lower_bounds.append(
                (value, False)
            )

        elif c.operator == ">=":
            lower_bounds.append(
                (value, True)
            )

        elif c.operator == "<":
            upper_bounds.append(
                (value, False)
            )

        elif c.operator == "<=":
            upper_bounds.append(
                (value, True)
            )

    # ------------------------------------------------
    # 1. Conflicting exact values
    # ------------------------------------------------

    unique_exact = set(exact_values)

    if len(unique_exact) > 1:

        errors.append(
            ConsistencyError(
                code="CONFLICTING_EXACT_VALUES",
                field=field_name,
                message=(
                    f"{field_name} has conflicting "
                    f"exact values: "
                    f"{sorted(unique_exact)}"
                ),
            )
        )

        return errors

    # ------------------------------------------------
    # 2. Strongest lower bound
    # ------------------------------------------------

    strongest_lower = None

    if lower_bounds:

        # Higher numeric value is stronger.
        # For same value, exclusive > is stronger
        # than inclusive >=.

        strongest_lower = max(
            lower_bounds,
            key=lambda x: (
                x[0],
                not x[1],
            ),
        )

    # ------------------------------------------------
    # 3. Strongest upper bound
    # ------------------------------------------------

    strongest_upper = None

    if upper_bounds:

        # Lower numeric value is stronger.
        # For same value, exclusive < is stronger
        # than inclusive <=.

        strongest_upper = min(
            upper_bounds,
            key=lambda x: (
                x[0],
                x[1],
            ),
        )

    # ------------------------------------------------
    # 4. Lower/upper compatibility
    # ------------------------------------------------

    if (
        strongest_lower is not None
        and strongest_upper is not None
    ):

        lower_value, lower_inclusive = (
            strongest_lower
        )

        upper_value, upper_inclusive = (
            strongest_upper
        )

        impossible = False

        if lower_value > upper_value:
            impossible = True

        elif lower_value == upper_value:

            # Same boundary is satisfiable only
            # when both sides include the value.
            if not (
                lower_inclusive
                and upper_inclusive
            ):
                impossible = True

        if impossible:

            lower_op = (
                ">="
                if lower_inclusive
                else ">"
            )

            upper_op = (
                "<="
                if upper_inclusive
                else "<"
            )

            errors.append(
                ConsistencyError(
                    code="INCOMPATIBLE_BOUNDS",
                    field=field_name,
                    message=(
                        f"{field_name} requires "
                        f"{lower_op} {lower_value:g} "
                        f"and "
                        f"{upper_op} {upper_value:g}"
                    ),
                )
            )

    # ------------------------------------------------
    # 5. Exact value against bounds
    # ------------------------------------------------

    if len(unique_exact) == 1:

        exact = next(
            iter(unique_exact)
        )

        if strongest_lower is not None:

            lower_value, lower_inclusive = (
                strongest_lower
            )

            violates_lower = (
                exact < lower_value
                if lower_inclusive
                else exact <= lower_value
            )

            if violates_lower:

                errors.append(
                    ConsistencyError(
                        code=(
                            "EXACT_VALUE_OUTSIDE_BOUNDS"
                        ),
                        field=field_name,
                        message=(
                            f"{field_name} exact value "
                            f"{exact:g} violates "
                            f"lower bound"
                        ),
                    )
                )

        if strongest_upper is not None:

            upper_value, upper_inclusive = (
                strongest_upper
            )

            violates_upper = (
                exact > upper_value
                if upper_inclusive
                else exact >= upper_value
            )

            if violates_upper:

                errors.append(
                    ConsistencyError(
                        code=(
                            "EXACT_VALUE_OUTSIDE_BOUNDS"
                        ),
                        field=field_name,
                        message=(
                            f"{field_name} exact value "
                            f"{exact:g} violates "
                            f"upper bound"
                        ),
                    )
                )

    return errors


def check_consistency(
    source_intent: SourceIntent,
) -> ConsistencyResult:

    errors = []

    for field_name in sorted(
        NUMERIC_FIELDS
    ):

        constraints = (
            source_intent.constraints_for(
                field_name
            )
        )

        if not constraints:
            continue

        errors.extend(
            _check_field(
                field_name,
                constraints,
            )
        )

    return ConsistencyResult(
        valid=(len(errors) == 0),
        errors=errors,
    )

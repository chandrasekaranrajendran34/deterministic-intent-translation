
"""
Deterministic source-boundary gate for E3-v2.

The gate operates on SourceIntent after source extraction.

It rejects:
1. control/bypass attempts captured from the source;
2. unresolved capability requirements;
3. requirements explicitly marked unsupported.

It does NOT attempt to infer universal semantic impossibility.
Unsupported means outside the frozen experimental capability profile.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

from source_intent import SourceIntent


@dataclass(frozen=True)
class SourceGateError:

    code: str
    message: str
    source_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SourceGateResult:

    valid: bool
    errors: List[SourceGateError]

    def to_dict(self) -> Dict[str, Any]:

        return {
            "valid": self.valid,
            "errors": [
                e.to_dict()
                for e in self.errors
            ],
        }


def check_source_gate(
    source_intent: SourceIntent,
) -> SourceGateResult:

    errors: List[SourceGateError] = []

    # ---------------------------------------------
    # 1. Control / bypass attempts
    # ---------------------------------------------

    for attempt in source_intent.control_attempts:

        errors.append(
            SourceGateError(
                code="SOURCE_CONTROL_ATTEMPT",
                message=(
                    "Source intent contains an attempt "
                    "to alter, bypass, disable, or override "
                    "the validation/control process."
                ),
                source_text=attempt,
            )
        )

    # ---------------------------------------------
    # 2. Capability-level requirements
    # ---------------------------------------------

    for requirement in source_intent.requirements:

        status = (
            requirement.status
            or "unresolved"
        ).lower()

        if status == "supported":
            continue

        if status == "unsupported":

            errors.append(
                SourceGateError(
                    code=(
                        "UNSUPPORTED_CAPABILITY_REQUIREMENT"
                    ),
                    message=(
                        "Source requirement is outside "
                        "the frozen experimental "
                        "capability profile."
                    ),
                    source_text=requirement.text,
                )
            )

        else:

            errors.append(
                SourceGateError(
                    code=(
                        "UNRESOLVED_SOURCE_REQUIREMENT"
                    ),
                    message=(
                        "Source requirement could not be "
                        "resolved to a supported capability "
                        "in the frozen experimental profile."
                    ),
                    source_text=requirement.text,
                )
            )

    return SourceGateResult(
        valid=(len(errors) == 0),
        errors=errors,
    )

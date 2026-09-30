"""
Source-intent representation for Experiment 2B / E3-v2.

This module represents requirements extracted from the original
natural-language intent before they are collapsed into the CIR.

Important:
- It does not claim standards compliance.
- It does not decide whether arbitrary concepts are universally valid.
- It preserves source constraints for later deterministic validation.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, List, Optional, Dict


NUMERIC_FIELDS = {
    "latency_ms",
    "bandwidth_mbps",
    "reliability",
    "device_count",
}

TEXT_FIELDS = {
    "coverage",
    "objective",
}

SUPPORTED_FIELDS = NUMERIC_FIELDS | TEXT_FIELDS

SUPPORTED_OPERATORS = {
    "=",
    "<",
    "<=",
    ">",
    ">=",
}


@dataclass(frozen=True)
class SourceConstraint:
    """
    One requirement explicitly represented from the source intent.
    """

    field: str
    operator: str
    value: Any
    unit: Optional[str] = None
    source_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SourceRequirement:
    """
    A non-numeric/capability-level requirement from the source intent.

    status is intentionally assigned later by the capability validator.
    """

    text: str
    normalized: Optional[str] = None
    status: str = "unresolved"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SourceIntent:
    """
    Structured representation of information preserved from the
    original natural-language request.
    """

    original_text: str

    service_type: Optional[str] = None

    constraints: List[SourceConstraint] = field(
        default_factory=list
    )

    requirements: List[SourceRequirement] = field(
        default_factory=list
    )

    control_attempts: List[str] = field(
        default_factory=list
    )

    extraction_notes: List[str] = field(
        default_factory=list
    )

    def add_constraint(
        self,
        field_name: str,
        operator: str,
        value: Any,
        unit: Optional[str] = None,
        source_text: Optional[str] = None,
    ) -> None:

        if field_name not in SUPPORTED_FIELDS:
            raise ValueError(
                f"Unknown source constraint field: {field_name}"
            )

        if operator not in SUPPORTED_OPERATORS:
            raise ValueError(
                f"Unsupported operator: {operator}"
            )

        self.constraints.append(
            SourceConstraint(
                field=field_name,
                operator=operator,
                value=value,
                unit=unit,
                source_text=source_text,
            )
        )

    def add_requirement(
        self,
        text: str,
        normalized: Optional[str] = None,
    ) -> None:

        self.requirements.append(
            SourceRequirement(
                text=text,
                normalized=normalized,
            )
        )

    def add_control_attempt(
        self,
        text: str,
    ) -> None:

        self.control_attempts.append(text)

    def constraints_for(
        self,
        field_name: str,
    ) -> List[SourceConstraint]:

        return [
            c
            for c in self.constraints
            if c.field == field_name
        ]

    def to_dict(self) -> Dict[str, Any]:

        return {
            "original_text":
                self.original_text,

            "service_type":
                self.service_type,

            "constraints": [
                c.to_dict()
                for c in self.constraints
            ],

            "requirements": [
                r.to_dict()
                for r in self.requirements
            ],

            "control_attempts":
                list(self.control_attempts),

            "extraction_notes":
                list(self.extraction_notes),
        }

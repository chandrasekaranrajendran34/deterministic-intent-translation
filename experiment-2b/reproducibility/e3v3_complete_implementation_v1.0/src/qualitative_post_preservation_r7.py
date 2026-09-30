"""
R7-aware post-CIR preservation.

This module does not modify:
- frozen R7 semantic analysis,
- validated R7 pre-LLM adapter,
- frozen preservation checker,
- CIR,
- service type,
- numeric constraints.

It reconstructs the same deterministic R7-repaired SourceIntent and then
executes the existing frozen preservation checker against the supplied CIR.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from source_analyzer import analyze_source
from capability_resolver import resolve_source_requirements
from source_gate import check_source_gate
from constraint_consistency import check_consistency
from source_intent import SourceRequirement
from preservation_check import check_preservation

from qualitative_requirement_resolver_r7 import (
    analyze_qualitative_requirements,
)


@dataclass
class R7PostPreservationResult:
    accepted: bool
    rejection_stage: Optional[str]
    error_codes: List[str]

    source_intent: Dict[str, Any]
    source_gate: Dict[str, Any]
    consistency: Dict[str, Any]
    preservation: Optional[Dict[str, Any]]

    r7_supported_qualitative_matches: List[Dict[str, Any]]
    r7_unsupported_qualitative_matches: List[Dict[str, Any]]
    r7_normalized_capabilities: List[str]

    r7_source_repair_applied: bool
    r7_repaired_source_requirements: List[Dict[str, Any]]

    def to_dict(self):
        return asdict(self)


def _dedupe(values):
    result = []
    seen = set()

    for value in values:
        if value is None:
            continue

        value = str(value)

        if value not in seen:
            seen.add(value)
            result.append(value)

    return result


def _capabilities(matches):
    values = []

    for match in matches:
        if not isinstance(match, dict):
            raise TypeError(
                "R7 supported match must be a dictionary."
            )

        value = match.get("normalized")

        if value is not None:
            values.append(value)

    return _dedupe(values)


def _build_r7_source(intent):
    """
    Reconstruct the same source-side semantics used by the validated
    pre-LLM R7 adapter.
    """

    source = analyze_source(intent)

    source = resolve_source_requirements(
        source
    )

    r7 = analyze_qualitative_requirements(
        intent
    )

    if not isinstance(r7, dict):
        raise TypeError(
            "Unexpected frozen R7 result representation."
        )

    supported = list(
        r7.get(
            "supported_qualitative_matches",
            [],
        )
        or []
    )

    unsupported = list(
        r7.get(
            "unsupported_qualitative_matches",
            [],
        )
        or []
    )

    qualitative_valid = bool(
        r7.get(
            "qualitative_valid",
            False,
        )
    )

    normalized = _capabilities(
        supported
    )

    # Unsupported R7 semantics are not repaired.
    if unsupported or not qualitative_valid:
        return (
            source,
            supported,
            unsupported,
            normalized,
            [],
        )

    repaired = []
    evidence = []

    for requirement in source.requirements:

        status = (
            requirement.status
            or "unresolved"
        ).lower()

        if status != "unresolved":
            repaired.append(requirement)
            continue

        local = analyze_qualitative_requirements(
            requirement.text
        )

        if not isinstance(local, dict):
            raise TypeError(
                "Unexpected local R7 representation."
            )

        local_unsupported = list(
            local.get(
                "unsupported_qualitative_matches",
                [],
            )
            or []
        )

        if local_unsupported:
            repaired.append(requirement)
            continue

        local_supported = list(
            local.get(
                "supported_qualitative_matches",
                [],
            )
            or []
        )

        candidates = [
            capability
            for capability in _capabilities(
                local_supported
            )
            if capability in normalized
        ]

        if len(candidates) != 1:
            repaired.append(requirement)
            continue

        capability = candidates[0]

        repaired.append(
            SourceRequirement(
                text=requirement.text,
                normalized=capability,
                status="supported",
            )
        )

        evidence.append({
            "source_text": requirement.text,
            "normalized": capability,
            "old_status": requirement.status,
            "new_status": "supported",
        })

    source.requirements = repaired

    return (
        source,
        supported,
        unsupported,
        normalized,
        evidence,
    )


def evaluate_r7_post_preservation(intent, cir):
    """
    R7-aware post-CIR source/preservation evaluation.
    """

    (
        source,
        supported,
        unsupported,
        normalized,
        repaired,
    ) = _build_r7_source(intent)

    # --------------------------------------------------------------
    # R7 unsupported semantics still fail closed.
    # --------------------------------------------------------------

    if unsupported:

        return R7PostPreservationResult(
            accepted=False,
            rejection_stage="r7_qualitative_source_gate",
            error_codes=[
                "UNSUPPORTED_QUALITATIVE_REQUIREMENT"
            ],

            source_intent=source.to_dict(),

            source_gate={
                "valid": False,
                "errors": [],
                "skipped": True,
            },

            consistency={
                "valid": None,
                "errors": [],
                "skipped": True,
            },

            preservation=None,

            r7_supported_qualitative_matches=
                supported,

            r7_unsupported_qualitative_matches=
                unsupported,

            r7_normalized_capabilities=
                normalized,

            r7_source_repair_applied=
                bool(repaired),

            r7_repaired_source_requirements=
                repaired,
        )

    # --------------------------------------------------------------
    # Existing source gate.
    # --------------------------------------------------------------

    gate = check_source_gate(
        source
    )

    if not gate.valid:

        return R7PostPreservationResult(
            accepted=False,
            rejection_stage="source_gate",
            error_codes=[
                e.code
                for e in gate.errors
            ],

            source_intent=source.to_dict(),
            source_gate=gate.to_dict(),

            consistency={
                "valid": None,
                "errors": [],
                "skipped": True,
            },

            preservation=None,

            r7_supported_qualitative_matches=
                supported,

            r7_unsupported_qualitative_matches=
                unsupported,

            r7_normalized_capabilities=
                normalized,

            r7_source_repair_applied=
                bool(repaired),

            r7_repaired_source_requirements=
                repaired,
        )

    # --------------------------------------------------------------
    # Existing consistency checker.
    # --------------------------------------------------------------

    consistency = check_consistency(
        source
    )

    if not consistency.valid:

        return R7PostPreservationResult(
            accepted=False,
            rejection_stage="constraint_consistency",
            error_codes=[
                e.code
                for e in consistency.errors
            ],

            source_intent=source.to_dict(),
            source_gate=gate.to_dict(),
            consistency=consistency.to_dict(),
            preservation=None,

            r7_supported_qualitative_matches=
                supported,

            r7_unsupported_qualitative_matches=
                unsupported,

            r7_normalized_capabilities=
                normalized,

            r7_source_repair_applied=
                bool(repaired),

            r7_repaired_source_requirements=
                repaired,
        )

    # --------------------------------------------------------------
    # Frozen preservation checker.
    # --------------------------------------------------------------

    preservation = check_preservation(
        source,
        cir,
    )

    if not preservation.valid:

        return R7PostPreservationResult(
            accepted=False,
            rejection_stage="preservation",
            error_codes=[
                e.code
                for e in preservation.errors
            ],

            source_intent=source.to_dict(),
            source_gate=gate.to_dict(),
            consistency=consistency.to_dict(),
            preservation=preservation.to_dict(),

            r7_supported_qualitative_matches=
                supported,

            r7_unsupported_qualitative_matches=
                unsupported,

            r7_normalized_capabilities=
                normalized,

            r7_source_repair_applied=
                bool(repaired),

            r7_repaired_source_requirements=
                repaired,
        )

    return R7PostPreservationResult(
        accepted=True,
        rejection_stage=None,
        error_codes=[],

        source_intent=source.to_dict(),
        source_gate=gate.to_dict(),
        consistency=consistency.to_dict(),
        preservation=preservation.to_dict(),

        r7_supported_qualitative_matches=
            supported,

        r7_unsupported_qualitative_matches=
            unsupported,

        r7_normalized_capabilities=
            normalized,

        r7_source_repair_applied=
            bool(repaired),

        r7_repaired_source_requirements=
            repaired,
    )

"""
R7 source-boundary integration.

Development-only integration layer.

Responsibilities:
1. Execute the frozen deterministic source analyzer and capability resolver.
2. Execute the frozen R7 qualitative analyzer.
3. Replace only matching unresolved SourceRequirement objects when R7
   supplies a supported qualitative capability.
4. Reject frozen R7 unsupported qualitative semantics before LLM/CIR.
5. Re-run the existing source gate and consistency checker on the repaired
   SourceIntent.
6. Never invent numeric values, thresholds, service types, or constraints.

This module does not modify R7 semantic signatures.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from source_analyzer import analyze_source
from capability_resolver import resolve_source_requirements
from source_gate import check_source_gate
from constraint_consistency import check_consistency
from source_intent import SourceRequirement

from qualitative_requirement_resolver_r7 import (
    analyze_qualitative_requirements,
)


@dataclass
class R7SourceIntegrationResult:
    accepted: bool
    rejection_stage: Optional[str]
    error_codes: List[str]

    source_intent: Dict[str, Any]
    source_gate: Dict[str, Any]
    consistency: Dict[str, Any]

    r7_supported_qualitative_matches: List[str]
    r7_unsupported_qualitative_matches: List[str]
    r7_normalized_capabilities: List[str]

    r7_qualitative_valid: bool
    r7_source_repair_applied: bool
    r7_repaired_source_requirements: List[Dict[str, Any]]
    r7_removed_source_errors: List[Dict[str, Any]]
    r7_rejection_stage: Optional[str]

    def to_dict(self):
        return asdict(self)


def _norm_text(value: str) -> str:
    """
    Frozen integration-level text identity:
    lowercase, hyphen -> space, collapse whitespace.
    """

    return " ".join(
        str(value)
        .lower()
        .replace("-", " ")
        .split()
    )


def _dedupe(values):
    seen = set()
    result = []

    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)

    return result


def _get_r7_field(result, name, default=None):

    if isinstance(result, dict):
        return result.get(name, default)

    return getattr(result, name, default)


def evaluate_r7_source_boundary(intent: str) -> R7SourceIntegrationResult:
    """
    Deterministic pre-LLM source evaluation for R7.

    No CIR and no LLM are used here.
    """

    # ------------------------------------------------------------------
    # 1. Existing frozen source analysis + capability resolution
    # ------------------------------------------------------------------

    source = analyze_source(intent)

    source = resolve_source_requirements(
        source
    )

    # Preserve the existing gate result for audit/reconciliation evidence.
    original_gate = check_source_gate(
        source
    )

    # ------------------------------------------------------------------
    # 2. Frozen R7 qualitative analysis
    # ------------------------------------------------------------------

    r7 = analyze_qualitative_requirements(
        intent
    )

    supported_matches = list(
        _get_r7_field(
            r7,
            "supported_qualitative_matches",
            [],
        )
        or []
    )

    unsupported_matches = list(
        _get_r7_field(
            r7,
            "unsupported_qualitative_matches",
            [],
        )
        or []
    )

    r7_valid = bool(
        _get_r7_field(
            r7,
            "valid",
            len(unsupported_matches) == 0,
        )
    )

    # The frozen R7 module returns capability names in the supported
    # qualitative match list. Deduplicate for reconciliation only.
    normalized_capabilities = _dedupe(
        supported_matches
    )

    # ------------------------------------------------------------------
    # 3. Unsupported qualitative semantics fail closed immediately
    # ------------------------------------------------------------------

    if unsupported_matches or not r7_valid:

        return R7SourceIntegrationResult(
            accepted=False,
            rejection_stage="r7_qualitative_source_gate",
            error_codes=[
                "UNSUPPORTED_QUALITATIVE_REQUIREMENT"
            ],

            source_intent=source.to_dict(),
            source_gate=original_gate.to_dict(),

            consistency={
                "valid": None,
                "errors": [],
                "skipped": True,
            },

            r7_supported_qualitative_matches=
                supported_matches,

            r7_unsupported_qualitative_matches=
                unsupported_matches,

            r7_normalized_capabilities=
                normalized_capabilities,

            r7_qualitative_valid=False,

            r7_source_repair_applied=False,

            r7_repaired_source_requirements=[],

            r7_removed_source_errors=[],

            r7_rejection_stage=
                "r7_qualitative_source_gate",
        )

    # ------------------------------------------------------------------
    # 4. Narrow repair of matching unresolved SourceRequirement objects
    # ------------------------------------------------------------------

    repaired_requirements = []
    repaired_evidence = []

    # Track which R7 capabilities are still available for reconciliation.
    #
    # Matching is source-grounded:
    # R7 capability is used only when an unresolved source requirement's
    # own text independently yields that same supported capability.
    for requirement in source.requirements:

        status = (
            requirement.status
            or "unresolved"
        ).lower()

        # Existing supported/unsupported classifications remain authoritative.
        if status != "unresolved":

            repaired_requirements.append(
                requirement
            )
            continue

        local_r7 = analyze_qualitative_requirements(
            requirement.text
        )

        local_unsupported = list(
            _get_r7_field(
                local_r7,
                "unsupported_qualitative_matches",
                [],
            )
            or []
        )

        local_supported = _dedupe(
            list(
                _get_r7_field(
                    local_r7,
                    "supported_qualitative_matches",
                    [],
                )
                or []
            )
        )

        # Never repair a requirement carrying an unsupported local signature.
        if local_unsupported:

            repaired_requirements.append(
                requirement
            )
            continue

        candidates = [
            capability
            for capability in local_supported
            if capability in normalized_capabilities
        ]

        # Fail closed on ambiguous local normalization.
        if len(candidates) != 1:

            repaired_requirements.append(
                requirement
            )
            continue

        capability = candidates[0]

        replacement = SourceRequirement(
            text=requirement.text,
            normalized=capability,
            status="supported",
        )

        repaired_requirements.append(
            replacement
        )

        repaired_evidence.append({
            "source_text": requirement.text,
            "normalized": capability,
            "old_status": requirement.status,
            "new_status": "supported",
        })

    source.requirements = repaired_requirements

    # ------------------------------------------------------------------
    # 5. Re-run existing source gate on repaired SourceIntent
    # ------------------------------------------------------------------

    gate = check_source_gate(
        source
    )

    original_errors = [
        e.to_dict()
        for e in original_gate.errors
    ]

    final_errors = [
        e.to_dict()
        for e in gate.errors
    ]

    final_error_identity = {
        (
            e.get("code"),
            _norm_text(
                e.get("source_text", "")
            ),
        )
        for e in final_errors
    }

    removed_errors = [
        e
        for e in original_errors
        if (
            e.get("code"),
            _norm_text(
                e.get("source_text", "")
            ),
        )
        not in final_error_identity
    ]

    # Strict integration-design restriction:
    # only matching unresolved-source errors may disappear.
    for error in removed_errors:

        if error.get("code") != "UNRESOLVED_SOURCE_REQUIREMENT":
            raise RuntimeError(
                "R7 integration attempted to remove a non-permitted "
                f"source error: {error}"
            )

        repaired_texts = {
            _norm_text(
                item["source_text"]
            )
            for item in repaired_evidence
        }

        if _norm_text(
            error.get(
                "source_text",
                ""
            )
        ) not in repaired_texts:

            raise RuntimeError(
                "R7 integration removed an unresolved source error "
                "without a matching repaired source requirement."
            )

    # ------------------------------------------------------------------
    # 6. Preserve any remaining source-gate rejection
    # ------------------------------------------------------------------

    if not gate.valid:

        return R7SourceIntegrationResult(
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

            r7_supported_qualitative_matches=
                supported_matches,

            r7_unsupported_qualitative_matches=
                unsupported_matches,

            r7_normalized_capabilities=
                normalized_capabilities,

            r7_qualitative_valid=True,

            r7_source_repair_applied=
                bool(repaired_evidence),

            r7_repaired_source_requirements=
                repaired_evidence,

            r7_removed_source_errors=
                removed_errors,

            r7_rejection_stage=None,
        )

    # ------------------------------------------------------------------
    # 7. Existing consistency checker runs normally
    # ------------------------------------------------------------------

    consistency = check_consistency(
        source
    )

    if not consistency.valid:

        return R7SourceIntegrationResult(
            accepted=False,
            rejection_stage="constraint_consistency",

            error_codes=[
                e.code
                for e in consistency.errors
            ],

            source_intent=source.to_dict(),
            source_gate=gate.to_dict(),
            consistency=consistency.to_dict(),

            r7_supported_qualitative_matches=
                supported_matches,

            r7_unsupported_qualitative_matches=
                unsupported_matches,

            r7_normalized_capabilities=
                normalized_capabilities,

            r7_qualitative_valid=True,

            r7_source_repair_applied=
                bool(repaired_evidence),

            r7_repaired_source_requirements=
                repaired_evidence,

            r7_removed_source_errors=
                removed_errors,

            r7_rejection_stage=None,
        )

    # ------------------------------------------------------------------
    # 8. Accepted pre-LLM source state
    # ------------------------------------------------------------------

    return R7SourceIntegrationResult(
        accepted=True,
        rejection_stage=None,
        error_codes=[],

        source_intent=source.to_dict(),
        source_gate=gate.to_dict(),
        consistency=consistency.to_dict(),

        r7_supported_qualitative_matches=
            supported_matches,

        r7_unsupported_qualitative_matches=
            unsupported_matches,

        r7_normalized_capabilities=
            normalized_capabilities,

        r7_qualitative_valid=True,

        r7_source_repair_applied=
            bool(repaired_evidence),

        r7_repaired_source_requirements=
            repaired_evidence,

        r7_removed_source_errors=
            removed_errors,

        r7_rejection_stage=None,
    )

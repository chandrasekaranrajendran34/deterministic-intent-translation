"""
R7 source-boundary integration.

Schema-repaired adapter following Step 26I-R1.

Important:
- The frozen R7 analyzer is not modified.
- R7 returns structured match dictionaries.
- Supported capability identity is match["normalized"].
- Validity field is "qualitative_valid".
- Full R7 match evidence is retained.
- Only matching unresolved SourceRequirement objects may be replaced.
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

    r7_supported_qualitative_matches: List[Dict[str, Any]]
    r7_unsupported_qualitative_matches: List[Dict[str, Any]]
    r7_normalized_capabilities: List[str]

    r7_qualitative_valid: bool
    r7_source_repair_applied: bool
    r7_repaired_source_requirements: List[Dict[str, Any]]
    r7_removed_source_errors: List[Dict[str, Any]]
    r7_rejection_stage: Optional[str]

    def to_dict(self):
        return asdict(self)


def _norm_text(value):
    return " ".join(
        str(value)
        .lower()
        .replace("-", " ")
        .split()
    )


def _dedupe_strings(values):
    seen = set()
    result = []

    for value in values:
        if value is None:
            continue

        value = str(value)

        if value in seen:
            continue

        seen.add(value)
        result.append(value)

    return result


def _capabilities(matches):
    """
    Extract normalized capability names from frozen R7
    structured supported-match dictionaries.
    """

    result = []

    for item in matches:

        if not isinstance(item, dict):
            raise TypeError(
                "Frozen R7 supported match must be a dict; "
                f"got {type(item)!r}"
            )

        normalized = item.get(
            "normalized"
        )

        if normalized is not None:
            result.append(
                normalized
            )

    return _dedupe_strings(
        result
    )


def evaluate_r7_source_boundary(intent):
    """
    Deterministic R7 pre-LLM source-boundary evaluation.

    No LLM and no CIR generation occur here.
    """

    # ------------------------------------------------------------------
    # 1. Existing deterministic source analysis
    # ------------------------------------------------------------------

    source = analyze_source(
        intent
    )

    source = resolve_source_requirements(
        source
    )

    original_gate = check_source_gate(
        source
    )

    # ------------------------------------------------------------------
    # 2. Frozen R7 qualitative evidence
    # ------------------------------------------------------------------

    r7 = analyze_qualitative_requirements(
        intent
    )

    if not isinstance(r7, dict):
        raise TypeError(
            "Frozen R7 analyzer returned unexpected type: "
            f"{type(r7)!r}"
        )

    supported_matches = list(
        r7.get(
            "supported_qualitative_matches",
            [],
        )
        or []
    )

    unsupported_matches = list(
        r7.get(
            "unsupported_qualitative_matches",
            [],
        )
        or []
    )

    r7_valid = bool(
        r7.get(
            "qualitative_valid",
            False,
        )
    )

    normalized_capabilities = _capabilities(
        supported_matches
    )

    # ------------------------------------------------------------------
    # 3. Unsupported qualitative semantics fail closed
    # ------------------------------------------------------------------

    if unsupported_matches or not r7_valid:

        return R7SourceIntegrationResult(
            accepted=False,

            rejection_stage=
                "r7_qualitative_source_gate",

            error_codes=[
                "UNSUPPORTED_QUALITATIVE_REQUIREMENT"
            ],

            source_intent=
                source.to_dict(),

            source_gate=
                original_gate.to_dict(),

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

            r7_qualitative_valid=
                r7_valid,

            r7_source_repair_applied=
                False,

            r7_repaired_source_requirements=
                [],

            r7_removed_source_errors=
                [],

            r7_rejection_stage=
                "r7_qualitative_source_gate",
        )

    # ------------------------------------------------------------------
    # 4. Narrow unresolved-requirement repair
    # ------------------------------------------------------------------

    repaired_requirements = []
    repaired_evidence = []

    for requirement in source.requirements:

        status = (
            requirement.status
            or "unresolved"
        ).lower()

        # Existing classification remains authoritative.
        if status != "unresolved":

            repaired_requirements.append(
                requirement
            )

            continue

        # Analyze only the unresolved requirement's own source text.
        local_r7 = (
            analyze_qualitative_requirements(
                requirement.text
            )
        )

        if not isinstance(
            local_r7,
            dict,
        ):
            raise TypeError(
                "Frozen R7 local analyzer returned "
                "unexpected representation."
            )

        local_unsupported = list(
            local_r7.get(
                "unsupported_qualitative_matches",
                [],
            )
            or []
        )

        local_supported = list(
            local_r7.get(
                "supported_qualitative_matches",
                [],
            )
            or []
        )

        # Never repair locally unsupported evidence.
        if local_unsupported:

            repaired_requirements.append(
                requirement
            )

            continue

        local_capabilities = _capabilities(
            local_supported
        )

        candidates = [
            capability
            for capability in local_capabilities
            if capability
            in normalized_capabilities
        ]

        # Exactly one source-grounded capability is required.
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
            "source_text":
                requirement.text,

            "normalized":
                capability,

            "old_status":
                requirement.status,

            "new_status":
                "supported",
        })

    source.requirements = (
        repaired_requirements
    )

    # ------------------------------------------------------------------
    # 5. Re-run existing source gate
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
            item.get("code"),
            _norm_text(
                item.get(
                    "source_text",
                    "",
                )
            ),
        )
        for item in final_errors
    }

    removed_errors = [
        item
        for item in original_errors
        if (
            item.get("code"),
            _norm_text(
                item.get(
                    "source_text",
                    "",
                )
            ),
        )
        not in final_error_identity
    ]

    # ------------------------------------------------------------------
    # 6. Enforce narrow repair contract
    # ------------------------------------------------------------------

    repaired_texts = {
        _norm_text(
            item["source_text"]
        )
        for item in repaired_evidence
    }

    for error in removed_errors:

        if (
            error.get("code")
            != "UNRESOLVED_SOURCE_REQUIREMENT"
        ):
            raise RuntimeError(
                "R7 removed a non-permitted "
                f"source error: {error}"
            )

        if _norm_text(
            error.get(
                "source_text",
                "",
            )
        ) not in repaired_texts:

            raise RuntimeError(
                "R7 removed an unresolved source "
                "error without a matching repair."
            )

    # ------------------------------------------------------------------
    # 7. Preserve remaining source-gate rejection
    # ------------------------------------------------------------------

    if not gate.valid:

        return R7SourceIntegrationResult(
            accepted=False,
            rejection_stage="source_gate",

            error_codes=[
                e.code
                for e in gate.errors
            ],

            source_intent=
                source.to_dict(),

            source_gate=
                gate.to_dict(),

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

            r7_qualitative_valid=
                True,

            r7_source_repair_applied=
                bool(
                    repaired_evidence
                ),

            r7_repaired_source_requirements=
                repaired_evidence,

            r7_removed_source_errors=
                removed_errors,

            r7_rejection_stage=
                None,
        )

    # ------------------------------------------------------------------
    # 8. Existing consistency engine
    # ------------------------------------------------------------------

    consistency = check_consistency(
        source
    )

    if not consistency.valid:

        return R7SourceIntegrationResult(
            accepted=False,

            rejection_stage=
                "constraint_consistency",

            error_codes=[
                e.code
                for e in consistency.errors
            ],

            source_intent=
                source.to_dict(),

            source_gate=
                gate.to_dict(),

            consistency=
                consistency.to_dict(),

            r7_supported_qualitative_matches=
                supported_matches,

            r7_unsupported_qualitative_matches=
                unsupported_matches,

            r7_normalized_capabilities=
                normalized_capabilities,

            r7_qualitative_valid=
                True,

            r7_source_repair_applied=
                bool(
                    repaired_evidence
                ),

            r7_repaired_source_requirements=
                repaired_evidence,

            r7_removed_source_errors=
                removed_errors,

            r7_rejection_stage=
                None,
        )

    # ------------------------------------------------------------------
    # 9. Accepted source state
    # ------------------------------------------------------------------

    return R7SourceIntegrationResult(
        accepted=True,
        rejection_stage=None,
        error_codes=[],

        source_intent=
            source.to_dict(),

        source_gate=
            gate.to_dict(),

        consistency=
            consistency.to_dict(),

        r7_supported_qualitative_matches=
            supported_matches,

        r7_unsupported_qualitative_matches=
            unsupported_matches,

        r7_normalized_capabilities=
            normalized_capabilities,

        r7_qualitative_valid=
            True,

        r7_source_repair_applied=
            bool(
                repaired_evidence
            ),

        r7_repaired_source_requirements=
            repaired_evidence,

        r7_removed_source_errors=
            removed_errors,

        r7_rejection_stage=
            None,
    )

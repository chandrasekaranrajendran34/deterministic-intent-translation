
"""
Integrated deterministic guard for Experiment 2B / E3-v2.

Stages:
1. Analyze original natural-language source.
2. Apply source-boundary gate.
3. Check source-constraint consistency.
4. If a CIR is supplied, verify source-to-CIR preservation.

This module does not call an LLM and does not claim standards
compliance. LLM generation and the existing CIR validator/mapping
pipeline are integrated separately.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from source_analyzer import analyze_source
from capability_resolver import resolve_source_requirements
from source_gate import check_source_gate
from constraint_consistency import check_consistency
from preservation_check import check_preservation


@dataclass
class GuardResult:

    accepted: bool
    rejection_stage: Optional[str]
    error_codes: List[str]
    source_intent: Dict[str, Any]
    source_gate: Dict[str, Any]
    consistency: Dict[str, Any]
    preservation: Optional[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def evaluate_guard(
    intent: str,
    cir: Optional[Any] = None,
) -> GuardResult:

    # ------------------------------------------
    # Stage 1 — deterministic source analysis
    # ------------------------------------------

    source = analyze_source(intent)

    # Resolve captured semantic requirements
    # against the frozen experimental
    # capability profile.
    source = resolve_source_requirements(
        source
    )

    # ------------------------------------------
    # Stage 2 — source-boundary gate
    # ------------------------------------------

    gate = check_source_gate(source)

    if not gate.valid:

        return GuardResult(
            accepted=False,
            rejection_stage="source_gate",
            error_codes=[
                e.code for e in gate.errors
            ],
            source_intent=source.to_dict(),
            source_gate=gate.to_dict(),
            consistency={
                "valid": None,
                "errors": [],
                "skipped": True,
            },
            preservation=None,
        )

    # ------------------------------------------
    # Stage 3 — constraint consistency
    # ------------------------------------------

    consistency = check_consistency(source)

    if not consistency.valid:

        return GuardResult(
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
        )

    # ------------------------------------------
    # Stage 4 — CIR preservation
    #
    # cir=None means only the pre-LLM guard
    # has been requested.
    # ------------------------------------------

    if cir is None:

        return GuardResult(
            accepted=True,
            rejection_stage=None,
            error_codes=[],
            source_intent=source.to_dict(),
            source_gate=gate.to_dict(),
            consistency=consistency.to_dict(),
            preservation=None,
        )

    preservation = check_preservation(
        source,
        cir,
    )

    if not preservation.valid:

        return GuardResult(
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
        )

    return GuardResult(
        accepted=True,
        rejection_stage=None,
        error_codes=[],
        source_intent=source.to_dict(),
        source_gate=gate.to_dict(),
        consistency=consistency.to_dict(),
        preservation=preservation.to_dict(),
    )

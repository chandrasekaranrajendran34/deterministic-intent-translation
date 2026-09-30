"""
R6 deterministic service_type CIR integration.

Development implementation.

Contract:
    R5 -> R6 -> post-guard

R6 resolves service type from original source text.

It may repair only cir["service_type"].

A supported canonical CIR/R6 disagreement is explicit conflict
and is never silently overwritten.
"""

from copy import deepcopy

from service_type_resolver_r6_cue_equivalent import (
    resolve_service_type,
    resolution_evidence,
)


SUPPORTED_SERVICE_TYPES = {
    "eMBB",
    "URLLC",
    "mMTC",
}


def _canonical_service(value):
    """
    Return a supported canonical service type or None.

    This helper intentionally does not infer semantic aliases.
    Semantic source resolution belongs exclusively to the
    frozen R6 resolver.
    """

    if not isinstance(value, str):
        return None

    value = value.strip()

    if value in SUPPORTED_SERVICE_TYPES:
        return value

    return None


def integrate_service_type_r6(intent, cir):
    """
    Apply frozen R6 service resolution to a CIR.

    Returns a structured dictionary containing the updated CIR
    and complete integration evidence.
    """

    if not isinstance(cir, dict):
        raise TypeError("cir must be a dictionary")

    before = deepcopy(cir)
    after = deepcopy(cir)

    resolved = resolve_service_type(intent)
    evidence = resolution_evidence(intent)

    original_value = before.get("service_type")
    canonical_original = _canonical_service(original_value)

    changed = False
    conflict = False
    action = "unchanged"

    # ------------------------------------------------------------
    # R6 unresolved:
    # source evidence is insufficient, so do nothing.
    # ------------------------------------------------------------

    if resolved is None:

        action = "unresolved_no_change"

    # ------------------------------------------------------------
    # Deterministic source service resolved.
    # ------------------------------------------------------------

    else:

        # Missing / null / empty / unsupported/noncanonical CIR
        # service value may be source-grounded repaired.
        if canonical_original is None:

            after["service_type"] = resolved

            changed = (
                original_value != resolved
            )

            action = "source_grounded_fill"

        # Existing CIR agrees with source evidence.
        elif canonical_original == resolved:

            action = "already_consistent"

        # Existing supported canonical service disagrees.
        # Never overwrite.
        else:

            conflict = True
            action = "supported_service_conflict"


    # ------------------------------------------------------------
    # Prove that R6 touched no other CIR field.
    # ------------------------------------------------------------

    before_without_service = deepcopy(before)
    after_without_service = deepcopy(after)

    before_without_service.pop(
        "service_type",
        None
    )

    after_without_service.pop(
        "service_type",
        None
    )

    non_service_fields_unchanged = (
        before_without_service
        == after_without_service
    )

    if not non_service_fields_unchanged:
        raise AssertionError(
            "R6 modified a non-service_type CIR field"
        )


    return {
        "cir": after,
        "resolved_service_type": resolved,
        "resolution_evidence": evidence,
        "original_service_type": original_value,
        "canonical_original_service_type":
            canonical_original,
        "service_type_changed": changed,
        "service_type_conflict": conflict,
        "action": action,
        "non_service_fields_unchanged":
            non_service_fields_unchanged,
    }


"""
R7 deterministic qualitative requirement resolver.

Closed-world development component.

This module:
- recognizes only explicitly configured supported qualitative phrases;
- recognizes only explicitly configured unsupported qualitative signatures;
- does not invent numeric values;
- does not invent thresholds;
- does not modify service type;
- does not perform general physical-law reasoning.
"""

import re
from copy import deepcopy


SUPPORTED_QUALITATIVE = (
    ("high throughput", "bandwidth_mbps"),
    ("bandwidth intensive", "bandwidth_mbps"),

    ("rapid response", "latency_ms"),
    ("minimal communication delay", "latency_ms"),
    ("latency sensitive", "latency_ms"),

    ("reliable communication", "reliability"),

    ("dense device connectivity", "device_count"),
    ("large device populations", "device_count"),

    ("broad coverage", "coverage"),
)


UNSUPPORTED_QUALITATIVE = (
    (
        "teleportation",
        "teleportation",
        "unsupported capability",
    ),

    (
        "unlimited physical range",
        "unbounded_physical_range",
        "unbounded physical capability",
    ),

    (
        "zero energy operation forever",
        "perpetual_zero_energy_operation",
        "unsupported perpetual zero-energy requirement",
    ),

    (
        "infinite bandwidth",
        "unbounded_bandwidth",
        "unbounded resource requirement",
    ),

    (
        "negative communication latency",
        "negative_latency",
        "invalid qualitative latency requirement",
    ),

    (
        "unlimited number of devices",
        "unbounded_device_count",
        "unbounded resource requirement",
    ),

    (
        "instantaneous data transfer",
        "instantaneous_data_transfer",
        "unsupported zero-time transfer requirement",
    ),
)


ERROR_CODE = "UNSUPPORTED_QUALITATIVE_REQUIREMENT"


def _normalize(text):
    """
    Frozen R7 normalization:
    lowercase, hyphen->space, collapse whitespace.
    """

    if text is None:
        return ""

    value = str(text).lower()
    value = value.replace("-", " ")
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def _phrase_pattern(phrase):
    """
    Phrase boundary matcher.

    Prevents accidental substring matching inside larger
    alphanumeric tokens while still permitting punctuation
    around a phrase.
    """

    tokens = [
        re.escape(token)
        for token in _normalize(phrase).split()
    ]

    body = r"\s+".join(tokens)

    return re.compile(
        r"(?<![a-z0-9])"
        + body
        + r"(?![a-z0-9])"
    )


def _contains_phrase(normalized_text, phrase):
    return bool(
        _phrase_pattern(phrase).search(
            normalized_text
        )
    )


def _locally_negated(normalized_text, phrase):
    """
    Minimal deterministic negation safeguard.

    R7 must not convert/reject an explicitly negated
    signature as though it were requested.

    This is intentionally narrow and closed-world.
    """

    phrase_norm = _normalize(phrase)

    patterns = (
        "no " + phrase_norm,
        "not " + phrase_norm,
        "without " + phrase_norm,
    )

    return any(
        _contains_phrase(
            normalized_text,
            pattern
        )
        for pattern in patterns
    )


def analyze_qualitative_requirements(intent):
    """
    Analyze qualitative source semantics.

    Returns evidence only.
    Does not mutate CIR or service type.
    """

    original = "" if intent is None else str(intent)
    normalized = _normalize(original)

    supported = []
    unsupported = []

    # ------------------------------------------------------------
    # Supported qualitative requirements
    # ------------------------------------------------------------

    for phrase, capability in SUPPORTED_QUALITATIVE:

        if not _contains_phrase(
            normalized,
            phrase
        ):
            continue

        if _locally_negated(
            normalized,
            phrase
        ):
            continue

        supported.append({
            "source_text": phrase,
            "normalized": capability,
            "status": "supported",
        })


    # ------------------------------------------------------------
    # Unsupported qualitative signatures
    # ------------------------------------------------------------

    for phrase, semantic_class, reason in UNSUPPORTED_QUALITATIVE:

        if not _contains_phrase(
            normalized,
            phrase
        ):
            continue

        if _locally_negated(
            normalized,
            phrase
        ):
            continue

        unsupported.append({
            "source_text": phrase,
            "class": semantic_class,
            "reason": reason,
            "status": "unsupported",
        })


    # Deterministic de-duplication.
    supported_unique = []
    seen_supported = set()

    for item in supported:

        key = (
            item["source_text"],
            item["normalized"],
        )

        if key in seen_supported:
            continue

        seen_supported.add(key)
        supported_unique.append(
            deepcopy(item)
        )


    unsupported_unique = []
    seen_unsupported = set()

    for item in unsupported:

        key = (
            item["source_text"],
            item["class"],
        )

        if key in seen_unsupported:
            continue

        seen_unsupported.add(key)
        unsupported_unique.append(
            deepcopy(item)
        )


    valid = (
        len(unsupported_unique) == 0
    )

    errors = []

    for item in unsupported_unique:

        errors.append({
            "code": ERROR_CODE,
            "message":
                "Source qualitative requirement is outside "
                "the frozen experimental capability profile.",
            "source_text":
                item["source_text"],
            "class":
                item["class"],
            "reason":
                item["reason"],
        })


    return {
        "supported_qualitative_matches":
            supported_unique,

        "unsupported_qualitative_matches":
            unsupported_unique,

        "normalized_requirements":
            deepcopy(supported_unique),

        "qualitative_valid":
            valid,

        "error_codes":
            errors,
    }

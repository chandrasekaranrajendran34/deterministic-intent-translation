
"""
R6 deterministic service-type resolver.

Closed-world supported service classes:
    eMBB
    URLLC
    mMTC

This module does not use an LLM, embeddings, fuzzy similarity,
or statistical classification.

It recognizes deterministic semantic signatures only.
"""

import re


# ----------------------------------------------------------------
# Normalization
# ----------------------------------------------------------------

def _normalize(text):
    text = str(text).lower()

    # Normalize common Unicode punctuation.
    text = (
        text
        .replace("–", "-")
        .replace("—", "-")
        .replace("-", "-")
    )

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _contains(text, phrase):
    """
    Deterministic phrase match with flexible hyphen/space handling.
    """

    phrase = _normalize(phrase)

    pattern = re.escape(phrase)

    # Allow hyphenated/non-hyphenated surface variants.
    pattern = pattern.replace(r"\-", r"[-\s]")

    return re.search(
        r"(?<!\w)" + pattern + r"(?!\w)",
        text,
        flags=re.IGNORECASE,
    ) is not None


def _matched_cues(text, phrases):
    """
    Return normalized lexical cues actually matched in text.

    Used where independent evidence from multiple semantic
    signature groups is required.
    """
    matches = []

    for phrase in phrases:
        if _contains(text, phrase):
            cue = _normalize(phrase)

            if cue not in matches:
                matches.append(cue)

    return matches


def _any(text, phrases):
    return bool(
        _matched_cues(text, phrases)
    )


# ----------------------------------------------------------------
# Existing canonical service patterns
# ----------------------------------------------------------------

CANONICAL = {
    "eMBB": [
        "embb",
        "enhanced mobile broadband",
    ],

    "URLLC": [
        "urllc",
        "ultra-reliable low-latency",
        "ultra reliable low latency",
    ],

    "mMTC": [
        "mmtc",
        "massive machine-type",
        "massive machine type",
        "massive iot",
    ],
}


# ----------------------------------------------------------------
# Frozen R6 semantic signature groups
# ----------------------------------------------------------------

EMBB_RATE = [
    "high-throughput",
    "high throughput",
    "high-capacity",
    "high capacity",
    "high-speed",
    "high speed",
    "very high data throughput",
    "bandwidth-intensive",
    "bandwidth intensive",
    "data-heavy",
    "data heavy",
    "demanding mobile data",
]

EMBB_MOBILE_MEDIA = [
    "mobile",
    "mobile users",
    "mobile applications",
    "mobile multimedia",
    "mobile data",
    "broadband",
    "rich media",
    "multimedia",
]


URLLC_DELAY = [
    "extremely low delay",
    "low delay",
    "minimal delay",
    "latency-sensitive",
    "latency sensitive",
    "delay-sensitive",
    "delay sensitive",
    "time-critical",
    "time critical",
    "mission-critical",
    "mission critical",
    "real-time",
    "real time",
    "near-real-time",
    "near real time",
    "critical control",
]

URLLC_RELIABILITY_CONTROL = [
    "strong reliability",
    "highly reliable",
    "very high reliability",
    "dependable",
    "control traffic",
    "control messages",
    "critical control",
    "mission-critical",
    "mission critical",
]


MMTC_SCALE = [
    "very large population",
    "massive numbers",
    "dense",
    "large-scale",
    "large scale",
    "huge numbers",
]

MMTC_MACHINE = [
    "devices",
    "sensors",
    "machine-type",
    "machine type",
    "machine endpoints",
    "iot",
    "telemetry",
]


# ----------------------------------------------------------------
# Signature evaluation
# ----------------------------------------------------------------

def _canonical_matches(text):
    matches = set()

    for service, phrases in CANONICAL.items():
        if _any(text, phrases):
            matches.add(service)

    return matches


def _semantic_matches(text):
    matches = set()

    # eMBB requires evidence from both groups.
    if (
        _any(text, EMBB_RATE)
        and _any(text, EMBB_MOBILE_MEDIA)
    ):
        matches.add("eMBB")

    # URLLC requires independent evidence from both groups.
    #
    # A lexical cue may occur in both signature groups, but the
    # same cue cannot satisfy both required groups by itself.
    urllc_delay_cues = _matched_cues(
        text,
        URLLC_DELAY,
    )

    urllc_reliability_control_cues = _matched_cues(
        text,
        URLLC_RELIABILITY_CONTROL,
    )

    urllc_has_independent_evidence = any(
        delay_cue != reliability_cue
        for delay_cue in urllc_delay_cues
        for reliability_cue
        in urllc_reliability_control_cues
    )

    if urllc_has_independent_evidence:
        matches.add("URLLC")

    # mMTC requires evidence from both groups.
    if (
        _any(text, MMTC_SCALE)
        and _any(text, MMTC_MACHINE)
    ):
        matches.add("mMTC")

    return matches


def resolve_service_type(text):
    """
    Resolve a supported service type deterministically.

    Returns:
        "eMBB", "URLLC", "mMTC", or None.

    Conflict policy:
        If multiple distinct supported services match, return None.
    """

    normalized = _normalize(text)

    canonical = _canonical_matches(normalized)
    semantic = _semantic_matches(normalized)

    all_matches = canonical | semantic

    if len(all_matches) == 1:
        return next(iter(all_matches))

    return None


def resolution_evidence(text):
    """
    Diagnostic evidence only.
    """

    normalized = _normalize(text)

    canonical = sorted(
        _canonical_matches(normalized)
    )

    semantic = sorted(
        _semantic_matches(normalized)
    )

    combined = sorted(
        set(canonical) | set(semantic)
    )

    resolved = (
        combined[0]
        if len(combined) == 1
        else None
    )

    return {
        "canonical_matches": canonical,
        "semantic_matches": semantic,
        "combined_matches": combined,
        "resolved_service_type": resolved,
        "conflict": len(combined) > 1,
    }

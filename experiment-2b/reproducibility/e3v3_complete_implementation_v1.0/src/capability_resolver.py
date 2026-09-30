
"""
Closed-world capability resolver for E3-v2.

Purpose:
Resolve source requirements against the frozen experimental
capability profile.

Design principle:
A requirement is considered supported only when it maps to an
explicit capability represented by the profile.

Unknown requirements are NOT labelled universally impossible.
They are marked unresolved relative to the experimental profile.

This module intentionally does not contain blacklists of fictional
or unsupported terms observed in Experiment 2A.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set

from source_intent import (
    SourceIntent,
    SourceRequirement,
)


# ---------------------------------------------------------
# Frozen profile location
# ---------------------------------------------------------

DEFAULT_PROFILE = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "e3v2_capability_profile_v1.json"
)


# ---------------------------------------------------------
# Supported semantic vocabulary
#
# These are mappings TO supported profile dimensions.
# They are not lists of unsupported words.
# ---------------------------------------------------------

CAPABILITY_ALIASES = {

    "latency_ms": {
        "latency",
        "delay",
        "response time",
    },

    "bandwidth_mbps": {
        "bandwidth",
        "throughput",
        "data rate",
    },

    "reliability": {
        "reliability",
        "availability",
    },

    "device_count": {
        "device count",
        "devices",
        "connections",
        "connected devices",
    },

    "coverage": {
        "coverage",
        "area coverage",
        "geographic coverage",
    },

    "objective": {
        "objective",
        "application objective",
        "service objective",
    },
}


def load_profile(
    profile_path: Optional[Path] = None,
) -> Dict:

    path = (
        Path(profile_path)
        if profile_path is not None
        else DEFAULT_PROFILE
    )

    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def profile_capabilities(
    profile: Dict,
) -> Set[str]:

    raw = profile.get(
        "supported_requirements",
        []
    )

    capabilities = set()

    for item in raw:

        if isinstance(item, str):
            capabilities.add(item)

        elif isinstance(item, dict):

            name = (
                item.get("name")
                or item.get("field")
                or item.get("id")
            )

            if name:
                capabilities.add(name)

    return capabilities


def resolve_capability_text(
    text: str,
    profile: Dict,
) -> Optional[str]:

    """
    Resolve requirement text to one supported capability.

    Returns:
        capability field name
        or None when unresolved.
    """

    normalized_text = re.sub(
        r"\s+",
        " ",
        text.lower().strip(),
    )

    supported = profile_capabilities(
        profile
    )

    matches = []

    for capability, aliases in (
        CAPABILITY_ALIASES.items()
    ):

        if capability not in supported:
            continue

        for alias in aliases:

            pattern = (
                r"(?<!\w)"
                + re.escape(alias)
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                normalized_text,
                flags=re.IGNORECASE,
            ):
                matches.append(capability)
                break

    matches = list(
        dict.fromkeys(matches)
    )

    # Conservative policy:
    # exactly one supported capability must resolve.
    if len(matches) == 1:
        return matches[0]

    return None


def classify_requirement(
    requirement: SourceRequirement,
    profile: Dict,
) -> SourceRequirement:

    resolved = resolve_capability_text(
        requirement.text,
        profile,
    )

    if resolved is None:

        return SourceRequirement(
            text=requirement.text,
            normalized=None,
            status="unresolved",
        )

    return SourceRequirement(
        text=requirement.text,
        normalized=resolved,
        status="supported",
    )


def resolve_source_requirements(
    source: SourceIntent,
    profile: Optional[Dict] = None,
) -> SourceIntent:

    if profile is None:
        profile = load_profile()

    resolved_requirements: List[
        SourceRequirement
    ] = []

    for requirement in source.requirements:

        resolved_requirements.append(
            classify_requirement(
                requirement,
                profile,
            )
        )

    source.requirements = (
        resolved_requirements
    )

    return source

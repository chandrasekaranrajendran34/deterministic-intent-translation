
"""
Deterministic source analyzer for Experiment 2B / E3-v2.

Extracts explicitly expressed:
- service type
- numeric latency constraints
- numeric bandwidth constraints
- numeric reliability constraints
- numeric device-count constraints
- validation/schema/control manipulation attempts

Important scope:
This analyzer intentionally handles explicit linguistic structures.
It does not claim complete semantic understanding of arbitrary
natural language.
"""

import re
from typing import Optional

from source_intent import SourceIntent


# ---------------------------------------------------------
# Service patterns
# ---------------------------------------------------------

SERVICE_PATTERNS = {
    "URLLC": [
        r"\burllc\b",
        r"\bultra[\s-]*reliable[\s-]*low[\s-]*latency\b",
    ],

    "eMBB": [
        r"\bembb\b",
        r"\benhanced[\s-]*mobile[\s-]*broadband\b",
        r"\bmobile[\s-]*broadband\b",
    ],

    "mMTC": [
        r"\bmmtc\b",
        r"\bmassive[\s-]*machine[\s-]*type\b",
        r"\bmassive[\s-]*iot\b",
    ],
}


# ---------------------------------------------------------
# Control-attempt patterns
#
# These represent general manipulation actions rather than
# Experiment-2A-specific fictional capability terms.
# ---------------------------------------------------------

CONTROL_PATTERNS = [
    r"\bbypass\b.{0,40}\b(validat(?:e|ion|or)|schema|policy|check)",
    r"\bskip\b.{0,40}\b(validat(?:e|ion|or)|schema|policy|check)",
    r"\bdisable\b.{0,40}\b(validat(?:e|ion|or)|schema|policy|check)",
    r"\boverride\b.{0,40}\b(validat(?:e|ion|or)|schema|policy|check)",
    r"\bignore\b.{0,40}\b(validat(?:e|ion|or)|schema|policy|check)",
    r"\binvent\b.{0,40}\b(field|parameter|schema)",
    r"\badd\b.{0,30}\bunsupported\b.{0,20}\b(field|parameter)",
]


# ---------------------------------------------------------
# Operator normalization
# ---------------------------------------------------------

def _normalize_operator(text: str) -> str:

    x = text.lower().strip()

    if x in {
        "<",
        "below",
        "under",
        "less than",
    }:
        return "<"

    if x in {
        "<=",
        "at most",
        "no more than",
        "maximum",
        "max",
        "up to",
    }:
        return "<="

    if x in {
        ">",
        "above",
        "over",
        "greater than",
        "more than",
    }:
        return ">"

    if x in {
        ">=",
        "at least",
        "minimum",
        "min",
        "no less than",
    }:
        return ">="

    return "="


# ---------------------------------------------------------
# Service extraction
# ---------------------------------------------------------

def _extract_service(
    text: str,
) -> Optional[str]:

    matches = []

    for service, patterns in SERVICE_PATTERNS.items():

        for pattern in patterns:

            if re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            ):
                matches.append(service)
                break

    matches = list(dict.fromkeys(matches))

    if len(matches) == 1:
        return matches[0]

    return None


# ---------------------------------------------------------
# Generic numeric extraction helper
# ---------------------------------------------------------

OPERATOR = (
    r"(?:"
    r"at\s+least|"
    r"no\s+less\s+than|"
    r"minimum|min|"
    r"at\s+most|"
    r"no\s+more\s+than|"
    r"maximum|max|"
    r"up\s+to|"
    r"less\s+than|"
    r"greater\s+than|"
    r"more\s+than|"
    r"below|under|above|over|"
    r"<=|>=|<|>|=|exactly"
    r")"
)


def _add_matches(
    source: SourceIntent,
    text: str,
    field_name: str,
    patterns,
    unit: Optional[str] = None,
    transform=None,
):

    spans = set()

    for pattern in patterns:

        for match in re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):

            span = match.span()

            # Prevent duplicate extraction when a broader
            # pattern overlaps text already captured by a
            # more specific earlier pattern.
            overlaps_existing = any(
                not (
                    span[1] <= old_span[0]
                    or span[0] >= old_span[1]
                )
                for old_span in spans
            )

            if overlaps_existing:
                continue

            spans.add(span)

            gd = match.groupdict()

            raw_operator = (
                gd.get("op")
                or "="
            )

            operator = _normalize_operator(
                raw_operator
            )

            value = float(
                gd["value"]
            )

            if transform is not None:
                value = transform(
                    value,
                    gd,
                )

            if (
                field_name == "device_count"
                and float(value).is_integer()
            ):
                value = int(value)

            source.add_constraint(
                field_name=field_name,
                operator=operator,
                value=value,
                unit=unit,
                source_text=match.group(0),
            )


# ---------------------------------------------------------
# Main analyzer
# ---------------------------------------------------------

def analyze_source(
    text: str,
) -> SourceIntent:

    source = SourceIntent(
        original_text=text,
        service_type=_extract_service(text),
    )

    # -----------------------------------------------------
    # Control attempts
    # -----------------------------------------------------

    for pattern in CONTROL_PATTERNS:

        for match in re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):

            attempt = match.group(0)

            if attempt not in source.control_attempts:
                source.add_control_attempt(
                    attempt
                )

    # -----------------------------------------------------
    # Latency
    #
    # Supports:
    # "latency below 5 ms"
    # "latency <= 5 ms"
    # "5 ms latency"
    # -----------------------------------------------------

    latency_patterns = [
        rf"\blatency\s+(?P<op>{OPERATOR})\s*(?P<value>\d+(?:\.\d+)?)\s*ms\b",

        rf"(?P<op>{OPERATOR})\s*(?P<value>\d+(?:\.\d+)?)\s*ms\s+latency\b",

        r"\b(?P<value>\d+(?:\.\d+)?)\s*ms\s+latency\b",
    ]

    _add_matches(
        source,
        text,
        "latency_ms",
        latency_patterns,
        unit="ms",
    )

    # -----------------------------------------------------
    # Bandwidth / throughput
    # Mbps and Gbps are normalized to Mbps.
    # -----------------------------------------------------

    bandwidth_patterns = [
        rf"\b(?:bandwidth|throughput)\s+(?P<op>{OPERATOR})\s*(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>mbps|gbps)\b",

        rf"(?P<op>{OPERATOR})\s*(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>mbps|gbps)\s+(?:bandwidth|throughput)\b",

        r"\b(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>mbps|gbps)\s+(?:bandwidth|throughput)\b",
    ]

    def bandwidth_transform(
        value,
        gd,
    ):
        unit_name = (
            gd.get("unit")
            or "mbps"
        ).lower()

        if unit_name == "gbps":
            return value * 1000.0

        return value

    _add_matches(
        source,
        text,
        "bandwidth_mbps",
        bandwidth_patterns,
        unit="Mbps",
        transform=bandwidth_transform,
    )

    # -----------------------------------------------------
    # Reliability
    #
    # Decimal form:
    # reliability >= 0.99999
    #
    # Percentage form:
    # reliability >= 99.999%
    # normalized to 0..1
    # -----------------------------------------------------

    reliability_patterns = [
        rf"\breliability\s+(?P<op>{OPERATOR})\s*(?P<value>\d+(?:\.\d+)?)\s*(?P<percent>%)?",
    ]

    def reliability_transform(
        value,
        gd,
    ):
        if gd.get("percent"):
            return value / 100.0

        return value

    _add_matches(
        source,
        text,
        "reliability",
        reliability_patterns,
        unit=None,
        transform=reliability_transform,
    )

    # -----------------------------------------------------
    # Device count
    # -----------------------------------------------------

    device_patterns = [
        rf"\b(?:device\s*count|devices?)\s+(?P<op>{OPERATOR})\s*(?P<value>\d+)\b",

        rf"(?P<op>{OPERATOR})\s*(?P<value>\d+)\s+devices?\b",

        r"\b(?P<value>\d+)\s+devices?\b",
    ]

    _add_matches(
        source,
        text,
        "device_count",
        device_patterns,
        unit="devices",
    )

    # -----------------------------------------------------
    # Semantic requirement extraction
    #
    # Conservative extraction of explicit requirement
    # constructions not already represented as numeric
    # constraints.
    #
    # Examples:
    #   "require high throughput"
    #   "with very low latency"
    #   "use a novel acceleration mechanism"
    #   "provide a special scheduling capability"
    #
    # Numeric expressions already captured as formal
    # constraints are not duplicated here.
    # -----------------------------------------------------

    requirement_patterns = [
        r"\b(?:require|requires|requiring)\s+"
        r"(?P<req>[^,.;]+)",

        r"\b(?:use|using)\s+"
        r"(?P<req>[^,.;]+)",

        r"\b(?:provide|providing)\s+"
        r"(?P<req>[^,.;]+)",

        r"\bwith\s+"
        r"(?P<req>"
        r"(?:very\s+|high\s+|low\s+|ultra[\s-]*low\s+|"
        r"enhanced\s+|massive\s+)?"
        r"(?:latency|throughput|bandwidth|reliability|"
        r"availability|coverage|device\s+count|"
        r"connected\s+devices)"
        r"(?:\s+[^,.;]+)?"
        r")",
    ]

    existing_requirement_texts = {
        r.text.lower().strip()
        for r in source.requirements
    }

    for pattern in requirement_patterns:

        for match in re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):

            req = (
                match.group("req")
                .strip()
            )

            # Skip fragments containing explicit numeric
            # values because those belong to the formal
            # numeric constraint representation.
            if re.search(
                r"\d",
                req,
            ):
                continue

            req_key = req.lower()

            if req_key in existing_requirement_texts:
                continue

            source.add_requirement(
                req
            )

            existing_requirement_texts.add(
                req_key
            )


    return source

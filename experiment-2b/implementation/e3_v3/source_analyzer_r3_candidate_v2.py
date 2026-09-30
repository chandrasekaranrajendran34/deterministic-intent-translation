
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

    # Direct control-avoidance verbs
    r"\bbypass(?:es|ed|ing)?\b.{0,60}\b(validat(?:e|es|ed|ing|ion|or)|schema|policy|policies|check|checks|rule|rules|control|controls|safeguard|safeguards|guardrail|guardrails|verification|compliance|enforcement|gate|mechanism|stage|step)\b",

    r"\bskip(?:s|ped|ping)?\b.{0,60}\b(validat(?:e|es|ed|ing|ion|or)|schema|policy|policies|check|checks|rule|rules|control|controls|safeguard|safeguards|guardrail|guardrails|verification|compliance|enforcement|gate|mechanism|stage|step)\b",

    r"\bdisabl(?:e|es|ed|ing)\b.{0,60}\b(validat(?:e|es|ed|ing|ion|or)|schema|policy|policies|check|checks|rule|rules|control|controls|safeguard|safeguards|guardrail|guardrails|verification|compliance|enforcement|gate|mechanism|stage|step)\b",

    r"\boverrid(?:e|es|den|ing)\b.{0,60}\b(validat(?:e|es|ed|ing|ion|or)|schema|policy|policies|check|checks|rule|rules|control|controls|safeguard|safeguards|guardrail|guardrails|verification|compliance|enforcement|gate|mechanism|stage|step)\b",

    r"\bignor(?:e|es|ed|ing)\b.{0,60}\b(validat(?:e|es|ed|ing|ion|or)|schema|policy|policies|check|checks|rule|rules|control|controls|safeguard|safeguards|guardrail|guardrails|verification|compliance|enforcement|gate|mechanism|stage|step)\b",

    r"\bsuppress(?:es|ed|ing)?\b.{0,60}\b(validat(?:e|es|ed|ing|ion|or)|schema|policy|policies|check|checks|rule|rules|control|controls|safeguard|safeguards|guardrail|guardrails|verification|compliance|enforcement|gate|mechanism|stage|step)\b",

    r"\bevad(?:e|es|ed|ing)\b.{0,60}\b(validat(?:e|es|ed|ing|ion|or)|schema|policy|policies|check|checks|rule|rules|control|controls|safeguard|safeguards|guardrail|guardrails|verification|compliance|enforcement|gate|mechanism|stage|step)\b",

    r"\bcircumvent(?:s|ed|ing)?\b.{0,60}\b(validat(?:e|es|ed|ing|ion|or)|schema|policy|policies|check|checks|rule|rules|control|controls|safeguard|safeguards|guardrail|guardrails|verification|compliance|enforcement|gate|mechanism|stage|step)\b",

    # Additional generalized avoidance families
    r"\bdisregard(?:s|ed|ing)?\b.{0,60}\b(validation|verification|policy|policies|rule|rules|check|checks|control|controls|safeguard|safeguards|compliance)\b",

    r"\bsidestep(?:s|ped|ping)?\b.{0,60}\b(validation|verification|policy|policies|rule|rules|check|checks|control|controls|safeguard|safeguards|compliance)\b",

    r"\bavoid(?:s|ed|ing)?\b.{0,60}\b(validation|verification|policy|policies|rule|rules|check|checks|control|controls|gate|stage|step|mechanism|safeguard|safeguards)\b",

    r"\bomit(?:s|ted|ting)?\b.{0,60}\b(?:mandatory\s+|required\s+)?(?:validation|verification|policy|compliance)\b",

    r"\bdeactivat(?:e|es|ed|ing)\b.{0,60}\b(validation|verification|policy|control|controls|mechanism|gate|safeguard|safeguards)\b",

    # Phrasal disabling
    r"\bturn(?:s|ed|ing)?\s+off\b.{0,60}\b(validation|verification|policy|policies|control|controls|enforcement|safeguard|safeguards|check|checks)\b",

    # Absence of required validation
    r"\bwithout\s+(?:performing|running|executing|applying|conducting|carrying\s+out)\b.{0,40}\b(validation|verification|policy\s+checks?|compliance\s+checks?|checks?)\b",

    # Passive disabling
    r"\b(validation|verification|policy|controls?|safeguards?|guardrails?|checks?)\b.{0,30}\b(disabled|deactivated|suppressed|bypassed|ignored|overridden)\b",

    # Explicit instruction not to perform protective action
    r"\b(?:instruct(?:s|ed|ing)?|tell(?:s|ing)?|ask(?:s|ed|ing)?)\b.{0,40}\bnot\s+to\s+(?:enforce|apply|perform|run|execute)\b.{0,50}\b(policy|validation|verification|controls?|checks?|safeguards?|compliance)\b",

    # Preserve original unsupported-field manipulation detectors
    r"\binvent\b.{0,40}\b(field|parameter|schema)",

    r"\badd\b.{0,30}\bunsupported\b.{0,20}\b(field|parameter)",
]

def _control_attempt_is_negated(text: str, match_start: int) -> bool:
    """
    Identify explicitly negated control-manipulation language.

    Examples:
        do not bypass validation
        must not disable policy checks
        never ignore validation rules
        without bypassing validation

    Only a short local prefix is examined.
    """

    prefix = text[
        max(0, match_start - 48):
        match_start
    ].lower()

    return bool(
        re.search(
            r"(?:"
            r"\bdo\s+not\s+|"
            r"\bdoes\s+not\s+|"
            r"\bdid\s+not\s+|"
            r"\bmust\s+not\s+|"
            r"\bshould\s+not\s+|"
            r"\bshall\s+not\s+|"
            r"\bnever\s+|"
            r"\bwithout\s+"
            r")$",
            prefix,
            flags=re.IGNORECASE,
        )
    )



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
        "no lower than",
    }:
        return ">="

    if x in {
        "no greater than",
        "no higher than",
    }:
        return "<="

    if x in {
        "fewer than",
    }:
        return "<"

    if x in {
        "fixed at",
        "set to",
        "set to exactly",
        "exactly",
    }:
        return "="

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
    r"no\s+lower\s+than|"
    r"minimum|min|"
    r"at\s+most|"
    r"no\s+more\s+than|"
    r"no\s+greater\s+than|"
    r"no\s+higher\s+than|"
    r"maximum|max|"
    r"up\s+to|"
    r"fewer\s+than|"
    r"less\s+than|"
    r"greater\s+than|"
    r"more\s+than|"
    r"below|under|above|over|"
    r"fixed\s+at|"
    r"exactly|"
    r"<=|>=|<|>|="
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
# E3-v3 R2-v2
# Coordinated same-field numeric extraction
# ---------------------------------------------------------

def _r2_signature(c):
    return (
        c.field,
        c.operator,
        c.value,
        c.unit,
    )


def _r2_add_unique(
    source,
    field_name,
    operator,
    value,
    unit,
    source_text,
):
    """
    Add only semantically new constraints.

    This prevents R2 from duplicating constraints already captured
    by the original deterministic extractor.
    """

    sig = (
        field_name,
        operator,
        value,
        unit,
    )

    existing = {
        _r2_signature(c)
        for c in source.constraints
    }

    if sig in existing:
        return

    source.add_constraint(
        field_name=field_name,
        operator=operator,
        value=value,
        unit=unit,
        source_text=source_text,
    )


def _r2_numeric_value(
    value_text,
    unit_text=None,
    field_name=None,
):
    value = float(value_text)

    if (
        field_name == "bandwidth_mbps"
        and unit_text
        and unit_text.lower() == "gbps"
    ):
        value *= 1000.0

    if (
        field_name == "device_count"
        and value.is_integer()
    ):
        return int(value)

    return value


def _extract_r2_same_field_constraints(
    source,
    text,
):
    """
    Extract two explicit numeric constraints sharing one field.

    R2 performs representation/extraction only.
    Contradiction decisions remain entirely in
    constraint_consistency.py.
    """

    # -------------------------------------------------------------
    # BANDWIDTH — field anchored before first constraint.
    #
    # Examples:
    # bandwidth exactly 320 Mbps and above 700 Mbps
    # bandwidth no greater than 350 Mbps but at least 750 Mbps
    # -------------------------------------------------------------

    bandwidth = re.compile(
        rf"""
        \b(?:bandwidth|throughput)\b
        \s*
        (?P<op1>{OPERATOR})
        \s*
        (?P<v1>\d+(?:\.\d+)?)
        \s*
        (?P<u1>mbps|gbps)
        \s*
        (?:
            and|
            but|
            yet|
            while(?:\s+also)?
        )
        \s*
        (?P<op2>{OPERATOR})
        \s*
        (?P<v2>\d+(?:\.\d+)?)
        \s*
        (?P<u2>mbps|gbps)
        \b
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    for m in bandwidth.finditer(text):

        for i in ("1", "2"):

            _r2_add_unique(
                source,
                "bandwidth_mbps",
                _normalize_operator(
                    m.group("op" + i)
                ),
                _r2_numeric_value(
                    m.group("v" + i),
                    m.group("u" + i),
                    "bandwidth_mbps",
                ),
                "Mbps",
                m.group(0),
            )


    # -------------------------------------------------------------
    # LATENCY — ordinary anchored construction.
    # -------------------------------------------------------------

    latency = re.compile(
        rf"""
        \blatency\b
        \s*
        (?P<op1>{OPERATOR})
        \s*
        (?P<v1>\d+(?:\.\d+)?)
        \s*ms
        \s*
        (?:
            and|
            but|
            yet|
            while(?:\s+also)?
        )
        \s*
        (?P<op2>{OPERATOR})
        \s*
        (?P<v2>\d+(?:\.\d+)?)
        \s*ms
        \b
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    for m in latency.finditer(text):

        for i in ("1", "2"):

            _r2_add_unique(
                source,
                "latency_ms",
                _normalize_operator(
                    m.group("op" + i)
                ),
                float(
                    m.group("v" + i)
                ),
                "ms",
                m.group(0),
            )


    # -------------------------------------------------------------
    # LATENCY — "latency to exactly ..."
    #
    # Example:
    # Set URLLC latency to exactly 12 ms and no more than 4 ms.
    # -------------------------------------------------------------

    latency_to = re.compile(
        rf"""
        \blatency\s+to\s+
        (?P<op1>exactly)
        \s*
        (?P<v1>\d+(?:\.\d+)?)
        \s*ms
        \s*
        (?:
            and|
            but|
            yet
        )
        \s*
        (?P<op2>{OPERATOR})
        \s*
        (?P<v2>\d+(?:\.\d+)?)
        \s*ms
        \b
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    for m in latency_to.finditer(text):

        for i in ("1", "2"):

            _r2_add_unique(
                source,
                "latency_ms",
                _normalize_operator(
                    m.group("op" + i)
                ),
                float(
                    m.group("v" + i)
                ),
                "ms",
                m.group(0),
            )


    # -------------------------------------------------------------
    # LATENCY — "while keeping it under ..."
    #
    # Example:
    # latency at least 30 ms while keeping it under 10 ms
    # -------------------------------------------------------------

    latency_keep = re.compile(
        rf"""
        \blatency\s+
        (?P<op1>{OPERATOR})
        \s*
        (?P<v1>\d+(?:\.\d+)?)
        \s*ms
        \s*
        while\s+
        (?:keeping|holding|maintaining)
        \s+it\s+
        (?P<op2>{OPERATOR})
        \s*
        (?P<v2>\d+(?:\.\d+)?)
        \s*ms
        \b
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    for m in latency_keep.finditer(text):

        for i in ("1", "2"):

            _r2_add_unique(
                source,
                "latency_ms",
                _normalize_operator(
                    m.group("op" + i)
                ),
                float(
                    m.group("v" + i)
                ),
                "ms",
                m.group(0),
            )


    # -------------------------------------------------------------
    # DEVICE COUNT — first value followed by "devices".
    #
    # Examples:
    # at least 900000 devices and no more than 200000
    # exactly 400000 devices and no more than 800000
    # fewer than 100000 devices and more than 600000
    # -------------------------------------------------------------

    device_first = re.compile(
        rf"""
        (?P<op1>{OPERATOR})
        \s*
        (?P<v1>\d+)
        \s+devices?
        \s*
        (?:
            and|
            but|
            yet
        )
        \s*
        (?P<op2>{OPERATOR})
        \s*
        (?P<v2>\d+)
        (?:\s+devices?)?
        \b
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    for m in device_first.finditer(text):

        for i in ("1", "2"):

            _r2_add_unique(
                source,
                "device_count",
                _normalize_operator(
                    m.group("op" + i)
                ),
                int(
                    m.group("v" + i)
                ),
                "devices",
                m.group(0),
            )


    # -------------------------------------------------------------
    # DEVICE COUNT — "devices" only after second value.
    #
    # Examples:
    # more than 200000 and fewer than 900000 devices
    # at least 300000 but fewer than 750000 devices
    #
    # IMPORTANT:
    # R2 adds BOTH operator-bearing constraints.
    # A later cleanup removes the spurious bare "=" generated by
    # the old generic device fallback.
    # -------------------------------------------------------------

    device_end = re.compile(
        rf"""
        (?P<op1>{OPERATOR})
        \s*
        (?P<v1>\d+)
        \s*
        (?:
            and|
            but|
            yet
        )
        \s*
        (?P<op2>{OPERATOR})
        \s*
        (?P<v2>\d+)
        \s+devices?
        \b
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    for m in device_end.finditer(text):

        for i in ("1", "2"):

            _r2_add_unique(
                source,
                "device_count",
                _normalize_operator(
                    m.group("op" + i)
                ),
                int(
                    m.group("v" + i)
                ),
                "devices",
                m.group(0),
            )


    # -------------------------------------------------------------
    # BANDWIDTH with first field implicit, second field explicit.
    #
    # Example:
    # capped below 450 Mbps while also requiring its bandwidth
    # to exceed 780 Mbps
    # -------------------------------------------------------------

    implicit_bandwidth = re.compile(
        r"""
        \b(?:capped|limited|kept|held)
        \s+
        (?P<op1>
            below|
            under|
            less\s+than|
            at\s+most|
            no\s+more\s+than|
            no\s+greater\s+than|
            above|
            over|
            greater\s+than|
            more\s+than|
            at\s+least
        )
        \s*
        (?P<v1>\d+(?:\.\d+)?)
        \s*
        (?P<u1>mbps|gbps)
        .{0,80}?
        \b(?:bandwidth|throughput)\b
        (?:\s+to)?
        \s*
        (?P<op2>
            exceed|
            exceeds|
            exceeding|
            below|
            under|
            less\s+than|
            above|
            over|
            greater\s+than|
            more\s+than|
            at\s+least|
            at\s+most|
            no\s+more\s+than
        )
        \s*
        (?P<v2>\d+(?:\.\d+)?)
        \s*
        (?P<u2>mbps|gbps)
        \b
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    def implicit_op(x):

        x = x.lower().strip()

        if x in {
            "exceed",
            "exceeds",
            "exceeding",
        }:
            return ">"

        return _normalize_operator(x)


    for m in implicit_bandwidth.finditer(text):

        for i in ("1", "2"):

            _r2_add_unique(
                source,
                "bandwidth_mbps",
                implicit_op(
                    m.group("op" + i)
                ),
                _r2_numeric_value(
                    m.group("v" + i),
                    m.group("u" + i),
                    "bandwidth_mbps",
                ),
                "Mbps",
                m.group(0),
            )


    # -------------------------------------------------------------
    # REMOVE SPURIOUS BARE DEVICE EQUALITY
    #
    # The legacy generic fallback:
    #
    #     900000 devices  -> "="
    #
    # is useful for genuine bare exact quantities, but is wrong when
    # that number is already explicitly governed by an operator such
    # as "fewer than 900000 devices".
    #
    # Remove "=" only when R2 has independently preserved a
    # non-equality constraint for the SAME numeric device value.
    # -------------------------------------------------------------

    device_non_equal_values = {
        c.value
        for c in source.constraints
        if (
            c.field == "device_count"
            and c.operator != "="
        )
    }

    source.constraints[:] = [
        c
        for c in source.constraints
        if not (
            c.field == "device_count"
            and c.operator == "="
            and c.value in device_non_equal_values
        )
    ]

# ---------------------------------------------------------
# Main analyzer
# ---------------------------------------------------------

def _analyze_source_r1_r2(
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

            if _control_attempt_is_negated(text, match.start()):
                continue
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
    # E3-v3 R2-v2
    # Coordinated same-field constraint preservation
    # -----------------------------------------------------

    _extract_r2_same_field_constraints(
        source,
        text,
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

# =============================================================================
# E3-v3 R3 — OPERATOR-PRESERVATION PARSER EXTENSION
# =============================================================================

_R3_NO_FEWER_DEVICE_RE = re.compile(
    r"\bno\s+fewer\s+than\s+"
    r"(?P<value>\d[\d,]*)\s*"
    r"(?:devices?|connections?|endpoints?)\b",
    flags=re.IGNORECASE,
)


def _r3_normalize_operator_phrases(text: str) -> str:
    """
    Normalize equivalent operator expressions to vocabulary already
    supported by the registered R1+R2 source analyzer.

    This normalization is generic:
      - no benchmark IDs
      - no benchmark-specific numeric values
    """

    normalized = text

    # "precisely 4 milliseconds"
    #          ->
    # "exactly 4 ms"
    normalized = re.sub(
        r"\bprecisely\s+"
        r"(?P<value>\d+(?:\.\d+)?)\s*"
        r"milliseconds?\b",
        lambda match: (
            "exactly "
            + match.group("value")
            + " ms"
        ),
        normalized,
        flags=re.IGNORECASE,
    )

    return normalized


def analyze_source(text: str):
    """
    R3 wrapper around registered R1+R2 source analysis.

    Adds generalized handling for:

        no fewer than N devices
            => device_count >= N

        precisely N milliseconds
            => latency_ms = N

    Existing R1/R2 behavior remains authoritative for all other forms.
    """

    normalized_text = (
        _r3_normalize_operator_phrases(
            text
        )
    )

    source = (
        _analyze_source_r1_r2(
            normalized_text
        )
    )

    # -----------------------------------------------------------------
    # Repair negated comparative:
    #
    #     no fewer than N devices
    #
    # means:
    #
    #     device_count >= N
    #
    # The generic parser may independently see the nested substring
    # "fewer than N" and create < N. Remove only that same-field,
    # same-threshold conflicting interpretation.
    # -----------------------------------------------------------------

    for match in (
        _R3_NO_FEWER_DEVICE_RE.finditer(
            text
        )
    ):

        value = float(
            match.group("value").replace(
                ",",
                "",
            )
        )

        retained = []

        for constraint in source.constraints:

            same_field = (
                constraint.field
                == "device_count"
            )

            try:

                same_value = (
                    abs(
                        float(constraint.value)
                        - value
                    )
                    <= 1e-12
                )

            except (
                TypeError,
                ValueError,
            ):

                same_value = False

            nested_wrong_parse = (
                same_field
                and same_value
                and constraint.operator == "<"
            )

            if not nested_wrong_parse:

                retained.append(
                    constraint
                )

        # Preserve list identity where possible.
        source.constraints[:] = retained

        already_present = False

        for constraint in source.constraints:

            if (
                constraint.field
                != "device_count"
            ):
                continue

            if (
                constraint.operator
                != ">="
            ):
                continue

            try:

                same_value = (
                    abs(
                        float(constraint.value)
                        - value
                    )
                    <= 1e-12
                )

            except (
                TypeError,
                ValueError,
            ):

                same_value = False

            if same_value:

                already_present = True
                break

        if not already_present:

            source.add_constraint(
                field_name="device_count",
                operator=">=",
                value=value,
                unit="devices",
                source_text=match.group(0),
            )

    # The audit trail must retain literal input, not normalized input.
    source.original_text = text

    return source


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
# E3-v3 R2 — coordinated same-field constraint extraction
# ---------------------------------------------------------

def _constraint_signature(
    constraint,
):
    """
    Stable semantic identity used only to avoid duplicate extraction.
    """
    return (
        constraint.field,
        constraint.operator,
        constraint.value,
        constraint.unit,
    )


def _add_constraint_if_new(
    source,
    field_name,
    operator,
    value,
    unit,
    source_text,
):
    """
    Preserve a newly extracted constraint unless the same semantic
    field/operator/value/unit tuple already exists.
    """

    candidate = (
        field_name,
        operator,
        value,
        unit,
    )

    existing = {
        _constraint_signature(c)
        for c in source.constraints
    }

    if candidate in existing:
        return False

    source.add_constraint(
        field_name=field_name,
        operator=operator,
        value=value,
        unit=unit,
        source_text=source_text,
    )

    return True


def _extract_coordinated_same_field_constraints(
    source,
    text,
):
    """
    E3-v3 R2.

    Extract explicit second/subsequent numeric constraints where the
    field is inherited from a preceding same-field clause.

    Examples:
        bandwidth exactly 320 Mbps and above 700 Mbps
        latency exactly 18 ms and below 6 ms
        bandwidth below 200 Mbps and above 600 Mbps
        at least 900000 devices and no more than 200000
        exactly 400000 devices and no more than 800000

    This helper performs extraction only. Logical compatibility is
    evaluated later by constraint_consistency.py.
    """

    # ------------------------------------------------------------------
    # 1. Bandwidth / throughput
    #
    # Require the first clause to anchor the field.
    # The second clause may omit "bandwidth"/"throughput".
    # ------------------------------------------------------------------

    bandwidth_coord = re.compile(
        rf"""
        \b(?:bandwidth|throughput)\s+
        (?P<op1>{OPERATOR})\s*
        (?P<value1>\d+(?:\.\d+)?)\s*
        (?P<unit1>mbps|gbps)
        \s*
        (?:,?\s*(?:and|but|yet|while(?:\s+also)?)\s+)
        (?P<op2>{OPERATOR})\s*
        (?P<value2>\d+(?:\.\d+)?)\s*
        (?P<unit2>mbps|gbps)
        \b
        """,
        flags=re.IGNORECASE | re.VERBOSE,
    )

    for match in bandwidth_coord.finditer(text):

        for suffix in ("1", "2"):

            op = _normalize_operator(
                match.group(f"op{suffix}")
            )

            value = float(
                match.group(f"value{suffix}")
            )

            raw_unit = (
                match.group(f"unit{suffix}")
                .lower()
            )

            if raw_unit == "gbps":
                value *= 1000.0

            _add_constraint_if_new(
                source=source,
                field_name="bandwidth_mbps",
                operator=op,
                value=value,
                unit="Mbps",
                source_text=match.group(0),
            )


    # ------------------------------------------------------------------
    # 2. Latency
    # ------------------------------------------------------------------

    latency_coord = re.compile(
        rf"""
        \blatency\s+
        (?P<op1>{OPERATOR})\s*
        (?P<value1>\d+(?:\.\d+)?)\s*ms
        \s*
        (?:,?\s*(?:and|but|yet|while(?:\s+also)?)\s+)
        (?P<op2>{OPERATOR})\s*
        (?P<value2>\d+(?:\.\d+)?)\s*ms
        \b
        """,
        flags=re.IGNORECASE | re.VERBOSE,
    )

    for match in latency_coord.finditer(text):

        for suffix in ("1", "2"):

            _add_constraint_if_new(
                source=source,
                field_name="latency_ms",
                operator=_normalize_operator(
                    match.group(f"op{suffix}")
                ),
                value=float(
                    match.group(f"value{suffix}")
                ),
                unit="ms",
                source_text=match.group(0),
            )


    # ------------------------------------------------------------------
    # 3. Device count — field appears after second value.
    #
    # Example:
    #   at least 900000 devices and no more than 200000
    #
    # Existing extraction captures the first clause because it contains
    # "devices"; R2 preserves the coordinated second constraint.
    # ------------------------------------------------------------------

    device_first_anchor = re.compile(
        rf"""
        (?P<op1>{OPERATOR})\s*
        (?P<value1>\d+)\s+
        devices?
        \s*
        (?:,?\s*(?:and|but|yet|while(?:\s+also)?)\s+)
        (?P<op2>{OPERATOR})\s*
        (?P<value2>\d+)
        (?:\s+devices?)?
        \b
        """,
        flags=re.IGNORECASE | re.VERBOSE,
    )

    for match in device_first_anchor.finditer(text):

        for suffix in ("1", "2"):

            _add_constraint_if_new(
                source=source,
                field_name="device_count",
                operator=_normalize_operator(
                    match.group(f"op{suffix}")
                ),
                value=int(
                    match.group(f"value{suffix}")
                ),
                unit="devices",
                source_text=match.group(0),
            )


    # ------------------------------------------------------------------
    # 4. Device count — unit/field only appears at end.
    #
    # Example:
    #   more than 200000 and fewer than 900000 devices
    #
    # "fewer than" is normalized locally to "<".
    # ------------------------------------------------------------------

    device_end_anchor = re.compile(
        r"""
        (?P<op1>
            at\s+least|
            no\s+less\s+than|
            no\s+lower\s+than|
            more\s+than|
            greater\s+than|
            above|
            over|
            at\s+most|
            no\s+more\s+than|
            no\s+higher\s+than|
            fewer\s+than|
            less\s+than|
            below|
            under|
            exactly
        )
        \s*
        (?P<value1>\d+)
        \s*
        (?:,?\s*(?:and|but|yet|while(?:\s+also)?)\s+)
        (?P<op2>
            at\s+least|
            no\s+less\s+than|
            no\s+lower\s+than|
            more\s+than|
            greater\s+than|
            above|
            over|
            at\s+most|
            no\s+more\s+than|
            no\s+higher\s+than|
            fewer\s+than|
            less\s+than|
            below|
            under|
            exactly
        )
        \s*
        (?P<value2>\d+)
        \s+devices?
        \b
        """,
        flags=re.IGNORECASE | re.VERBOSE,
    )

    def normalize_device_operator(raw):

        x = raw.lower().strip()

        if x in {
            "fewer than",
        }:
            return "<"

        if x in {
            "no higher than",
        }:
            return "<="

        if x in {
            "no lower than",
        }:
            return ">="

        return _normalize_operator(x)


    for match in device_end_anchor.finditer(text):

        for suffix in ("1", "2"):

            _add_constraint_if_new(
                source=source,
                field_name="device_count",
                operator=normalize_device_operator(
                    match.group(f"op{suffix}")
                ),
                value=int(
                    match.group(f"value{suffix}")
                ),
                unit="devices",
                source_text=match.group(0),
            )


    # ------------------------------------------------------------------
    # 5. Field repeated only in second bandwidth clause.
    #
    # Example:
    #   capped below 450 Mbps while also requiring its bandwidth
    #   to exceed 780 Mbps
    #
    # This is still generic: two explicit bandwidth quantities in a
    # coordinated construction.
    # ------------------------------------------------------------------

    bandwidth_repeated_second = re.compile(
        r"""
        \b(?:capped|limited|kept|held)?
        \s*
        (?P<op1>
            below|under|less\s+than|
            at\s+most|no\s+more\s+than|
            above|over|greater\s+than|more\s+than|
            at\s+least|exactly
        )
        \s*
        (?P<value1>\d+(?:\.\d+)?)\s*
        (?P<unit1>mbps|gbps)
        .{0,70}?
        \b(?:bandwidth|throughput)\b
        (?:\s+to)?
        \s*
        (?P<op2>
            exceed|exceeds|exceeding|
            fall\s+below|
            stay\s+below|
            remain\s+below|
            below|under|less\s+than|
            at\s+most|no\s+more\s+than|
            above|over|greater\s+than|more\s+than|
            at\s+least|exactly
        )
        \s*
        (?P<value2>\d+(?:\.\d+)?)\s*
        (?P<unit2>mbps|gbps)
        \b
        """,
        flags=re.IGNORECASE | re.VERBOSE,
    )

    def normalize_extended_operator(raw):

        x = raw.lower().strip()

        if x in {
            "exceed",
            "exceeds",
            "exceeding",
        }:
            return ">"

        if x in {
            "fall below",
            "stay below",
            "remain below",
        }:
            return "<"

        return _normalize_operator(x)


    for match in bandwidth_repeated_second.finditer(text):

        for suffix in ("1", "2"):

            value = float(
                match.group(f"value{suffix}")
            )

            raw_unit = (
                match.group(f"unit{suffix}")
                .lower()
            )

            if raw_unit == "gbps":
                value *= 1000.0

            _add_constraint_if_new(
                source=source,
                field_name="bandwidth_mbps",
                operator=normalize_extended_operator(
                    match.group(f"op{suffix}")
                ),
                value=value,
                unit="Mbps",
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
    # E3-v3 R2
    #
    # Preserve coordinated second/subsequent constraints
    # whose field is inherited from the first clause.
    # Logical consistency remains the responsibility of
    # constraint_consistency.py.
    # -----------------------------------------------------

    _extract_coordinated_same_field_constraints(
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

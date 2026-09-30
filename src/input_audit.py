import re


ALLOWED_PARAMETER_TERMS = {
    "service_type",
    "latency",
    "latency_ms",
    "bandwidth",
    "bandwidth_mbps",
    "reliability",
    "device_count",
    "coverage",
    "objective",
}


def audit_input(intent: str):
    """
    Deterministic audit of explicit parameter-like assignments
    appearing in the original natural-language intent.

    This is intentionally conservative. It does not attempt
    general natural-language understanding.
    """

    errors = []
    unsupported_parameters = []

    # Detect explicit forms such as:
    # quantum_priority=10
    # foo = 25
    pattern = r"\b([A-Za-z_][A-Za-z0-9_]*)\s*="

    parameters = re.findall(pattern, intent)

    for parameter in parameters:
        normalized = parameter.lower()

        if normalized not in ALLOWED_PARAMETER_TERMS:
            unsupported_parameters.append(parameter)

    if unsupported_parameters:
        errors.append(
            "UNSUPPORTED_INPUT_PARAMETER: "
            + ", ".join(sorted(set(unsupported_parameters)))
        )

    return {
        "valid": len(errors) == 0,
        "unsupported_parameters":
            sorted(set(unsupported_parameters)),
        "errors": errors,
    }
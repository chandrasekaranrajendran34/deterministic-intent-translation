from jsonschema import Draft202012Validator
from .schema import CIR_SCHEMA, ALLOWED, SUPPORTED


def validate_cir(c):
    errors = []

    # 1. Detect unknown/generated fields
    unknown = sorted(set(c) - ALLOWED)

    # 2. Collect ALL JSON-schema violations
    validator = Draft202012Validator(CIR_SCHEMA)

    schema_errors = sorted(
        validator.iter_errors(c),
        key=lambda e: (
            ".".join(str(x) for x in e.path),
            e.message
        )
    )

    for e in schema_errors:
        if e.path:
            field = ".".join(str(x) for x in e.path)
            errors.append(f"{field}: {e.message}")
        else:
            errors.append(f"SCHEMA: {e.message}")

    schema_valid = len(schema_errors) == 0

    # 3. Semantic service-type validation
    svc = c.get("service_type")

    if svc is None:
        errors.append("SERVICE_TYPE_UNRESOLVED")
    elif svc not in SUPPORTED:
        errors.append("SERVICE_TYPE_UNSUPPORTED")

    # 4. Unknown fields
    if unknown:
        errors.append(
            "UNKNOWN_FIELDS:" + ",".join(unknown)
        )

    # 5. Final deterministic decision
    accepted = (
        schema_valid
        and svc in SUPPORTED
        and not unknown
    )

    return {
        "accepted": accepted,
        "schema_valid": schema_valid,
        "hallucination_detected": bool(unknown),
        "errors": errors
    }

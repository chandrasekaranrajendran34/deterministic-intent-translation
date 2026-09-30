"""
E3-v3 R3 operator-aware source-constraint sidecar.

Purpose
-------
Preserve deterministic source-level constraint semantics without changing
the historical canonical CIR schema.

The canonical CIR remains the original seven-field representation.
Operator semantics are represented separately as source-bound metadata.

No LLM/API calls are performed here.
"""

SUPPORTED_OPERATORS = {
    "=",
    "<",
    "<=",
    ">",
    ">=",
}


def build_constraint_semantics(source_intent):

    semantics = []

    for constraint in source_intent.constraints:

        if constraint.operator not in SUPPORTED_OPERATORS:
            continue

        semantics.append({
            "field":
                constraint.field,

            "operator":
                constraint.operator,

            "threshold":
                constraint.value,

            "unit":
                constraint.unit,

            "source_text":
                constraint.source_text,
        })

    return semantics


def get_cir_value(cir, field):

    if isinstance(cir, dict):
        return cir.get(field)

    return getattr(
        cir,
        field,
        None,
    )


def threshold_matches_cir(
    cir,
    semantic,
    tolerance=1e-9,
):

    cir_value = get_cir_value(
        cir,
        semantic["field"],
    )

    if cir_value is None:
        return False

    threshold = semantic[
        "threshold"
    ]

    try:

        return abs(
            float(cir_value)
            - float(threshold)
        ) <= tolerance

    except (TypeError, ValueError):

        return cir_value == threshold


def semantic_constraint_preserved(
    cir,
    semantic,
    tolerance=1e-9,
):
    """
    Representation-level preservation.

    The scalar CIR value is treated as the represented threshold, not as
    an achieved runtime measurement.

    Operator identity remains explicit in the source-bound sidecar.
    """

    if (
        semantic.get("operator")
        not in SUPPORTED_OPERATORS
    ):
        return False

    return threshold_matches_cir(
        cir,
        semantic,
        tolerance=tolerance,
    )

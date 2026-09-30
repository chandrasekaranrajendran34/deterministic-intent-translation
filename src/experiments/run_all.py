
import json
from pathlib import Path

import pandas as pd

from src.llm.together_adapter import call_json
from src.validator import validate_cir
from src.input_audit import audit_input
from src.standards.mapper import map_standards
from src.descriptor import compile_descriptor


def run(
    dataset,
    out_path,
    model="Qwen/Qwen3.5-9B",
    limit=None
):
    df = pd.read_csv(dataset)

    if limit:
        df = df.head(limit)

    out = []

    for _, r in df.iterrows():

        for pipeline in [
            "direct",
            "cir",
            "proposed"
        ]:

            # ---------------------------------
            # LLM call
            # ---------------------------------

            mode = (
                "direct"
                if pipeline == "direct"
                else "cir"
            )

            llm = call_json(
                r.intent,
                mode,
                model
            )

            output = llm["json"]

            record = {
                "id": r.id,
                "intent": r.intent,
                "category": r.category,
                "expected_service":
                    r.expected_service
                    if pd.notna(r.expected_service)
                    else None,
                "expected_valid":
                    bool(r.expected_valid),
                "pipeline": pipeline,
                "model": model,
                "parse_ok": llm["parse_ok"],
                "latency_ms":
                    llm["latency_ms"],
                "finish_reason":
                    llm.get("finish_reason"),
                "prompt_tokens":
                    llm.get("prompt_tokens"),
                "completion_tokens":
                    llm.get(
                        "completion_tokens"
                    ),
                "raw_response":
                    llm["raw"]
            }

            # =================================
            # E1 — DIRECT BASELINE
            # =================================

            if pipeline == "direct":

                reject = (
                    bool(
                        output.get(
                            "rejected",
                            False
                        )
                    )
                    if isinstance(output, dict)
                    else True
                )

                accepted = (
                    llm["parse_ok"]
                    and not reject
                )

                record.update({
                    "predicted_service":
                        output.get(
                            "service_type"
                        )
                        if isinstance(
                            output,
                            dict
                        )
                        else None,

                    "schema_valid":
                        llm["parse_ok"],

                    "hallucination_detected":
                        False,

                    "unsupported_input_detected":
                        False,

                    "input_audit_valid":
                        None,

                    "mapping_found":
                        False,

                    "descriptor_success":
                        accepted,

                    "accepted":
                        accepted,

                    "validation_errors":
                        None,

                    "cir_json":
                        None,

                    "descriptor_json":
                        json.dumps(output)
                        if (
                            isinstance(
                                output,
                                dict
                            )
                            and accepted
                        )
                        else None
                })

            # =================================
            # E2 — CIR BASELINE
            # =================================

            elif pipeline == "cir":

                cir = (
                    output
                    if isinstance(
                        output,
                        dict
                    )
                    else {}
                )

                validation = (
                    validate_cir(cir)
                )

                mapping = (
                    map_standards(cir)
                    if validation["accepted"]
                    else {
                        "mapping_found": False
                    }
                )

                descriptor = None

                if (
                    validation["accepted"]
                    and mapping[
                        "mapping_found"
                    ]
                ):
                    descriptor = (
                        compile_descriptor(
                            cir,
                            mapping
                        )
                    )

                record.update({
                    "predicted_service":
                        cir.get(
                            "service_type"
                        ),

                    "schema_valid":
                        validation[
                            "schema_valid"
                        ],

                    "hallucination_detected":
                        validation[
                            "hallucination_detected"
                        ],

                    "unsupported_input_detected":
                        False,

                    "input_audit_valid":
                        None,

                    "mapping_found":
                        mapping.get(
                            "mapping_found",
                            False
                        ),

                    "descriptor_success":
                        descriptor is not None,

                    # E2 decision is based on
                    # structured CIR validation.
                    "accepted":
                        validation[
                            "accepted"
                        ],

                    "validation_errors":
                        ";".join(
                            validation[
                                "errors"
                            ]
                        ),

                    "cir_json":
                        json.dumps(cir),

                    "descriptor_json":
                        json.dumps(
                            descriptor
                        )
                        if descriptor
                        else None
                })

            # =================================
            # E3 — PROPOSED PIPELINE
            # =================================

            else:

                cir = (
                    output
                    if isinstance(
                        output,
                        dict
                    )
                    else {}
                )

                # Deterministic audit of
                # original user intent.
                input_audit = audit_input(
                    r.intent
                )

                # Deterministic CIR validation.
                validation = (
                    validate_cir(cir)
                )

                pre_mapping_valid = (
                    llm["parse_ok"]
                    and input_audit["valid"]
                    and validation[
                        "accepted"
                    ]
                )

                # Standards mapping occurs only
                # after deterministic checks.
                if pre_mapping_valid:
                    mapping = (
                        map_standards(cir)
                    )
                else:
                    mapping = {
                        "mapping_found": False
                    }

                descriptor = None

                if (
                    pre_mapping_valid
                    and mapping.get(
                        "mapping_found",
                        False
                    )
                ):
                    descriptor = (
                        compile_descriptor(
                            cir,
                            mapping
                        )
                    )

                accepted = (
                    pre_mapping_valid
                    and mapping.get(
                        "mapping_found",
                        False
                    )
                    and descriptor is not None
                )

                all_errors = (
                    input_audit["errors"]
                    + validation["errors"]
                )

                record.update({
                    "predicted_service":
                        cir.get(
                            "service_type"
                        ),

                    "schema_valid":
                        validation[
                            "schema_valid"
                        ],

                    "hallucination_detected":
                        validation[
                            "hallucination_detected"
                        ],

                    "unsupported_input_detected":
                        len(
                            input_audit[
                                "unsupported_parameters"
                            ]
                        ) > 0,

                    "input_audit_valid":
                        input_audit[
                            "valid"
                        ],

                    "mapping_found":
                        mapping.get(
                            "mapping_found",
                            False
                        ),

                    "descriptor_success":
                        descriptor is not None,

                    "accepted":
                        accepted,

                    "validation_errors":
                        ";".join(
                            all_errors
                        ),

                    "cir_json":
                        json.dumps(cir),

                    "descriptor_json":
                        json.dumps(
                            descriptor
                        )
                        if descriptor
                        else None
                })

            out.append(record)

    results = pd.DataFrame(out)

    Path(out_path).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    results.to_csv(
        out_path,
        index=False
    )

    return results

import argparse
import time
import random
import json
from pathlib import Path

import pandas as pd

from src.validator import validate_cir
from src.standards.mapper import map_standards
from src.descriptor import compile_descriptor

from journal_experiments.experiment_B_review_requested_constrained_decoding.implementation.experiment_B_review_structured_adapter_v1 import (
    call_json_structured
)


def run(
    dataset,
    out_path,
    model="Qwen/Qwen3.5-9B"
):
    df = pd.read_csv(dataset)

    out = []

    for _, r in df.iterrows():

        # Execution-resilience wrapper only.
        # Scientific treatment arguments are unchanged.
        max_attempts = 5
        llm = None

        for attempt in range(1, max_attempts + 1):
            try:
                llm = call_json_structured(
                    r.intent,
                    mode="cir",
                    model=model
                )
                break

            except Exception as exc:
                message = str(exc).lower()

                transient = (
                    "503" in message
                    or "service unavailable" in message
                    or "timeout" in message
                    or "temporarily unavailable" in message
                    or "rate limit" in message
                    or "429" in message
                )

                if (not transient) or attempt == max_attempts:
                    raise

                wait_seconds = min(30, 2 ** attempt)

                print(
                    f"TRANSIENT_PROVIDER_RETRY "
                    f"case={r.id} "
                    f"attempt={attempt}/{max_attempts} "
                    f"wait={wait_seconds}s",
                    flush=True
                )

                time.sleep(wait_seconds)

        assert llm is not None

        output = llm["json"]

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

        record = {
            "id":
                r.id,

            "intent":
                r.intent,

            "category":
                r.category,

            "expected_service":
                r.expected_service
                if pd.notna(
                    r.expected_service
                )
                else None,

            "expected_valid":
                bool(
                    r.expected_valid
                ),

            "pipeline":
                "cir_constrained",

            "model":
                model,

            "parse_ok":
                llm["parse_ok"],

            "latency_ms":
                llm["latency_ms"],

            "finish_reason":
                llm.get(
                    "finish_reason"
                ),

            "prompt_tokens":
                llm.get(
                    "prompt_tokens"
                ),

            "completion_tokens":
                llm.get(
                    "completion_tokens"
                ),

            "raw_response":
                llm["raw"],

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

            # Historical CIR decision:
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
                json.dumps(
                    cir
                ),

            "descriptor_json":
                json.dumps(
                    descriptor
                )
                if descriptor
                else None
        }

        out.append(
            record
        )

        print(
            f"[{len(out)}/{len(df)}] "
            f"{r.id}",
            flush=True
        )

    results = pd.DataFrame(
        out
    )

    Path(out_path).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    results.to_csv(
        out_path,
        index=False
    )

    print()
    print(
        "Rows written:",
        len(results)
    )

    print(
        "Output:",
        out_path
    )

    return results


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset",
        required=True
    )

    parser.add_argument(
        "--out",
        required=True
    )

    parser.add_argument(
        "--model",
        default="Qwen/Qwen3.5-9B"
    )

    args = parser.parse_args()

    run(
        args.dataset,
        args.out,
        args.model
    )


if __name__ == "__main__":
    main()

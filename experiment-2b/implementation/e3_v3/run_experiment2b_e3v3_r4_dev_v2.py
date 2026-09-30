"""
E3-v3 DEVELOPMENT-ONLY RUNNER

Generated during STEP 24E-D2.

Scientific role:
    Development evaluation only.

This runner is NOT the frozen E3-v2 runner.

Differences from the copied E3-v2 execution harness:
    1. Local guard imports resolve to implementation/e3_v3/src.
    2. run_e3_v2 is named run_e3_v3.
    3. output pipeline label is e3_v3.
    4. dataset loop executes only e3_v3.
    5. historical runner remains unchanged.

No algorithmic CIR/LLM/validation/descriptor logic is intentionally
changed in this development harness.
"""


import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd


# ============================================================
# Paths / imports
# ============================================================

THIS_FILE = Path(__file__).resolve()

E3V3_ROOT = THIS_FILE.parent
EXP2B_ROOT = E3V3_ROOT.parents[1]
PROJECT_ROOT = EXP2B_ROOT.parent
E3V3_SRC = E3V3_ROOT / "src"

# Shared project modules:
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# CRITICAL:
# E3-v3 source must precede historical experiment2b/src
# for local guard imports.
if str(E3V3_SRC) not in sys.path:
    sys.path.insert(0, str(E3V3_SRC))


from src.llm.together_adapter import call_json
from src.input_audit import audit_input
from src.validator import validate_cir
from src.standards.mapper import map_standards
from src.descriptor import compile_descriptor

from e3v2_guard import evaluate_guard
from cir_reconciliation import reconcile_cir


DEFAULT_MODEL = "Qwen/Qwen3.5-9B"


# ============================================================
# Helpers
# ============================================================

def json_text(value):
    if value is None:
        return ""

    try:
        if hasattr(value, "to_dict"):
            value = value.to_dict()

        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )

    except Exception:
        return json.dumps(
            str(value),
            ensure_ascii=False,
        )


def obj_dict(value):
    if value is None:
        return None

    if hasattr(value, "to_dict"):
        return value.to_dict()

    if isinstance(value, dict):
        return value

    if hasattr(value, "__dict__"):
        return dict(value.__dict__)

    return {"value": str(value)}


def field(obj, *names, default=None):
    if obj is None:
        return default

    if isinstance(obj, dict):
        for name in names:
            if name in obj:
                return obj[name]
        return default

    for name in names:
        if hasattr(obj, name):
            return getattr(obj, name)

    return default


def bool_field(obj, *names, default=False):
    value = field(
        obj,
        *names,
        default=default,
    )

    return bool(value)


def error_codes(obj):
    d = obj_dict(obj)

    if not d:
        return []

    errors = d.get("errors", [])

    codes = []

    for err in errors:
        if isinstance(err, dict):
            code = err.get("code")

        elif isinstance(err, str):
            code = err

        else:
            code = getattr(
                err,
                "code",
                None,
            )

        if code:
            codes.append(str(code))

    if not codes:
        direct = d.get("error_codes")
        if isinstance(direct, list):
            codes.extend(
                str(x)
                for x in direct
            )

    return codes


def parse_llm_result(result):
    """
    Preserve the complete adapter output while extracting the
    parsed CIR and common metadata defensively.
    """

    raw_result = obj_dict(result)

    if isinstance(result, dict):
        parsed = (
            result.get("json")
            if "json" in result
            else result.get("parsed")
        )
    else:
        parsed = field(
            result,
            "json",
            "parsed",
            default=None,
        )

    parse_ok = bool_field(
        result,
        "parse_ok",
        default=(parsed is not None),
    )

    latency_ms = field(
        result,
        "latency_ms",
        default=None,
    )

    finish_reason = field(
        result,
        "finish_reason",
        default=None,
    )

    raw_text = field(
        result,
        "raw",
        "text",
        "content",
        default=None,
    )

    reasoning = field(
        result,
        "reasoning",
        default=None,
    )

    prompt_tokens = field(
        result,
        "prompt_tokens",
        default=None,
    )

    completion_tokens = field(
        result,
        "completion_tokens",
        default=None,
    )

    return {
        "adapter_result": raw_result,
        "cir": parsed,
        "parse_ok": parse_ok,
        "llm_latency_ms": latency_ms,
        "finish_reason": finish_reason,
        "raw_text": raw_text,
        "reasoning": reasoning,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
    }


def call_cir(intent, model):
    """
    Use exactly the historical Experiment 1/2A CIR
    invocation. The semantic extraction instructions
    remain in CIR_SYSTEM_PROMPT inside call_json().
    """

    return call_json(
        intent,
        mode="cir",
        model=model,
    )


def safe_map_and_compile(cir):
    mapping = map_standards(cir)

    descriptor = compile_descriptor(
        cir,
        mapping,
    )

    return mapping, descriptor


# ============================================================
# Original E3
# ============================================================

def run_e3_original(intent, model):

    start = time.perf_counter()

    record = {
        "pipeline": "e3_original",
        "llm_invoked": True,
        "accepted": False,
        "rejection_stage": "",
        "error_codes": [],
    }

    try:
        llm_result = call_cir(
            intent,
            model,
        )

        llm = parse_llm_result(
            llm_result
        )

        record.update(llm)

        cir = llm["cir"]

        if not llm["parse_ok"] or cir is None:
            record["rejection_stage"] = "llm_parse"
            record["error_codes"] = [
                "LLM_PARSE_FAILURE"
            ]
            return finalize(
                record,
                start,
            )

        audit = audit_input(intent)
        record["input_audit"] = obj_dict(audit)

        audit_valid = bool_field(
            audit,
            "valid",
            "accepted",
            "is_valid",
            default=True,
        )

        if not audit_valid:
            record["rejection_stage"] = "input_audit"
            record["error_codes"] = (
                error_codes(audit)
                or ["INPUT_AUDIT_REJECTION"]
            )

            return finalize(
                record,
                start,
            )

        validation = validate_cir(cir)
        record["cir_validation"] = obj_dict(
            validation
        )

        validation_valid = bool_field(
            validation,
            "valid",
            "accepted",
            "is_valid",
            default=False,
        )

        if not validation_valid:
            record["rejection_stage"] = "cir_validation"
            record["error_codes"] = (
                error_codes(validation)
                or ["CIR_VALIDATION_REJECTION"]
            )

            return finalize(
                record,
                start,
            )

        mapping, descriptor = (
            safe_map_and_compile(cir)
        )

        record["standards_mapping"] = mapping
        record["descriptor"] = descriptor

        record["accepted"] = True
        record["rejection_stage"] = ""

        return finalize(
            record,
            start,
        )

    except Exception as exc:
        record["accepted"] = False
        record["rejection_stage"] = "exception"
        record["error_codes"] = [
            type(exc).__name__
        ]
        record["exception"] = repr(exc)

        return finalize(
            record,
            start,
        )


# ============================================================
# E3-v2
# ============================================================

def run_e3_v3(intent, model):

    start = time.perf_counter()

    record = {
        "pipeline": "e3_v3",
        "llm_invoked": False,
        "accepted": False,
        "rejection_stage": "",
        "error_codes": [],
    }

    try:

        # ----------------------------------------------------
        # Stage 1:
        # frozen deterministic source-side guard before LLM
        # ----------------------------------------------------

        pre_guard = evaluate_guard(
            intent,
            None,
        )

        pre_guard_dict = obj_dict(
            pre_guard
        )

        record["pre_guard"] = (
            pre_guard_dict
        )

        pre_accepted = bool_field(
            pre_guard,
            "accepted",
            default=False,
        )

        if not pre_accepted:
            record["rejection_stage"] = field(
                pre_guard,
                "rejection_stage",
                default="source_guard",
            )

            record["error_codes"] = (
                error_codes(pre_guard)
                or ["E3V2_PRE_GUARD_REJECTION"]
            )

            return finalize(
                record,
                start,
            )

        # ----------------------------------------------------
        # Stage 2:
        # same CIR generation mechanism
        # ----------------------------------------------------

        record["llm_invoked"] = True

        llm_result = call_cir(
            intent,
            model,
        )

        llm = parse_llm_result(
            llm_result
        )

        record.update(llm)

        cir = llm["cir"]

        if not llm["parse_ok"] or cir is None:
            record["rejection_stage"] = "llm_parse"
            record["error_codes"] = [
                "LLM_PARSE_FAILURE"
            ]

            return finalize(
                record,
                start,
            )

        # ----------------------------------------------------
        # R4:
        # deterministic source-grounded CIR reconciliation
        # ----------------------------------------------------

        record["cir_before_reconciliation"] = dict(cir)

        reconciliation = reconcile_cir(
            intent,
            cir,
        )

        # R4 may return a CIR directly or a structured result.
        if isinstance(reconciliation, dict):

            if (
                "reconciled_cir" in reconciliation
                and isinstance(
                    reconciliation["reconciled_cir"],
                    dict,
                )
            ):
                reconciled_cir = reconciliation[
                    "reconciled_cir"
                ]

            elif (
                "cir" in reconciliation
                and isinstance(
                    reconciliation["cir"],
                    dict,
                )
            ):
                reconciled_cir = reconciliation["cir"]

            else:
                reconciled_cir = reconciliation

        else:
            reconciled_cir = field(
                reconciliation,
                "reconciled_cir",
                "cir",
                default=None,
            )

        if not isinstance(reconciled_cir, dict):
            raise TypeError(
                "R4 reconciliation did not produce "
                "a CIR dictionary"
            )

        cir = reconciled_cir

        record["cir_after_reconciliation"] = dict(cir)
        record["reconciliation"] = obj_dict(
            reconciliation
        )

        # ----------------------------------------------------
        # Stage 3:
        # frozen source-to-CIR preservation guard
        # ----------------------------------------------------

        post_guard = evaluate_guard(
            intent,
            cir,
        )

        record["post_guard"] = obj_dict(
            post_guard
        )

        post_accepted = bool_field(
            post_guard,
            "accepted",
            default=False,
        )

        if not post_accepted:
            record["rejection_stage"] = field(
                post_guard,
                "rejection_stage",
                default="preservation",
            )

            record["error_codes"] = (
                error_codes(post_guard)
                or ["E3V2_POST_GUARD_REJECTION"]
            )

            return finalize(
                record,
                start,
            )

        # ----------------------------------------------------
        # Stage 4:
        # retain original CIR validator
        # ----------------------------------------------------

        validation = validate_cir(cir)

        record["cir_validation"] = obj_dict(
            validation
        )

        validation_valid = bool_field(
            validation,
            "valid",
            "accepted",
            "is_valid",
            default=False,
        )

        if not validation_valid:
            record["rejection_stage"] = "cir_validation"

            record["error_codes"] = (
                error_codes(validation)
                or ["CIR_VALIDATION_REJECTION"]
            )

            return finalize(
                record,
                start,
            )

        # ----------------------------------------------------
        # Stage 5:
        # standards mapping + descriptor compilation
        # ----------------------------------------------------

        mapping, descriptor = (
            safe_map_and_compile(cir)
        )

        record["standards_mapping"] = mapping
        record["descriptor"] = descriptor

        record["accepted"] = True
        record["rejection_stage"] = ""

        return finalize(
            record,
            start,
        )

    except Exception as exc:
        record["accepted"] = False
        record["rejection_stage"] = "exception"
        record["error_codes"] = [
            type(exc).__name__
        ]
        record["exception"] = repr(exc)

        return finalize(
            record,
            start,
        )


# ============================================================
# Finalization
# ============================================================

def finalize(record, start):

    record["end_to_end_latency_ms"] = (
        time.perf_counter() - start
    ) * 1000.0

    return record


# ============================================================
# Dataset execution
# ============================================================

def run(
    dataset,
    out_path,
    model=DEFAULT_MODEL,
    limit=None,
):

    dataset = Path(dataset)
    out_path = Path(out_path)

    df = pd.read_csv(dataset)

    if limit is not None:
        df = df.head(limit)

    rows = []

    for index, row in df.iterrows():

        intent_id = str(row["id"])
        intent = str(row["intent"])

        expected_valid = str(
            row["expected_valid"]
        ).strip().lower() == "true"

        base = {
            "id": intent_id,
            "intent": intent,

            # E3-v3 development-dataset metadata.
            # The frozen 160-case dataset uses family_id/repair_id
            # rather than the historical Experiment-2B "category".
            "family_id": row.get(
                "family_id",
                None,
            ),
            "repair_id": row.get(
                "repair_id",
                None,
            ),
            "subcategory": row.get(
                "subcategory",
                None,
            ),
            "difficulty": row.get(
                "difficulty",
                None,
            ),
            "linguistic_form": row.get(
                "linguistic_form",
                None,
            ),
            "constraint_type": row.get(
                "constraint_type",
                None,
            ),
            "control_type": row.get(
                "control_type",
                None,
            ),
            "notes": row.get(
                "notes",
                None,
            ),

            "expected_valid": expected_valid,
            "expected_service": row.get(
                "expected_service",
                None,
            ),
            "difficulty": row.get(
                "difficulty",
                None,
            ),
            "linguistic_form": row.get(
                "linguistic_form",
                None,
            ),
            "constraint_type": row.get(
                "constraint_type",
                None,
            ),
        }

        print(
            f"[{index + 1}/{len(df)}] "
            f"{intent_id}"
        )

        for pipeline_fn in [
            run_e3_v3,
        ]:

            result = pipeline_fn(
                intent,
                model,
            )

            decision_correct = (
                bool(result["accepted"])
                ==
                expected_valid
            )

            output = dict(base)

            output.update({
                "pipeline":
                    result["pipeline"],

                "accepted":
                    result["accepted"],

                "decision_correct":
                    decision_correct,

                "llm_invoked":
                    result.get(
                        "llm_invoked",
                        False,
                    ),

                "parse_ok":
                    result.get(
                        "parse_ok",
                        None,
                    ),

                "llm_latency_ms":
                    result.get(
                        "llm_latency_ms",
                        None,
                    ),

                "end_to_end_latency_ms":
                    result.get(
                        "end_to_end_latency_ms",
                        None,
                    ),

                "finish_reason":
                    result.get(
                        "finish_reason",
                        None,
                    ),

                "rejection_stage":
                    result.get(
                        "rejection_stage",
                        "",
                    ),

                "error_codes_json":
                    json_text(
                        result.get(
                            "error_codes",
                            [],
                        )
                    ),

                "cir_json":
                    json_text(
                        result.get(
                            "cir"
                        )
                    ),

                "input_audit_json":
                    json_text(
                        result.get(
                            "input_audit"
                        )
                    ),

                "pre_guard_json":
                    json_text(
                        result.get(
                            "pre_guard"
                        )
                    ),

                "post_guard_json":
                    json_text(
                        result.get(
                            "post_guard"
                        )
                    ),

                "cir_before_reconciliation_json":
                    json_text(
                        result.get(
                            "cir_before_reconciliation"
                        )
                    ),

                "cir_after_reconciliation_json":
                    json_text(
                        result.get(
                            "cir_after_reconciliation"
                        )
                    ),

                "reconciliation_json":
                    json_text(
                        result.get(
                            "reconciliation"
                        )
                    ),

                "cir_validation_json":
                    json_text(
                        result.get(
                            "cir_validation"
                        )
                    ),

                "standards_mapping_json":
                    json_text(
                        result.get(
                            "standards_mapping"
                        )
                    ),

                "descriptor_json":
                    json_text(
                        result.get(
                            "descriptor"
                        )
                    ),

                "raw_text":
                    result.get(
                        "raw_text",
                        None,
                    ),

                "reasoning_json":
                    json_text(
                        result.get(
                            "reasoning"
                        )
                    ),

                "prompt_tokens":
                    result.get(
                        "prompt_tokens",
                        None,
                    ),

                "completion_tokens":
                    result.get(
                        "completion_tokens",
                        None,
                    ),

                "adapter_result_json":
                    json_text(
                        result.get(
                            "adapter_result"
                        )
                    ),

                "exception":
                    result.get(
                        "exception",
                        "",
                    ),
            })

            rows.append(output)

    result_df = pd.DataFrame(rows)

    out_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result_df.to_csv(
        out_path,
        index=False,
    )

    return result_df


# ============================================================
# CLI
# ============================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset",
        required=True,
    )

    parser.add_argument(
        "--out",
        required=True,
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
    )

    args = parser.parse_args()

    df = run(
        dataset=args.dataset,
        out_path=args.out,
        model=args.model,
        limit=args.limit,
    )

    print()
    print(
        "Rows written:",
        len(df)
    )

    print(
        "Output:",
        args.out
    )


if __name__ == "__main__":
    main()

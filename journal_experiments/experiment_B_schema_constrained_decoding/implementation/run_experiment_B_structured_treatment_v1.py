"""
Experiment B — schema-constrained decoding treatment harness.

This harness DOES NOT modify or duplicate the frozen E3-v3 pipeline.

It dynamically loads:
  1. the frozen historical E3-v3 runner;
  2. the isolated Experiment-B structured-output adapter.

The only in-memory experimental substitution is:

    frozen_runner.call_json =
        treatment_adapter.call_json_structured

Because frozen call_cir() resolves call_json from its module globals,
all downstream frozen E3-v3 logic remains unchanged.
"""

from pathlib import Path
import argparse
import importlib.util
import sys


ROOT = Path('/content/deterministic-intent-translation-journal')

FROZEN_RUNNER = Path('/content/deterministic-intent-translation-journal/experiment-2b/implementation/e3_v3/run_experiment2b_e3v3_r7_dev_v1.py')

TREATMENT_ADAPTER = Path('/content/deterministic-intent-translation-journal/journal_experiments/experiment_B_schema_constrained_decoding/implementation/experiment_B_structured_adapter_v1.py')

EXPECTED_RUNNER_SHA256 = '40c035cb864978c718a72fcfdfbb164d262529960b0ae78242d5194147cd8257'

EXPECTED_TREATMENT_ADAPTER_SHA256 = '3e2a1cac6c2427eab9a28b69dc67b9a659ff9c83fd3d7bacb84222c51a21b4b6'


def sha256(path):
    import hashlib

    h = hashlib.sha256()

    with open(path, "rb") as f:
        for block in iter(
            lambda: f.read(1024 * 1024),
            b""
        ):
            h.update(block)

    return h.hexdigest()


def load_module(name, path):

    spec = importlib.util.spec_from_file_location(
        name,
        path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Unable to load module from {path}"
        )

    module = importlib.util.module_from_spec(spec)

    sys.modules[name] = module

    spec.loader.exec_module(module)

    return module


def main():

    # ------------------------------------------------------------------
    # Integrity before loading
    # ------------------------------------------------------------------

    if sha256(FROZEN_RUNNER) != EXPECTED_RUNNER_SHA256:
        raise RuntimeError(
            "Frozen runner SHA-256 mismatch"
        )

    if (
        sha256(TREATMENT_ADAPTER)
        != EXPECTED_TREATMENT_ADAPTER_SHA256
    ):
        raise RuntimeError(
            "Treatment adapter SHA-256 mismatch"
        )

    # Project root must precede imports performed by frozen runner.
    root_text = str(ROOT)

    if root_text not in sys.path:
        sys.path.insert(0, root_text)

    # ------------------------------------------------------------------
    # Load exact frozen runner and isolated treatment adapter
    # ------------------------------------------------------------------

    frozen_runner = load_module(
        "experiment_B_frozen_e3v3_runner",
        FROZEN_RUNNER,
    )

    treatment_adapter = load_module(
        "experiment_B_structured_adapter",
        TREATMENT_ADAPTER,
    )

    # ------------------------------------------------------------------
    # SINGLE EXPERIMENTAL SUBSTITUTION
    # ------------------------------------------------------------------

    historical_call_json = frozen_runner.call_json

    frozen_runner.call_json = (
        treatment_adapter.call_json_structured
    )

    if (
        frozen_runner.call_json
        is not treatment_adapter.call_json_structured
    ):
        raise RuntimeError(
            "Treatment call_json substitution failed"
        )

    if frozen_runner.call_json is historical_call_json:
        raise RuntimeError(
            "Historical call_json remained active"
        )

    # ------------------------------------------------------------------
    # Delegate CLI execution to frozen runner.
    #
    # No benchmark semantics are implemented here.
    # ------------------------------------------------------------------

    frozen_runner.main()


if __name__ == "__main__":
    main()

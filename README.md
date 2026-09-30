# Deterministic Intent Translation for Network Slicing

This repository contains the implementation, datasets, experiment outputs, analysis artifacts, and reproducibility records for research on **hallucination-resistant deterministic intent translation for network slicing**.

The central idea is to separate probabilistic natural-language interpretation from deterministic validation and enforcement. Natural-language intents are translated into a structured intermediate representation (CIR), while deterministic stages check source constraints, consistency, preservation, schema/semantic validity, capability constraints, and mapping conditions before an executable-oriented descriptor is produced. Unsupported, contradictory, or infeasible requests are intended to be rejected with an explainable failure rather than silently propagated.

> **Research status:** This repository is a research/reproducibility artifact. It is not a production network-slicing orchestrator and does not claim universal hallucination-free operation or formal standards conformance.

## Research Questions

The experiments investigate two closely related questions:

1. How can natural-language network-slicing intents be translated into structured, executable-oriented descriptors while reducing the risk that unsupported or lost information reaches the actuation stage?
2. How much additional failure containment can be obtained by placing deterministic source analysis, preservation, consistency, validation, and capability checks around an LLM-based semantic parser?

## Pipeline

The final experimental architecture can be summarized as:

```text
Natural-language intent
        |
        v
Deterministic source analysis / pre-gates
        |
        v
LLM semantic interpretation
        |
        v
Canonical Intermediate Representation (CIR)
        |
        v
Reconciliation / normalization
        |
        v
Source-to-CIR preservation checks
        |
        v
Deterministic schema / semantic / consistency /
capability / policy validation
        |
        v
Mapping
        |
        +--------------------+
        |                    |
        v                    v
Descriptor             Explainable rejection
```

The design deliberately treats the LLM as a semantic interpretation component rather than the final authority for whether an intent is safe or valid to translate.

## Experimental Sequence

The repository records an incremental experimental program rather than a single benchmark run.

| Experiment | Role |
|---|---|
| **Experiment 1 (E1)** | Controlled feasibility study and information-loss diagnosis |
| **Experiment 2A (E2A)** | Robustness evaluation and failure discovery on more varied intents |
| **Experiment 2B / E3-v2** | Targeted deterministic safeguards and repair/development evidence |
| **E3-v3** | Frozen final implementation evaluated on a held-out benchmark |

These experiments use different benchmark populations and should **not** be interpreted as a conventional learning curve measured repeatedly on one common test set.

## Final Held-Out Result

The frozen E3-v3 evaluation contains **120 held-out cases**. The primary recorded result is:

| Metric | Result |
|---|---:|
| Decision accuracy | **101/120 (84.17%)** |
| Exact 95% CI for accuracy | **76.38%–90.19%** |
| Valid-intent acceptance | **87.93%** |
| Invalid-intent rejection | **80.65%** |
| Rejection F1 | **84.03%** |

The held-out experiment is the primary final evidence in this repository. Development experiments are retained because they document how failure modes were identified and how the deterministic safeguards evolved.

## Repository Layout

The most useful top-level paths are:

```text
.
├── configs/                  # Experiment/configuration profiles
├── data/                     # Experiment 1 datasets
├── src/                      # Core Experiment 1 implementation
├── notebooks/                # Colab/notebook material retained in the archive
├── results/                  # Raw and derived Experiment 1 results
├── analysis/                 # Metrics, statistics, tables and figures
│
├── experiment-2/             # Experiment 2A robustness evaluation
│   ├── configs/
│   ├── data/
│   ├── results/
│   ├── analysis/
│   └── reproducibility/
│
├── experiment-2b/            # E3-v2 and E3-v3 development/final evaluation
│   ├── configs/
│   ├── data/
│   ├── development/
│   ├── failure_analysis/
│   ├── implementation/
│   ├── heldout/
│   └── reproducibility/
│
└── paper_synthesis/          # Cross-experiment and manuscript evidence
    ├── cross_experiment/
    ├── literature_grounding/
    ├── manuscript_blueprint/
    └── manuscript_claim_audit/
```

Some artifacts intentionally appear in both working/result directories and frozen reproducibility directories. The frozen copies and manifests provide provenance for the reported experiments.

## Where to Start

For a quick review of the project, a useful order is:

1. Read this README.
2. Inspect `src/` for the original pipeline components.
3. Review `experiment-2/` for the robustness/failure-discovery experiment.
4. Review `experiment-2b/implementation/e3_v3/` for the later deterministic safeguards.
5. Use `experiment-2b/heldout/` for the final held-out benchmark, official result, metrics, failure analysis, and leakage/integrity audits.
6. Use `experiment-2b/reproducibility/` for frozen implementation/result packages and manifests.
7. Use `paper_synthesis/cross_experiment/` for the cross-experiment evidence inventory and synthesis.

For the final E3-v3 evidence, the following paths are particularly important:

```text
experiment-2b/heldout/results/
experiment-2b/heldout/analysis/
experiment-2b/heldout/audit/
experiment-2b/heldout/post_evaluation_integrity_audit/
experiment-2b/reproducibility/e3v3_complete_implementation_v1.0/
experiment-2b/reproducibility/e3v3_final_experiment_closure_v1.0/
experiment-2b/reproducibility/e3v3_heldout_benchmark_v1.0/
```

## Environment Setup

Clone the repository and create an isolated Python environment:

```bash
git clone https://github.com/chandrasekaranrajendran34/deterministic-intent-translation.git
cd deterministic-intent-translation

python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\\Scripts\\activate      # Windows

pip install --upgrade pip
pip install -r requirements.txt
```

The experiments used the Together API for LLM inference. Supply credentials through an environment variable; **never hard-code or commit an API key**:

```bash
export TOGETHER_API_KEY="your-token-here"
```

For Windows PowerShell:

```powershell
$env:TOGETHER_API_KEY="your-token-here"
```

The repository code expects credentials to be provided at runtime. Historical result files allow many analyses to be inspected without rerunning paid/external model calls.

## Reproducibility Guidance

This repository contains both development history and frozen experimental evidence. If the goal is to reproduce the published/reported result, prefer the frozen artifacts under `reproducibility/` rather than modifying historical development files.

Important principles when working with the archive:

- Do not alter frozen benchmark labels or official result files and then describe them as the original experiment.
- Do not tune E3-v3 against its held-out failures and still treat the modified system as the same held-out evaluation.
- Verify manifest hashes when auditing frozen artifacts.
- Keep new experiments in new directories/versioned artifacts instead of overwriting the recorded runs.
- Record the model, configuration, environment, dataset version, and output hashes for any new run.

Because external model APIs and their serving infrastructure can change, an exact future API rerun is not guaranteed to reproduce every model-generated token or latency measurement. The repository therefore preserves raw results and deterministic/frozen artifacts in addition to executable code.

## Held-Out Integrity

The E3-v3 benchmark was frozen before the official final evaluation. The repository also contains pre-evaluation similarity/leakage checks and a later read-only expanded exposure audit. These artifacts are retained under the held-out audit and reproducibility directories.

The integrity evidence supports a **controlled held-out evaluation within this experimental program**. It should not be interpreted as proof of semantic independence from all possible external data or as evidence of real-world production generalization.

## Interpretation Boundaries

Please use the following boundaries when citing or extending this work:

- The approach is described as **hallucination-resistant**, not hallucination-free.
- Deterministic validators provide failure containment only for the constraints and semantics represented by the implemented checks.
- Controlled benchmark results are not production-network performance measurements.
- Generic logical/capability constraints in the experiments should not automatically be interpreted as formal 3GPP or O-RAN conformance tests.
- The different experimental stages use different datasets and experimental roles.
- E2B is development/repair evidence; E3-v3 is the final frozen held-out evidence.

## Results, Tables, and Figures

Publication-oriented artifacts are available in several locations, including:

```text
analysis/tables/
analysis/figures/
experiment-2b/heldout/analysis/publication_tables/
experiment-2b/heldout/analysis/publication_figures/
experiment-2b/reproducibility/e3v3_final_experiment_closure_v1.0/publication_tables/
experiment-2b/reproducibility/e3v3_final_experiment_closure_v1.0/publication_figures/
```

The repository also preserves failure-taxonomy artifacts so that aggregate accuracy is not the only basis for interpreting the system.

## Extending the Repository

A clean extension should be treated as a new experiment rather than modifying the frozen evidence. Examples include:

- additional intent families;
- broader unsupported-capability detection;
- richer relational and compound-constraint reasoning;
- alternative LLMs;
- external or independently constructed benchmarks;
- stronger standards-grounded capability profiles;
- production/network-emulation evaluation;
- additional explainability and provenance mechanisms.

Create a new versioned dataset, freeze it before final evaluation, record implementation hashes, preserve raw outputs, and keep development data separate from the final held-out benchmark.

## Citation

A formal paper citation can be added here after publication. Until then, if you use this repository, please cite the repository and the corresponding research manuscript when available.

Repository:

```text
https://github.com/chandrasekaranrajendran34/deterministic-intent-translation
```

## License

No software license is asserted by this README. If the repository does not contain a separate `LICENSE` file, the default copyright rules apply. Add an explicit open-source license before encouraging unrestricted reuse or redistribution.

## Contact / Issues

For reproducibility questions, suspected inconsistencies, or proposed extensions, please open a GitHub issue in this repository with the relevant experiment, artifact path, and (where applicable) manifest/hash information.

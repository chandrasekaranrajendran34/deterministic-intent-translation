# Journal Extension Experiments: Experiments A and B

**Project:** Deterministic Intent Translation for Network Slicing\
**Repository extension:** `journal_experiments/`\
**Experimental freeze date:** 2 October 2026\
**Status:** Experimental and consolidation phase complete and frozen

------------------------------------------------------------------------

## 1. Purpose

This document records the journal-extension experiments conducted after
the original Experiment 1, Experiment 2A, and Experiment 2B/E3-v3 work,
and defines the next manuscript-revision phase.

The extension addresses two questions:

1.  **Experiment A --- Multi-model robustness:** How does decision
    performance vary when the semantic-parser model changes while the
    deterministic validation and failure-containment pipeline remains
    fixed?
2.  **Experiment B --- Schema-constrained decoding:** Is provider-side
    structural constrained generation sufficient to prevent semantic
    failures such as dropped constraints, unsupported requirements,
    mis-mapping, or incorrect acceptance?

A separate B-E3 experiment is retained as supplementary evidence. C1-C6
consolidate the frozen experimental evidence, publication tables,
claim-evidence mapping, and final reproducibility records.

The supported framing is **hallucination-resistant intent translation**
and **deterministic failure containment under tested constraints**. The
evidence does not establish hallucination-free operation, universal
model independence, arbitrary-model guarantees, formal 3GPP/O-RAN
conformance, or zero deployment risk.

------------------------------------------------------------------------

## 2. Repository Placement

Place the new material at the repository root:

``` text
deterministic-intent-translation/
├── README.md
├── analysis/
├── configs/
├── experiment-2/
├── experiment-2b/
├── ...
├── README_A_B_Journal_experiments.md
└── journal_experiments/
    ├── experiment_A_model_sweep/
    ├── experiment_B_review_requested_constrained_decoding/
    ├── experiment_B_schema_constrained_decoding/
    └── journal_final_evidence/
```

The journal experiments remain separate from `experiment-2b/`, which
contains the frozen E3-v3 implementation, benchmark, official run,
analysis, and reproducibility packages.

Do not commit generated Python caches. Recommended `.gitignore` entries:

``` gitignore
__pycache__/
*.py[cod]
.ipynb_checkpoints/
.env
.env.*
```

------------------------------------------------------------------------

# 3. Experiment A --- Multi-Model Robustness

## 3.1 Objective

Experiment A varies the semantic-parser model while retaining the frozen
E3-v3 benchmark and deterministic validation/failure-containment
architecture.

Frozen benchmark: **120 cases --- 58 valid and 62 invalid**.

## 3.2 Evaluable Arms

  --------------------------------------------------------------------------------------------------------
  Arm       Model                                         Accuracy          VAR          IRR   Containment
                                                                                                Violations
  --------- ----------------------------------------- ------------ ------------ ------------ -------------
  A1        Qwen/Qwen3.5-9B                                 84.17%       87.93%       80.65%             0

  A2        meta-llama/Llama-3.3-70B-Instruct-Turbo         83.33%       82.76%       83.87%             0

  A7        arize-ai/qwen-2-1.5b-instruct                   60.00%       18.97%       98.39%             0

  A8        Prism-ML/Ternary-Bonsai-27B                     75.83%       70.69%       80.65%             0

  A9        deepseek-ai/DeepSeek-V4.1-Flash                 84.17%       87.93%       80.65%             0

  A10       openai/gpt-oss-120b                             74.17%       65.52%       82.26%             0
  --------------------------------------------------------------------------------------------------------

Observed ranges:

-   Accuracy: **60.00%-84.17%**, spread **24.17 pp**
-   VAR: **18.97%-87.93%**, spread **68.96 pp**
-   IRR: **80.65%-98.39%**, spread **17.74 pp**
-   Containment violations: **0 in every evaluable arm**

Paper-safe statement:

> Across six evaluable semantic-parser models tested on the frozen
> 120-case benchmark, decision accuracy ranged from 60.00% to 84.17%,
> while the deterministic failure-containment mechanism produced zero
> observed containment violations in every evaluable arm.

This is empirical evidence for the evaluated models and benchmark, not a
universal proof of model independence.

## 3.3 Provenance

The original A1-A6 preregistration and the availability-screened
prospective A7-A10 extension should remain distinguishable. Some planned
models did not have accessible serverless endpoints.

A Colab reset caused loss of some ephemeral Experiment A raw evidence.
Lost evidence was **not reconstructed by rerunning experiments**.
Recovery/persistence artifacts document this limitation.

## 3.4 Key Artifacts

``` text
journal_experiments/experiment_A_model_sweep/
├── logs/
├── manifests/
├── preregistration/
├── recovery/
└── results/
    ├── analysis/
    ├── metrics/
    └── raw/
```

Final Experiment A freeze SHA-256:

`667cfd8b1e693c0ba2f7107a877c695181b273985adc976e43f124313e8d892a`

------------------------------------------------------------------------

# 4. Experiment B --- Reviewer-Requested Constrained Decoding

## 4.1 Objective and Treatment

This is the experiment that directly satisfies the reviewer-requested
constrained-decoding comparison on **E1 (50 cases) and E2A (200
cases)**.

Treatment:

-   Qwen/Qwen3.5-9B
-   reasoning disabled
-   temperature 0
-   historical CIR prompt/user formulation
-   historical downstream CIR validation/mapping/descriptor logic
-   provider-side structural JSON-schema constrained generation as the
    intended change

The provider schema requires the seven CIR keys/types and disallows
additional properties. It does not impose semantic enum/range
constraints.

## 4.2 E1 Results

  Metric                         Result
  ------------------- -----------------
  Accuracy                       94.00%
  VAR                           100.00%
  IRR                            88.00%
  TP / FP / FN / TN     22 / 0 / 3 / 25
  Parse success                 50 / 50

Three hallucination-probe cases remained accepted as URLLC.

A bounded search did not locate a historical E1 result table; therefore
no historical E1 comparison should be invented.

## 4.3 E2A Results

  Metric       Constrained   Historical CIR
  ---------- ------------- ----------------
  Accuracy          73.00%           75.50%
  VAR               93.00%           96.00%
  IRR               53.00%           55.00%

Constrained confusion matrix: **TP/FP/FN/TN = 53/7/47/93**.

The constrained treatment produced **200/200 parseable outputs**.
Downstream `schema_valid` was **185/200 (92.5%)**, illustrating that
provider-side structural validity and downstream semantic/range validity
are different.

Constrained-minus-historical deltas:

-   Accuracy: **-2.5 pp**
-   VAR: **-3.0 pp**
-   IRR: **-2.0 pp**

Paired correctness:

``` text
Both correct       : 144
Constrained only   :   2
Historical only    :   7
Both wrong         :  47
McNemar exact p    : 0.1796875
```

The observed E2A accuracy difference was not statistically significant
at the conventional 0.05 level.

## 4.4 Unsupported-Requirement Forensics

  Outcome                       Cases   Percentage
  --------------------------- ------- ------------
  Dropped from CIR                 17       70.83%
  Mapped to supported field         3       12.50%
  Preserved as text                 4       16.67%
  Other                             0           0%

All **24/24** unsupported-requirement cases were ultimately accepted.

Further observations:

-   20/24 constrained CIR dictionaries were semantically identical to
    historical CIR.
-   24/24 had the same final acceptance outcome as historical CIR.
-   47/100 invalid E2A cases were accepted by the constrained treatment.
-   54/200 cases were structurally valid but decision-wrong.

The forensic classifier is specific to the frozen synthetic benchmark
and is not a general semantic-equivalence detector.

Paper-safe statement:

> On the frozen E2A benchmark, structural constrained decoding produced
> fully parseable outputs but did not improve decision accuracy relative
> to the historical CIR control and did not eliminate semantic omission,
> mis-mapping, or unsupported-requirement acceptance. These results
> support retaining deterministic semantic validation beyond
> provider-side structural decoding.

The historical CIR control is not the complete proposed pipeline and
does not include the deterministic input audit.

## 4.5 Key Artifacts

``` text
journal_experiments/experiment_B_review_requested_constrained_decoding/
├── analysis/
├── capability_probe/
├── final/
├── implementation/
├── logs/
├── manifests/
├── preregistration/
└── results/
    ├── E1/
    └── E2A/
```

Final B-Review freeze SHA-256:

`63fa99c81477eb7d2c3136b67f72ac3d4673f7d081d7b332ef8d634c68faf3dd`

------------------------------------------------------------------------

# 5. B-E3 --- Supplementary Structured-Generation Experiment

B-E3 is a separate supplementary experiment on the frozen 120-case E3-v3
benchmark. It does **not** replace the reviewer-requested E1/E2A
Experiment B.

  Metric                                    Result
  ----------------------------- ------------------
  Accuracy                                  84.17%
  VAR                                       87.93%
  IRR                                       80.65%
  TP / FP / FN / TN               50 / 7 / 12 / 51
  LLM invoked                             77 / 120
  Parse success among invoked              77 / 77
  Pre-LLM/no-call cases                   43 / 120
  Accepted/descriptors                    63 / 120

Rejection-stage counts: accepted 63; source gate 24; constraint
consistency 14; CIR validation 12; qualitative source gate 5;
preservation 2.

The historical and B-E3 cleaner implementations differ at source level.
A corrected retrospective diagnostic found identical cleaning behavior
on all **77 observed B-E3 LLM responses**. This is a bounded
retrospective observation, not universal implementation equivalence.

Key directory:

``` text
journal_experiments/experiment_B_schema_constrained_decoding/
```

Final B-E3 freeze SHA-256:

`e3e5dee967eeb233f1e583624d204b26c648040938715d41ff7cd4102d6d77bb`

------------------------------------------------------------------------

# 6. C1-C6 --- Journal Final Evidence Package

Directory:

``` text
journal_experiments/journal_final_evidence/
```

C1-C6 consolidate frozen evidence; they are not additional model
experiments.

## C1 --- Frozen Evidence Inventory

Artifact:

`inventory/C1_frozen_evidence_inventory_v1.json`

SHA-256:

`550446bdd7f70481e0eb1a512af4e8d3fddb62eec7272f227d1c192514e7ced2`

## C2 --- B-E3 Closure

Key SHA-256 values:

-   Case analysis:
    `6663345076357ffae72e95fb9dc71da701161feee9ae03b7c217ba39237c9e5c`
-   Results table:
    `10e0599c30630c6bfa6523be546bff50ffea2489aa04c380355f5802c229d403`
-   Summary:
    `89842933a3db43cdc447a350838a92ed32a5c1b40f129a84bc1433a4e5691bab`
-   Final freeze:
    `e3e5dee967eeb233f1e583624d204b26c648040938715d41ff7cd4102d6d77bb`

## C3 --- Master Frozen-Evidence Manifest

`manifests/journal_master_frozen_evidence_manifest_v1.json`

SHA-256:

`80555895d6b3c3c877455f252c9924ad7c7d35d68ebcc8bed1f74f9622d1884c`

## C4 --- Publication Tables

``` text
publication_tables/
├── Table_C4_T1_experiment_A_model_robustness.csv
├── Table_C4_T2_B_review_constrained_results.csv
├── Table_C4_T3_E2A_constrained_vs_historical_CIR.csv
├── Table_C4_T4_E2A_paired_correctness.csv
├── Table_C4_T5_unsupported_requirement_forensics.csv
└── Table_C4_T6_B_E3_supplementary.csv
```

C4 manifest SHA-256:

`b5dde308ca53757a48ba9e14fe34551855fdecd7eda5ee2dd74d30c371532eca`

## C5 --- Paper-Ready Evidence

``` text
paper_ready/
├── C5_paper_ready_results_discussion_v1.md
└── C5_claim_evidence_map_v1.json
```

SHA-256:

-   Results/discussion:
    `dc340dbd24d4dd3c817b10ca95c5711c5a5833cd255ab726cbcd82652f47fe49`
-   Claim-evidence map:
    `356c4a9de1d5387fa1d95af08743d1b001cdeb05d0757bbdc98f3361dbe1d56e`
-   C5 manifest:
    `464c863d070ef29b2308e5cecbce15d45772e2793bb5a212c6322b596f9d558f`

## C6 --- Final Reproducibility Freeze

``` text
reproducibility/
├── README_FINAL_REPRODUCIBILITY_FREEZE.md
└── journal_FINAL_reproducibility_index_v1.json

manifests/
└── journal_FINAL_REPRODUCIBILITY_FREEZE_v1.json
```

  --------------------------------------------------------------------------------------------------------
  Artifact                            SHA-256
  ----------------------------------- --------------------------------------------------------------------
  Final reproducibility index         `4f41c6656f0d836b03991c67046c56e64a55013564c13a7216008b72e3cb8402`

  Final reproducibility README        `405219d333ff8c3a645dbd7a83883b44ad4c5f1f618b51cd1385c61ed55bf3a6`

  Final reproducibility freeze        `cf90834784d91f0937944fded6493b195a4b81923e09b705c0b45b66b6cc2187`
  --------------------------------------------------------------------------------------------------------

Final status:

``` text
Experiment A       FINAL_FROZEN
B-Review           FINAL_FROZEN
B-E3               FINAL_FROZEN / SUPPLEMENTARY
C1-C5              COMPLETE
C6                 FINAL REPRODUCIBILITY FREEZE
Experimental phase CLOSED
```

C6 involved zero API/model calls, zero benchmark executions, zero
experiment reruns, zero new statistical tests, and zero new scientific
results.

------------------------------------------------------------------------

# 7. Evidence Hierarchy and Claim Boundaries

## Primary new evidence

-   **Experiment A:** multi-model robustness.
-   **B-Review:** reviewer-requested E1/E2A constrained-decoding
    evaluation.

## Supplementary evidence

-   **B-E3:** structured-generation evaluation on frozen E3-v3.

## Consolidation/reproducibility evidence

-   **C1-C6:** inventory, consolidation, publication tables, paper-ready
    evidence, and final reproducibility freeze.

Supported language includes:

-   hallucination-resistant intent translation
-   deterministic failure containment under defined/tested constraints
-   semantic-parser performance varied substantially across evaluated
    models
-   zero observed containment violations across six evaluable Experiment
    A arms
-   structural constrained decoding produced parseable structured
    outputs
-   structural validity did not eliminate semantic omission,
    mis-mapping, or unsupported-requirement acceptance

Avoid:

-   hallucination-free
-   universal guarantee
-   universal model independence
-   arbitrary-model guarantee
-   zero-risk
-   formal 3GPP/O-RAN conformance
-   universal cleaner equivalence
-   causal model-size/architecture conclusions
-   inferring A1/A9 case-level identity from equal aggregate metrics

------------------------------------------------------------------------

# 8. Manuscript Revision Roadmap --- M1 to M9

The experimental phase remains frozen. M1-M9 consume frozen evidence
rather than regenerate it.

## M1 --- Manuscript Baseline Audit

**Objective:** establish the exact pre-revision manuscript baseline.

Tasks:

1.  Preserve the current manuscript source as a baseline copy.
2.  Record version/date, page count, bibliography count, and
    table/figure inventory.
3.  Locate claims concerning model independence, hallucination
    resistance, structured output, deterministic containment,
    generalization, and E1/E2A/E3-v3.
4.  Identify affected sections: Abstract, Introduction, Contributions,
    Methodology, Experimental Setup, Results, Discussion, Limitations,
    and Conclusion.
5.  Cross-check existing numerical claims against frozen authoritative
    artifacts.
6.  Do not silently replace historical values with journal-extension
    results.

**Deliverable:** manuscript baseline and claim-location audit.

## M2 --- Integrate Experiment A

**Objective:** add the six-model robustness experiment with bounded
interpretation.

Tasks:

1.  Describe the frozen benchmark/pipeline and varied semantic model.
2.  Document original preregistered arms versus the prospective
    availability-screened extension.
3.  Add the six-model table.
4.  Report Accuracy, VAR, IRR ranges and zero observed containment
    violations.
5.  Discuss the **68.96 pp VAR spread**.
6.  Explain semantic-model-dependent decision quality versus observed
    containment stability.
7.  Transparently disclose the Colab-reset/lost-raw-evidence limitation.

**Deliverable:** Experiment A methodology, results, table, and
discussion.

## M3 --- Integrate Reviewer-Requested Experiment B

**Objective:** incorporate the exact E1/E2A constrained-decoding
experiment.

Tasks:

1.  Define structural constrained decoding precisely.
2.  Explain structural versus semantic/range constraints.
3.  Add E1 results.
4.  Add E2A results and historical CIR comparison.
5.  Add paired correctness counts.
6.  Report McNemar exact `p = 0.1796875`.
7.  Explain 200/200 parse success versus 185/200 downstream
    schema-valid.
8.  State that the accuracy difference was not statistically
    significant.
9.  Do not invent a historical E1 comparison.

**Deliverable:** Experiment B methodology/results subsection and
comparison tables.

## M4 --- Add Semantic-Failure Analysis

**Objective:** demonstrate why structural validity is insufficient for
semantic correctness.

Tasks:

1.  Add the 24 unsupported-requirement forensic cases.
2.  Report dropped 17, mapped 3, preserved-as-text 4.
3.  State all 24 were accepted.
4.  Report 20/24 semantically identical CIR dictionaries and 24/24 same
    final acceptance as historical.
5.  Report 47/100 invalid cases accepted and 54/200 structurally valid
    but decision-wrong.
6.  Connect these failures to preservation checks and deterministic
    semantic/policy validation.
7.  State that the forensic classifier is benchmark-specific.

**Deliverable:** semantic-failure analysis subsection.

## M5 --- Integrate B-E3 as Supplementary Evidence Only

**Objective:** preserve B-E3 without conflating it with the
reviewer-requested experiment.

Tasks:

1.  Label B-E3 explicitly as supplementary.
2.  Report Accuracy 84.17%, VAR 87.93%, IRR 80.65%.
3.  Report 77/77 parse success among invoked cases and 43 pre-LLM
    decisions.
4.  Document cleaner source difference and observed 77-response
    behavioral equivalence.
5.  Do not claim universal cleaner equivalence.
6.  Do not present B-E3 as satisfying the E1/E2A reviewer request.
7.  Move detailed material to an appendix/supplement if space requires.

**Deliverable:** concise supplementary subsection or appendix.

## M6 --- Rewrite Results and Discussion

**Objective:** create one coherent scientific narrative.

Recommended flow:

1.  Frozen E3-v3 baseline effectiveness.
2.  Experiment A model sensitivity.
3.  Observed deterministic containment stability.
4.  Experiment B structural-versus-semantic validity.
5.  Unsupported-requirement failure mechanisms.
6.  Architectural implication: probabilistic interpretation separated
    from deterministic validation.
7.  Statistical interpretation of the E2A comparison.
8.  Limitations and threats to validity.

Use the frozen C5 paper-ready package and claim-evidence map as starting
evidence. Do not recalculate frozen results.

**Deliverable:** revised Results and Discussion with traceable
quantitative claims.

## M7 --- Revise Abstract, Contributions, Introduction, and Conclusion

**Objective:** align the manuscript's high-level claims with the
strengthened evidence.

### Abstract

Include:

-   hallucination-resistant/deterministic framing;
-   six evaluable semantic parsers;
-   observed accuracy range;
-   zero observed containment violations under Experiment A conditions;
-   finding that structural constrained decoding did not resolve
    semantic failures.

### Contributions

Recommended contribution structure:

1.  Deterministic architecture separating probabilistic semantic
    interpretation from deterministic validation/failure containment.
2.  Frozen benchmark evaluation and failure analysis.
3.  Six-model robustness experiment showing model-dependent decision
    variation with zero observed containment violations across evaluated
    arms.
4.  Controlled constrained-decoding experiment showing structural
    constraints alone do not eliminate semantic failures.
5.  Reproducibility and claim-evidence artifacts.

### Introduction/Conclusion

Emphasize the distinction between output fluency/structure and
operational semantic validity. Conclude only that deterministic
validation contributes to tested failure containment, semantic parsing
remains model-sensitive, and structured generation is insufficient as a
replacement for semantic validation.

**Deliverable:** revised front matter, contributions, conclusion, and
future work.

## M8 --- Prepare Reviewer Response

**Objective:** make every requested change easy to verify.

For each reviewer concern:

1.  State the concern.
2.  State the change made.
3.  Identify manuscript section/table/page.
4.  Report the key result.
5.  State the bounded interpretation.

Use **Experiment A** for the model-variation concern and **B-Review
E1/E2A** for the constrained-decoding concern. B-E3 remains
supplementary.

Suggested format:

``` text
Reviewer comment:
[concise concern]

Response:
We added ...

Changes in manuscript:
Section X, Table Y, pages ...

Key result:
...

Interpretation:
...
```

**Deliverable:** point-by-point reviewer response.

## M9 --- Final Submission Audit

**Objective:** verify scientific, numerical, reproducibility, and
formatting consistency.

### Numerical audit

Verify:

-   Experiment A model metrics and 68.96 pp VAR spread
-   Experiment B E1/E2A metrics
-   historical E2A CIR metrics
-   McNemar p-value
-   unsupported-requirement counts
-   B-E3 supplementary metrics

### Claim audit

Search for:

``` text
hallucination-free
guarantee
guaranteed
model-independent
universal
zero-risk
formal conformance
3GPP compliant
O-RAN compliant
```

Remove, qualify, or substantiate every occurrence appropriately.

### Role audit

Confirm:

-   Experiment A = multi-model robustness
-   B-Review = reviewer-requested constrained decoding
-   B-E3 = supplementary
-   C1-C6 = consolidation/reproducibility

### Reproducibility audit

Confirm paths, hashes, manifests, absence of caches/credentials, honest
disclosure of lost raw evidence, and no reconstruction by rerunning
experiments.

### Formatting audit

Check journal template, tables/figures, abbreviations, references/DOIs,
page limits, supplementary references, captions, cross-references,
equations, and symbols.

### Scientific audit

Every major conclusion should trace to a frozen artifact through the
claim-evidence map.

**Deliverable:** submission-ready manuscript, reviewer response,
reproducibility package, and final audit checklist.

------------------------------------------------------------------------

# 9. Recommended Manuscript Work Order

``` text
M1  Manuscript baseline audit
 ↓
M2  Integrate Experiment A
 ↓
M3  Integrate reviewer-requested Experiment B
 ↓
M4  Add semantic-failure analysis
 ↓
M5  Integrate B-E3 as supplementary evidence
 ↓
M6  Rewrite Results and Discussion
 ↓
M7  Revise Abstract / Contributions / Introduction / Conclusion
 ↓
M8  Prepare reviewer response
 ↓
M9  Final submission audit
```

No frozen A/B/C artifact should be modified while performing M1-M9.

------------------------------------------------------------------------

# 10. Repository Navigation

Original frozen E3-v3 work:

``` text
experiment-2b/reproducibility/
```

Journal-extension experiments:

``` text
journal_experiments/
```

Final evidence package:

``` text
journal_experiments/journal_final_evidence/
```

Paper-ready evidence:

``` text
journal_experiments/journal_final_evidence/paper_ready/
```

Final reproducibility records:

``` text
journal_experiments/journal_final_evidence/reproducibility/
```

------------------------------------------------------------------------

# 11. Final Status

``` text
Experiment A       FINAL_FROZEN
B-Review           FINAL_FROZEN
B-E3               FINAL_FROZEN / SUPPLEMENTARY
C1-C5              COMPLETE
C6                 FINAL REPRODUCIBILITY FREEZE

Experimental/consolidation phase: COMPLETE
Current phase: MANUSCRIPT REVISION — M1 through M9
```

The repository should continue to distinguish historical experiments,
new journal experiments, supplementary experiments, evidence
consolidation, and manuscript-revision artifacts. This separation
preserves the provenance and interpretation boundaries of the frozen
scientific evidence.

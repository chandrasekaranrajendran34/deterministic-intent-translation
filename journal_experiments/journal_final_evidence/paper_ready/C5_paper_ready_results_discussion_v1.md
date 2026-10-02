# C5 Paper-Ready Results and Discussion Evidence Package

## Scope

This document converts the frozen journal-experiment evidence into publication-ready prose. It does not introduce new experiments, new statistical tests, or new scientific observations. Experiment A evaluates cross-model behavior of the frozen deterministic pipeline, B-Review is the reviewer-requested constrained-decoding experiment on E1 and E2A, and B-E3 is retained only as a supplementary E3-v3 follow-up.

## Cross-model robustness of deterministic failure containment

To examine whether the observed behavior depended on a single semantic parser, the frozen E3-v3 benchmark was evaluated with six accessible model arms while preserving the deterministic downstream pipeline. Decision accuracy varied substantially across the evaluable models, ranging from 60.00% to 84.17% (spread 24.17 percentage points). The valid-acceptance rate ranged from 18.97% to 87.93% (spread 68.96 percentage points), while the invalid-rejection rate ranged from 80.65% to 98.39% (spread 17.74 percentage points).

Despite this variation in decision performance, zero containment violations were observed in every one of the six evaluable model arms. This result separates two properties of the architecture: semantic interpretation quality remained model dependent, whereas the tested deterministic downstream containment boundary remained stable across the evaluated arms. The result should therefore be interpreted as empirical cross-model evidence under the frozen benchmark and evaluated models, rather than as a universal guarantee of model independence.

## Reviewer-requested constrained-decoding experiment

The reviewer-requested constrained-decoding experiment evaluated the CIR-constrained configuration on the frozen E1 and E2A benchmarks. On E1 (n=50; 25 valid and 25 invalid requests), constrained decoding achieved 94.00% decision accuracy, a 100.00% valid-acceptance rate, and an 88.00% invalid-rejection rate. The corresponding confusion counts were TP=22, FP=0, FN=3, and TN=25, where the positive class denotes an invalid request that was rejected.

On E2A (n=200; 100 valid and 100 invalid requests), the constrained configuration achieved 73.00% decision accuracy, a 93.00% valid-acceptance rate, and a 53.00% invalid-rejection rate. The corresponding counts were TP=53, FP=7, FN=47, and TN=93.

## Constrained decoding versus the historical CIR configuration

On the same frozen E2A benchmark, the historical CIR configuration achieved 75.50% decision accuracy, a 96.00% valid-acceptance rate, and a 55.00% invalid-rejection rate. The constrained configuration therefore differed by -2.50 percentage points in accuracy, -3.00 percentage points in valid acceptance, and -2.00 percentage points in invalid rejection.

The paired correctness analysis showed that both configurations were correct on 144 cases and both were wrong on 47 cases. The constrained configuration alone was correct on 2 cases, whereas the historical CIR configuration alone was correct on 7 cases. The exact McNemar test yielded p=0.1796875. Accordingly, the frozen comparison does not provide evidence that structural constrained decoding improved decision accuracy, and the observed paired difference should not be described as statistically significant.

## Why structural constrained decoding is insufficient for semantic safety

The E2A forensic analysis provides a more direct explanation of this result. Among 24 requests containing unsupported requirements, all 24 were ultimately accepted by the CIR-constrained branch. Of these unsupported requirements, 17/24 (70.83%) were dropped from the generated CIR, 3/24 (12.50%) were mapped into a supported field, and 4/24 (16.67%) were preserved as free text. No case remained in the residual other/ambiguous category.

More broadly, 47 of the 100 invalid E2A requests were accepted, and 54 of the 200 cases were structurally valid yet decision-wrong. These observations distinguish structural output control from semantic preservation and policy correctness. Provider-side constrained generation can control the form of an LLM response, but structural validity alone does not establish that every source requirement has been preserved, correctly mapped, or semantically validated.

This distinction supports the architectural separation used in the proposed pipeline. The LLM is responsible for probabilistic semantic extraction, whereas deterministic source analysis, preservation checks, semantic validation, consistency checks, and policy/catalog gates remain responsible for deciding whether the interpreted request is safe to translate into an actionable descriptor.

## Supplementary E3-v3 structured-generation result

The supplementary B-E3 experiment provides an additional observation on the frozen 120-case E3-v3 benchmark. The structured-generation treatment achieved 84.17% decision accuracy, an 87.93% valid-acceptance rate, and an 80.65% invalid-rejection rate. Of the 120 cases, 77 reached the LLM and all 77 parsed successfully; the remaining 43 cases were handled without invoking the LLM and therefore have parse status N/A rather than parse failure.

The B-E3 result is supplementary and is not used as a substitute for the reviewer-requested E1/E2A constrained-decoding experiment. In addition, the frozen B-E3 result schema did not contain a separate `schema_valid` metric, so no such value is inferred or reported.

A retrospective implementation check found that the historical and B-E3 JSON-cleaning functions were not source- or AST-identical. After correcting the diagnostic execution environment, however, both cleaners produced identical cleaned text and identical parsed JSON on all 77 actually observed B-E3 LLM outputs. This finding is limited to those frozen responses and should not be interpreted as a universal equivalence proof for arbitrary model outputs.

## Overall interpretation

Taken together, the experiments support a bounded conclusion. Semantic-parser choice can materially change decision performance, as demonstrated by the wide cross-model variation in Experiment A. Structural constrained decoding improves control over output form but, in the frozen E2A evaluation, did not recover semantic requirements that were omitted or incorrectly represented and did not improve decision accuracy relative to the historical CIR configuration.

The results therefore support retaining deterministic validation after probabilistic intent interpretation. Under the tested architecture, the semantic parser proposes a structured interpretation, while deterministic gates determine whether that interpretation is sufficiently complete, consistent, policy-compliant, and supported to proceed. The evidence supports describing this design as hallucination-resistant through deterministic failure containment under defined constraints; it does not support claims of hallucination-free operation, universal model independence, zero risk, or formal 3GPP/O-RAN conformance.

## Paper-safe key result statements

1. Across six evaluable semantic-parser models on the frozen 120-case benchmark, decision accuracy ranged from 60.00% to 84.17%, while zero containment violations were observed in every evaluated arm.

2. On frozen E2A, the constrained CIR configuration achieved 73.00% accuracy compared with 75.50% for the historical CIR configuration; the paired exact McNemar test was p=0.1796875.

3. All 24 E2A requests containing unsupported requirements were accepted by the CIR-constrained branch: 17 requirements were dropped, 3 were mapped to supported fields, and 4 were retained as free text.

4. The constrained-decoding results show that structural output control does not by itself ensure source-requirement preservation or semantic validity.

5. These results support retaining deterministic source analysis, preservation checks, semantic validation, consistency checks, and policy/catalog gates after LLM-based semantic interpretation.

## Claims explicitly excluded

The frozen evidence does not establish that the system is hallucination-free, universally model-independent, universally safe, formally verified for arbitrary inputs, or formally conformant with 3GPP or O-RAN standards. B-E3 is supplementary and must not be represented as the experiment requested by the reviewer.

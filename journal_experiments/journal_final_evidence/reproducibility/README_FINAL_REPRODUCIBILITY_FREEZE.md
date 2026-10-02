# Final Reproducibility Freeze

## Status

The journal experimental and evidence-consolidation phase is FINAL FROZEN.

No further model-running experiment is required for the current reviewer-response plan.

## Frozen evidence streams

1. Experiment A — multi-model robustness and deterministic failure-containment evidence.
2. B-Review — reviewer-requested constrained-decoding experiment on frozen E1 and E2A.
3. B-E3 — supplementary structured-generation follow-up on frozen E3-v3.

B-E3 must remain explicitly supplementary and must not be represented as the reviewer-requested Experiment B.

## Consolidation chain

- C1 — frozen evidence inventory
- C2 — B-E3 analytic closure
- C3 — master frozen-evidence consolidation
- C4 — publication-table derivation
- C5 — paper-ready Results/Discussion evidence package
- C6 — final reproducibility freeze

## Final scientific boundaries

The evidence supports describing the architecture as hallucination-resistant through deterministic failure containment under defined constraints.

The evidence does not establish:

- hallucination-free operation;
- universal model independence;
- universal safety;
- zero risk;
- a formal arbitrary-input guarantee;
- formal 3GPP or O-RAN conformance;
- universal equivalence of the historical and B-E3 cleaner implementations.

## Statistical interpretation

For the frozen E2A paired comparison, the constrained CIR configuration achieved 73.00% accuracy and the historical CIR configuration achieved 75.50% accuracy. The exact paired McNemar test was p=0.1796875. The result should therefore be described as showing no observed improvement from constrained decoding in this comparison, not as a statistically significant degradation.

## Experiment A interpretation

Across the six evaluable model arms, decision accuracy ranged from 60.00% to 84.17%. Zero containment violations were observed in every evaluated arm. This is empirical evidence under the tested models and frozen benchmark, not a universal model-independence guarantee.

## Structural decoding interpretation

Provider-side structural constrained generation controls output form but does not by itself establish source-requirement preservation, semantic validity, policy correctness, or supported actionability.

In the frozen E2A forensic analysis, all 24 unsupported-requirement cases were accepted by the CIR-constrained branch: 17 were dropped, 3 were mapped into supported fields, and 4 were preserved as free text.

## Reproducibility index

SHA-256: `4f41c6656f0d836b03991c67046c56e64a55013564c13a7216008b72e3cb8402`

## Allowed next work

After this freeze, work should be limited to read-only use of the frozen evidence for:

- manuscript revision;
- publication-table formatting;
- figure preparation;
- reviewer-response drafting;
- supplementary-material preparation;
- reproducibility documentation.

No frozen experimental artifact should be modified or silently replaced.

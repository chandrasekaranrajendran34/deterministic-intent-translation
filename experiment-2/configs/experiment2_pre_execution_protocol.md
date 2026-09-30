# Experiment 2 Pre-Execution Protocol

## Objective

Evaluate whether the intent-translation architecture generalizes beyond
the controlled Experiment 1 benchmark to linguistically diverse,
compound, implicit, and adversarial intent formulations.

## Research Questions

RQ1:
How accurately do E1, E2, and E3 distinguish valid from invalid
network-slicing intents on diverse unseen formulations?

RQ2:
To what extent does deterministic validation prevent invalid intents
from reaching mapping and descriptor compilation?

RQ3:
Can independent validation of the original request identify unsupported
information omitted or transformed during CIR generation?

RQ4:
How robust are the pipelines to implicit unsupported requirements,
compound constraints, boundary conditions, contradictions, and
adversarial instructions?

## Hypotheses

H1:
E3 will reject a larger proportion of invalid/challenging intents than
E2 when unsupported information is omitted during CIR generation.

H2:
E3 will prevent invalid requests detected by its deterministic safeguards
from reaching mapping and descriptor compilation.

H3:
E3 will preserve a high valid-intent acceptance rate while applying
additional deterministic rejection mechanisms.

H4:
Local deterministic processing cost will remain small relative to remote
LLM inference latency.

## Dataset

200 intents total.

100 valid.
100 invalid/challenging.

The dataset will be frozen before the full experiment.

## Pipelines

E1: Direct LLM generation.

E2: LLM -> CIR -> deterministic CIR validation -> mapping -> descriptor.

E3: LLM -> CIR plus independent original-input audit -> deterministic
validation -> mapping -> descriptor.

## Important Experimental Constraint

The Experiment 1 E3 input-audit implementation will not be modified
before Experiment 2A execution.

This prevents adapting the detector to failures observed in the new
benchmark.

## Primary Outcomes

- Decision accuracy
- Invalid rejection precision
- Invalid rejection recall
- Invalid rejection F1
- Valid acceptance rate
- Invalid containment rate
- Service classification accuracy for comparable pipelines
- Mapping eligibility
- Descriptor generation
- End-to-end latency

## Statistical Analysis

- Exact binomial confidence intervals
- Paired correctness comparison
- Category-level failure analysis
- Paired latency analysis
- Effect sizes
- Deterministic processing microbenchmark

## Interpretation Rule

Perfect observed benchmark performance will not be interpreted as
universal correctness, hallucination freedom, prompt-injection immunity,
or formal standards compliance.

# IEEE Manuscript Blueprint

## Working Title

**Deterministic Intent Translation for 3GPP- and O-RAN-Aligned Network
Slicing: A Hallucination-Resistant Pipeline**

## Core Argument

Natural-language intent translation for network slicing should not allow
probabilistic semantic extraction to directly determine executable actions.
The proposed architecture therefore separates probabilistic interpretation
from deterministic source analysis, consistency checking, preservation,
validation, capability enforcement, and descriptor mapping.

The paper evaluates whether these deterministic safeguards provide
failure containment around probabilistic intent extraction within a defined
closed-world capability profile.

## Evidence Hierarchy

The experiments have distinct methodological roles:

- **E1:** controlled feasibility and information-loss diagnosis.
- **E2A:** robustness evaluation and failure discovery.
- **E2B:** targeted repair and development evidence.
- **E3-v3:** final frozen held-out evidence.

The experiments use different benchmark populations. Their accuracy values
must not be presented as a common-test-set learning curve.

## Primary Final Result

The primary paper result is the frozen E3-v3 held-out evaluation:

- Correct decisions: **101/120**
- Decision accuracy: **84.17%**
- Exact 95% CI: **76.38–90.19%**
- Valid-intent acceptance: **51/58 = 87.93%**
- Invalid-intent rejection: **50/62 = 80.65%**
- Rejection precision: **50/57 = 87.72%**
- Rejection recall: **50/62 = 80.65%**
- Rejection F1: **84.03%**

## Mandatory Claim Boundaries

The manuscript may describe the architecture as:

- hallucination-resistant;
- deterministic failure containment;
- source-aware;
- standards-aligned or standards-oriented;
- evaluated on a frozen controlled held-out benchmark.

The manuscript must **not** claim:

- hallucination-free operation;
- universal semantic correctness;
- formal 3GPP/O-RAN conformance;
- external real-world generalization;
- production-network performance;
- a common-test-set learning curve across E1, E2A, E2B, and E3-v3.

## Manuscript Structure

The main paper uses 22 structural entries:

1. Title
2. Abstract
3. I. Introduction
4. II-A. Intent-Based Network and Slice Management
5. II-B. LLM/AI-Based Intent Translation
6. II-C. Research Gap
7. III-A. Design Principles
8. III-B. Source Analysis and Pre-LLM Guards
9. III-C. CIR Extraction and Reconciliation
10. III-D. Preservation, Validation and Mapping
11. IV-A. Evaluation Sequence
12. IV-B. Metrics and Statistical Analysis
13. IV-C. Held-Out Benchmark and Integrity Controls
14. V-A. Development Evidence: E1 and E2A
15. V-B. Targeted Repair Evidence: E2B
16. V-C. Final E3-v3 Held-Out Evaluation
17. V-D. Residual Failure Analysis
18. VI-A. Effect of Deterministic Failure Containment
19. VI-B. Validity-Rejection Trade-Off
20. VI-C. Remaining Limitations
21. VII. Threats to Validity
22. VIII. Conclusion and Future Work

## Main-Paper Visual Plan

The preferred main-paper visuals are:

- Fig. 1 — Proposed deterministic intent-translation architecture
- Table I — Experimental evaluation sequence
- Table II — Cross-experiment decision results
- Table III — Final E3-v3 held-out performance
- Fig. 2 — Held-out decision accuracy by family H1-H8
- Fig. 3 — Residual held-out failure taxonomy T1-T6
- Table IV — Residual failure classes
- Fig. 4 — Rejection-stage distribution, if page budget permits

Detailed LLM invocation, family-level results, rejection stages, runtime, and
descriptor-generation measurements may be placed in supplementary material.

## Integrity Statement

The final E3-v3 benchmark and implementation were frozen before the official
evaluation. The official result remains 101/120. The retained 19 errors are
used for failure analysis and are not used for result-driven modification or
rerunning of the frozen evaluation.

A post-evaluation expanded exposure audit supplements the pre-evaluation
leakage screen. It must be identified as post-evaluation rather than described
as preregistered or pre-evaluation evidence.

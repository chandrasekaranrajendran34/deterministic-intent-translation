# Core IEEE Manuscript Draft

## Working Title

**Deterministic Intent Translation for 3GPP- and O-RAN-Aligned Network Slicing: A Hallucination-Resistant Pipeline**

---

## Abstract

Natural-language intent interfaces can simplify network-slice management, but probabilistic semantic extraction may omit source constraints, accept unsupported capabilities, or produce intermediate representations that appear valid while failing to preserve the original request. This work presents a hallucination-resistant intent-translation pipeline that separates probabilistic semantic extraction from deterministic failure containment. The architecture combines source-side analysis, constraint-consistency checking, a canonical intermediate representation (CIR), reconciliation and normalization, source-to-CIR preservation, deterministic validation, and closed-world capability policies before 3GPP- and O-RAN-oriented descriptor generation. Evaluation followed a staged sequence of controlled experiments culminating in a frozen 120-case held-out benchmark containing 58 valid and 62 invalid intents. The final E3-v3 pipeline correctly classified 101 of 120 held-out intents, yielding 84.17% decision accuracy with an exact 95% confidence interval of 76.38–90.19%. It accepted 87.93% of valid intents and rejected 80.65% of invalid intents, with a rejection F1 score of 84.03%. Nineteen retained errors identify remaining limitations in source-semantic resolution, normalization, capability auditing, and relational or compound-constraint handling. The results support deterministic failure containment around probabilistic intent extraction within the defined closed-world capability scope; they do not establish hallucination-free operation or formal 3GPP/O-RAN conformance.

---

## Contributions

The principal contributions of this work are:

1. A source-aware intent-translation architecture that separates probabilistic semantic extraction from deterministic source analysis, consistency checking, validation, and descriptor actuation.

2. An explicit source-to-CIR preservation mechanism that checks whether supported constraints captured from the original natural-language intent survive probabilistic translation into the canonical intermediate representation.

3. Closed-world deterministic failure containment using capability, policy, contradiction, qualitative-requirement, and preservation checks before descriptor generation.

4. A staged empirical evaluation comprising controlled feasibility, robustness and failure discovery, targeted repair evidence, and a final frozen 120-case held-out benchmark.

5. A retained failure taxonomy for the 19 incorrect held-out decisions, exposing limitations in semantic resolution, normalization, capability coverage, and compound or relational constraint handling.

---

# V. Results

## A. Development Evidence: E1 and E2A

The first controlled experiment (E1) evaluated 50 intents. The direct LLM baseline and the proposed E3 pipeline each produced 50/50 correct decisions, whereas the CIR-plus-deterministic-validation pipeline produced 47/50 correct decisions (94.00%). The three CIR-validation errors occurred when explicitly unsupported source parameters were omitted during probabilistic extraction. Once those source details were absent from the generated CIR, downstream CIR validation had no information with which to reject them. E1 therefore exposed an information-loss boundary: deterministic validation of an intermediate representation cannot validate source information that has already been lost during probabilistic extraction.

E2A evaluated 200 intents containing unseen linguistic forms, compound constraints, contradictions, unsupported semantics, and adversarial requests. The direct LLM baseline produced 138/200 correct decisions (69.00%), CIR plus deterministic validation produced 151/200 (75.50%), and proposed E3 produced 165/200 (82.50%). Within this common E2A benchmark, paired analysis showed 14 wrong-to-correct and no correct-to-wrong transitions between CIR validation and proposed E3 (exact p=0.000122). Against direct generation, proposed E3 showed 59 wrong-to-correct and 32 correct-to-wrong transitions (exact p=0.006106). The direct-versus-CIR comparison did not show a statistically distinguishable paired difference at the 0.05 level (p=0.236902).

The E2A failures revealed limitations involving implicit unsupported semantics, contradictions not represented in the CIR, mixed-constraint information loss, adversarial bypasses, and false rejection of valid intents. These observations motivated additional deterministic source-side and preservation mechanisms. Because E1 and E2A use different benchmark populations, their accuracy values are not interpreted as a common-test-set performance progression.

## B. Targeted Repair Evidence: E2B

E2B evaluated targeted deterministic safeguards on a separate 120-case development benchmark constructed after analysis of the E2A failure modes. The original E3 implementation correctly classified 54/120 cases (45.00%), whereas E3-v2 correctly classified 101/120 cases (84.17%). Paired comparison identified 50 cases correct under both implementations, four cases correct only under the original E3 implementation, 51 cases correct only under E3-v2, and 15 cases incorrect under both. The resulting exact paired p-value was approximately 2.05 × 10^-11.

E3-v2 accepted 71.11% of valid intents and rejected 92.00% of invalid intents, with rejection precision of 84.15% and rejection F1 of 87.90%. These measurements demonstrate the effect of the targeted repair mechanisms on the E2B benchmark. They are treated as development evidence rather than as an independent estimate of final generalization performance.

## C. Final E3-v3 Held-Out Evaluation

The primary evaluation used the final frozen E3-v3 architecture and a 120-case held-out benchmark frozen before the official evaluation. The benchmark contained 58 valid and 62 invalid intents. E3-v3 correctly classified 101/120 cases, yielding a decision accuracy of 84.17%. The exact Clopper-Pearson 95% confidence interval was 76.38–90.19%.

Of the 58 valid intents, 51 were accepted, corresponding to a valid-intent acceptance rate of 87.93%. Of the 62 invalid intents, 50 were rejected, corresponding to an invalid-intent rejection rate of 80.65%. Rejection precision was 50/57 (87.72%), rejection recall was 50/62 (80.65%), and rejection F1 was 84.03%.

Performance varied across the eight held-out benchmark families. Decision accuracy was 72.22% for H1, 88.89% for H2, 90.00% for H3, 85.71% for H4, 100.00% for H5, 50.00% for H6, 80.00% for H7, and 100.00% for H8. These family-level results show that the aggregate 84.17% accuracy masks substantial variation across intent classes.

The LLM was invoked for 77/120 held-out cases (64.17%), and all 77 invoked responses were parsed successfully. Sixty-three intents were accepted, and all 63 generated descriptors. Descriptor generation is reported as a pipeline-output property and does not establish successful network deployment or formal standards conformance.

Mean end-to-end processing latency was 1050.16 ms, with a median of 944.86 ms and a 95th percentile of 3434.82 ms. These measurements characterize the controlled experimental environment and should not be generalized to production 5G or 6G network latency.

## D. Residual Failure Analysis

Nineteen of the 120 held-out decisions were incorrect. The frozen failure taxonomy assigned five errors to source-semantic-resolution false rejection (T1), two to reliability-representation normalization misses (T2), two to numeric capability-boundary omissions (T3), two to compound-constraint contradiction misses (T4), six to unsupported named-capability escape (T5), and two to relational-contradiction parsing misses (T6).

Unsupported named-capability escape was the largest residual category, accounting for 6/19 errors, followed by source-semantic-resolution false rejection at 5/19. The remaining categories each accounted for two errors. The 19 failures were retained after the official held-out evaluation and were not used to tune or rerun the final system. They therefore define observed limitations of the evaluated architecture rather than targets incorporated into the reported result.

---

# VIII. Conclusion and Future Work

This work investigated deterministic failure containment for natural-language intent translation in 3GPP- and O-RAN-oriented network slicing. The central design principle is to prevent probabilistic semantic extraction from directly determining executable descriptor actuation. Instead, the proposed pipeline combines deterministic source analysis, constraint-consistency checking, CIR extraction, reconciliation and normalization, source-to-CIR preservation, validation, and closed-world capability policies before descriptor generation.

The staged experiments exposed an important information-loss boundary: validation applied only to a generated intermediate representation cannot recover source constraints omitted during probabilistic extraction. Source-aware deterministic mechanisms were therefore introduced to retain and verify relevant information across the translation boundary. On the final frozen 120-case held-out benchmark, E3-v3 correctly classified 101 intents, corresponding to 84.17% decision accuracy with an exact 95% confidence interval of 76.38–90.19%. The system accepted 87.93% of valid intents, rejected 80.65% of invalid intents, and achieved a rejection F1 score of 84.03%.

The findings support a bounded conclusion: deterministic source analysis, consistency checks, preservation checks, and capability policies can provide explicit failure containment around probabilistic intent extraction within the defined evaluation and closed-world capability scope. The results do not establish hallucination-free operation, universal semantic correctness, production-network performance, or formal 3GPP/O-RAN conformance.

Future work should evaluate the architecture using independent operator or external intent corpora, expand capability and semantic-policy coverage, improve relational and compound-constraint reasoning, and examine robustness across additional language models and decoding configurations. A further step is normative validation of generated artifacts against applicable 3GPP and O-RAN specifications and evaluation in an executable network-slice testbed or digital-twin environment. The 19 retained held-out failures provide a transparent basis for such future investigation but are not used to modify the results reported in this study.

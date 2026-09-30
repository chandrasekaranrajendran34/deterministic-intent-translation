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

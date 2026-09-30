# IEEE Paper — Results and Discussion Evidence Package

## Evidence status

All quantitative statements in this package are derived from the frozen experiment artifacts and the locked cross-experiment synthesis. No experiment or model was rerun during preparation of this package.

## A. Experimental Evaluation Strategy

The evaluation was organized as a staged evidence sequence rather than as repeated measurements on a common test set. E1 provided an initial controlled evaluation; E2A examined robustness and exposed failure modes; E2B evaluated targeted deterministic repairs; and E3-v3 provided the final frozen held-out evaluation. Consequently, accuracy values across E1, E2A, E2B, and E3-v3 are not interpreted as a longitudinal learning curve or directly subjected to cross-benchmark significance testing.

## B. Initial Controlled Evaluation (E1)

On the 50-intent controlled E1 benchmark, both the direct LLM baseline and the proposed E3 pipeline classified all 50 decisions correctly, whereas the CIR-plus-deterministic-validation pipeline classified 47/50 correctly (94.00%). The three CIR failures arose when explicitly unsupported source parameters were omitted during probabilistic extraction. Because the omitted information was no longer present in the CIR, downstream CIR validation could not recover it. E1 therefore exposed an information-loss boundary between probabilistic extraction and deterministic validation.

## C. Robustness Evaluation (E2A)

E2A expanded the evaluation to 200 intents containing unseen linguistic forms, compound constraints, contradictions, unsupported semantics, and adversarial requests. Proposed E3 achieved 165/200 correct decisions (82.50%), compared with 151/200 (75.50%) for CIR validation and 138/200 (69.00%) for direct generation. Within this paired benchmark, the proposed pipeline differed from CIR validation (exact p=0.000122) and direct generation (exact p=0.006106). The direct-versus-CIR comparison did not show a statistically distinguishable paired difference at the 0.05 level (p=0.236902).

Failure analysis of E2A identified five recurring classes: implicit unsupported semantics, contradictions not represented by the CIR, mixed-constraint information loss, adversarial bypasses, and valid intent false rejection. These observations motivated additional deterministic source-side analysis and preservation mechanisms.

## D. Targeted Repair Evaluation (E2B)

The subsequent frozen E2B benchmark contained 120 cases designed to evaluate the identified repair mechanisms. Original E3 correctly classified 54/120 cases (45.00%), whereas E3-v2 correctly classified 101/120 (84.17%). Paired analysis identified 51 wrong-to-correct transitions and four correct-to-wrong transitions (exact paired p≈2.05×10^-11). E3-v2 rejected 92.00% of invalid intents but accepted 71.11% of valid intents. Because E2B was constructed after E2A failure analysis, these measurements are treated as targeted development evidence rather than an independent generalization estimate.

## E. Final Frozen Held-Out Evaluation (E3-v3)

The primary evaluation of the final E3-v3 architecture used a 120-case benchmark frozen before the official run. The benchmark contained 58 valid and 62 invalid intents. E3-v3 correctly classified 101/120 cases, yielding 84.17% decision accuracy with an exact Clopper–Pearson 95% confidence interval of 76.38–90.19%. Valid-intent acceptance was 51/58 (87.93%), while invalid-intent rejection was 50/62 (80.65%). Rejection precision was 50/57 (87.72%), rejection recall was 80.65%, and rejection F1 was 84.03%.

The LLM was invoked for 77/120 cases (64.17%). All 77 invoked responses were parsed successfully. Sixty-three intents were accepted, and all 63 produced descriptors. Mean end-to-end latency was 1050.16 ms, with a median of 944.86 ms and p95 of 3434.82 ms. These latency measurements characterize only the controlled experimental environment and are not deployment-level latency claims.

## F. Discussion

The experiments collectively indicate that the placement of deterministic safeguards is important. E1 showed that validating only the generated intermediate representation is insufficient when the probabilistic extraction stage has already discarded relevant source information. E2A reinforced this observation by exposing failures involving unsupported semantics, compound constraints, and contradictions. The later architectures therefore moved selected checks toward the source side and added explicit source-to-CIR preservation and consistency mechanisms.

The final E3-v3 result should not be interpreted solely through its 84.17% overall accuracy. The system accepted 87.93% of valid intents while rejecting 80.65% of invalid intents. This balance is relevant for intent translation because an overly aggressive validator may obtain high invalid-intent rejection by incorrectly rejecting usable requests, whereas an overly permissive system may preserve valid traffic at the expense of unsupported or contradictory requests.

The deterministic stages also reduced dependence on probabilistic extraction for a subset of requests: the LLM was invoked for 64.17% of held-out cases. This result demonstrates deterministic early termination within the implemented policy scope; it should not be interpreted as evidence that every non-LLM case represented an unsafe request.

## G. Residual Failure Analysis

Nineteen held-out cases remained incorrect. The frozen taxonomy assigned five cases to source-semantic-resolution false rejection (T1), two to reliability-representation normalization misses (T2), two to numeric capability-boundary omissions (T3), two to compound-constraint contradiction misses (T4), six to unsupported named-capability escape (T5), and two to relational-contradiction parsing misses (T6). Unsupported named-capability escape was the largest observed class (6/19), followed by source-semantic false rejection (5/19).

These failures were retained after the held-out evaluation rather than used for additional tuning. They therefore provide explicit evidence of the current system boundary. In particular, closed-world source auditing remains dependent on the supported vocabulary and capability catalog, while relational and compound constraints remain sensitive to how completely source semantics are represented.

## H. Threats to Validity and Limitations

**Benchmark construction.** The final benchmark was frozen before evaluation, but it is a controlled benchmark constructed for this study rather than an external operator or industry benchmark. The reported accuracy therefore estimates performance on the defined benchmark population, not all natural-language network intents.

**Closed-world coverage.** Several deterministic checks rely on explicit service, capability, qualitative, and policy vocabularies. Their deterministic behavior is reproducible within that defined scope, but the implementation is not a universal semantic or physical-impossibility detector.

**Model dependence.** Probabilistic CIR extraction was evaluated using the frozen model configuration used by the experiments. Different models, prompts, providers, or decoding implementations may produce different extraction behavior.

**Standards scope.** The experimental mapper and validators are standards-oriented/aligned components. The current experiments do not constitute formal 3GPP or O-RAN conformance testing and should not be described as certification of standards compliance.

**Exposure audit.** The original pre-evaluation leakage screening was conducted against the canonical prior corpus. A later read-only expanded audit reconstructed 528 unique prior intents from 6,507 temporally eligible occurrences across 136 CSV artifacts. It found no exact or normalized matches and no held-out case at or above the predefined 0.70 token-Jaccard review threshold; the maximum was 0.692308. Because this expanded analysis was performed after the official evaluation, it supplements rather than replaces the pre-evaluation screening and does not establish semantic independence or absence of model pretraining exposure.

## I. Evidence-Supported Conclusion

The experiments support a bounded conclusion: deterministic source analysis, consistency checking, source-to-CIR preservation, and closed-world capability policies can provide explicit failure containment around probabilistic natural-language intent extraction. The final frozen E3-v3 architecture achieved 84.17% decision accuracy on the controlled held-out benchmark while accepting 87.93% of valid intents and rejecting 80.65% of invalid intents. The remaining 19 errors identify limitations in semantic coverage, representation normalization, capability auditing, and relational constraint handling. The results do not establish hallucination-free operation, universal semantic correctness, formal standards conformance, or production-network performance.

## J. Recommended IEEE Table and Figure Placement

1. **Evaluation methodology table:** summarize E1, E2A, E2B, and E3-v3 by benchmark size, purpose, and methodological role. Avoid presenting their accuracy values as a common-test-set progression.

2. **Cross-experiment results table:** use the locked nine-row cross-experiment table, with a footnote stating that benchmark populations differ.

3. **Primary held-out results table:** report E3-v3 accuracy, valid acceptance, invalid rejection, rejection precision/recall/F1, and exact confidence intervals.

4. **Family-level figure:** show E3-v3 held-out decision accuracy across H1-H8.

5. **Failure-taxonomy figure:** show T1-T6 counts for the 19 residual errors.

6. **Rejection-stage figure:** show where deterministic rejection occurred in the final held-out pipeline.

7. **LLM-invocation figure:** show family-level LLM invocation rates to illustrate deterministic early processing without claiming that non-invoked cases are necessarily unsafe.

## K. Mandatory Claim Rules

- Use **hallucination-resistant** or **failure containment**, not **hallucination-free**.
- Use **standards-aligned/oriented**, unless formal conformance is independently established.
- Do not describe E1→E2A→E2B→E3-v3 as a common-test-set learning curve.
- Treat E2B as targeted development evidence.
- Treat E3-v3 as the primary final held-out result.
- Do not tune the current system using the 19 held-out failures.
- Preserve the distinction between deterministic behavior within the defined policy scope and universal semantic correctness.


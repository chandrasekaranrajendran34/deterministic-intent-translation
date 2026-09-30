# Cross-Experiment Scientific Synthesis

## Interpretation rule

E1, E2A, E2B, and E3-v3 use different benchmark populations and serve different experimental purposes. Their accuracy values must therefore not be interpreted as measurements on a common test set or as a monotonic learning curve.

The experiments instead form an evidence sequence: controlled feasibility (E1), robustness and failure discovery (E2A), targeted deterministic repair evaluation (E2B), and final frozen held-out evaluation (E3-v3).

## Experimental evidence

### S1 — E1 / controlled_initial

**Finding.** On the 50-intent controlled benchmark, the direct baseline and proposed E3 each classified 50/50 decisions correctly, while the CIR-only deterministic-validation pipeline classified 47/50 correctly.

**Evidence.** Direct 50/50 (100%); CIR 47/50 (94%); Proposed E3 50/50 (100%).

**Interpretation.** The controlled benchmark established functional correctness of the initial pipeline and exposed an information-loss boundary: deterministic CIR validation cannot recover unsupported information that the probabilistic extractor omits.

**Claim boundary.** This small controlled benchmark is not evidence of broad generalization and should not be compared numerically with later benchmark accuracies as if they used the same test population.

### S2 — E2A / robustness_generalization

**Finding.** On the 200-intent robustness benchmark, proposed E3 achieved 165/200 correct decisions, compared with 151/200 for CIR validation and 138/200 for the direct baseline.

**Evidence.** Proposed E3 82.50%; CIR 75.50%; Direct 69.00%. Paired exact tests: CIR vs Proposed p=0.000122; Direct vs Proposed p=0.006106; Direct vs CIR p=0.236902.

**Interpretation.** Within this benchmark, the source-aware proposed pipeline produced more correct decisions than both comparators. Failure analysis nevertheless exposed implicit unsupported semantics, contradictions and mixed-constraint information loss.

**Claim boundary.** The statistical tests are valid only for paired comparisons within E2A. They do not establish a statistical difference between E2A and any other experiment.

### S3 — E2B / targeted_repair

**Finding.** On the frozen 120-case targeted repair benchmark, E3-v2 classified 101/120 cases correctly compared with 54/120 for the original E3 pipeline.

**Evidence.** Original E3 54/120 (45.00%); E3-v2 101/120 (84.17%); paired transitions: 51 wrong-to-correct and 4 correct-to-wrong; exact paired p=2.05e-11.

**Interpretation.** The deterministic source-analysis, consistency and preservation safeguards addressed many failure modes identified in the preceding robustness study, especially invalid-intent rejection.

**Claim boundary.** E2B was constructed as a targeted repair benchmark after E2A failure analysis. It therefore provides development evidence rather than an independent final generalization estimate.

### S4 — E3-v3 / final_heldout

**Finding.** The frozen final E3-v3 system correctly classified 101/120 previously held-out benchmark cases.

**Evidence.** Accuracy 84.17% (exact 95% CI 76.38–90.19%); valid-intent acceptance 87.93%; invalid-intent rejection 80.65%; rejection precision 87.72%; rejection F1 84.03%.

**Interpretation.** This is the primary controlled generalization result for the final frozen architecture. The result shows that deterministic pre- and post-LLM safeguards can contain many unsupported, contradictory and adversarial requests while retaining a high valid-intent acceptance rate.

**Claim boundary.** The result applies to the frozen controlled held-out benchmark and defined closed-world capability policy. It does not demonstrate universal semantic correctness, hallucination-free operation, real-world deployment performance, or formal 3GPP/O-RAN conformance.

### S5 — E3-v3 / failure_analysis

**Finding.** Nineteen held-out cases remained incorrect and were assigned to six frozen failure classes.

**Evidence.** T1 source semantic resolution false rejection: 5; T2 reliability normalization miss: 2; T3 numeric capability boundary omission: 2; T4 compound contradiction miss: 2; T5 unsupported named-capability escape: 6; T6 relational contradiction parsing miss: 2.

**Interpretation.** The dominant observed residual failure class was unsupported named-capability escape (6/19), followed by source semantic resolution false rejection (5/19). These failures define concrete limitations for future work rather than targets for post-hoc tuning in the current study.

**Claim boundary.** The taxonomy describes observed failures in this controlled benchmark; it is not claimed to be a complete taxonomy of intent-translation failures.

### S6 — E3-v3 / integrity

**Finding.** A post-evaluation read-only expanded exposure audit found no exact, normalized or threshold-level lexical overlap between the 120 held-out cases and the expanded temporally eligible prior-exposure corpus.

**Evidence.** 136 eligible prior CSVs; 6,507 raw prior occurrences; 528 unique prior intents; 0/120 exact overlap; 0/120 normalized overlap; 0 cases with Jaccard >=0.70; maximum Jaccard 0.692308.

**Interpretation.** The read-only audit strengthens the evidence that the reported held-out result was not produced by exact or high-threshold lexical reuse of the expanded prior experimental corpus.

**Claim boundary.** The audit addresses lexical exposure within the identified local experimental corpus. It is not proof against all possible semantic similarity or model pretraining exposure.

## Paper-ready synthesis

The evaluation was conducted as a staged sequence rather than as a single benchmark. In E1, the initial 50-intent controlled evaluation established basic pipeline behavior and exposed an information-loss boundary: validation over the generated CIR cannot recover source constraints that are omitted during probabilistic extraction. The direct baseline and proposed E3 each achieved 50/50 correct decisions, whereas CIR-only validation achieved 47/50.

E2A then evaluated robustness on 200 intents containing unseen linguistic forms, compound constraints, unsupported semantics, contradictions and adversarial requests. Proposed E3 achieved 165/200 correct decisions (82.50%), compared with 151/200 (75.50%) for CIR validation and 138/200 (69.00%) for direct generation. Within this paired benchmark, proposed E3 differed from CIR validation (exact p=0.000122) and from direct generation (exact p=0.006106), while the direct-versus-CIR comparison was not statistically distinguishable at the 0.05 level (p=0.236902). These results motivated explicit deterministic source-side safeguards.

On the subsequent frozen 120-case targeted E2B benchmark, E3-v2 achieved 101/120 correct decisions (84.17%) compared with 54/120 (45.00%) for the original E3 implementation. Paired analysis identified 51 wrong-to-correct transitions and four correct-to-wrong transitions. Because this benchmark was constructed after analysis of earlier failure modes, E2B is treated as development evidence rather than as the final generalization estimate.

The primary final result is therefore the independently frozen E3-v3 held-out evaluation. E3-v3 correctly classified 101 of 120 cases, corresponding to 84.17% decision accuracy with an exact 95% Clopper–Pearson confidence interval of 76.38–90.19%. Valid-intent acceptance was 87.93%, invalid-intent rejection was 80.65%, rejection precision was 87.72%, and rejection F1 was 84.03%. All 77 invoked LLM calls parsed successfully, and all 63 accepted intents produced descriptors.

The 19 residual held-out errors were retained rather than tuned away. They comprised five source-semantic false rejections, two reliability-representation normalization misses, two numeric capability-boundary omissions, two compound-constraint contradiction misses, six unsupported named-capability escapes, and two relational-contradiction parsing misses. These observed failures delimit the current closed-world deterministic coverage and motivate future extensions.

Finally, a post-evaluation read-only integrity audit expanded the prior-exposure corpus to 528 unique intents derived from 6,507 temporally eligible occurrences across 136 CSV artifacts. No held-out case had an exact or normalized match, no case reached the predefined Jaccard review threshold of 0.70, and the maximum observed token Jaccard similarity was 0.692308. The audit did not alter the benchmark, predictions, labels, or official 101/120 result.

These results support a narrower conclusion than universal hallucination elimination: deterministic source analysis, consistency checking, preservation checks and closed-world capability policies can provide explicit failure containment around probabilistic intent extraction. Formal standards conformance and deployment-level validation remain outside the scope of the present controlled evaluation.


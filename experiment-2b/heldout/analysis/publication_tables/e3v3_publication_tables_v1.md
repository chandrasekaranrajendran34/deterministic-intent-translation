# E3-v3 Held-Out Evaluation — Publication Tables

Source: frozen 120-case controlled held-out benchmark.

## Table 1. Overall Held-Out Performance

| Metric                   | Result   |   Rate (%) | Exact 95% CI (%)   |
|:-------------------------|:---------|-----------:|:-------------------|
| Decision accuracy        | 101/120  |      84.17 | 76.38–90.19        |
| Valid-intent acceptance  | 51/58    |      87.93 | 76.70–95.01        |
| Invalid-intent rejection | 50/62    |      80.65 | 68.63–89.58        |
| Rejection precision      | 50/57    |      87.72 | 76.32–94.92        |
| Rejection recall         | 50/62    |      80.65 | 68.63–89.58        |
| Rejection F1             | —        |      84.03 | —                  |

## Table 2. Performance by Benchmark Family

| Family   | Category                             | Correct / N   |   Accuracy (%) | Valid accepted   | Invalid rejected   |
|:---------|:-------------------------------------|:--------------|---------------:|:-----------------|:-------------------|
| H1       | Canonical / semantic service intents | 13/18         |          72.22 | 13/18            | —                  |
| H2       | Single numeric constraints           | 16/18         |          88.89 | 12/12            | 4/6                |
| H3       | Compound / multi-constraints         | 18/20         |          90    | 12/12            | 6/8                |
| H4       | Reliability representations          | 12/14         |          85.71 | 6/8              | 6/6                |
| H5       | Qualitative requirements             | 16/16         |         100    | 8/8              | 8/8                |
| H6       | Unsupported capabilities             | 6/12          |          50    | —                | 6/12               |
| H7       | Contradictions / incompatible bounds | 8/10          |          80    | —                | 8/10               |
| H8       | Control / adversarial attempts       | 12/12         |         100    | —                | 12/12              |

## Table 3. Observed Failure Taxonomy

| Class   | Observed failure mechanism                    | Error type   |   Count |   Share of failures (%) |
|:--------|:----------------------------------------------|:-------------|--------:|------------------------:|
| T1      | Source semantic-resolution false rejection    | False reject |       5 |                   26.32 |
| T2      | Reliability representation normalization miss | False reject |       2 |                   10.53 |
| T3      | Numeric capability-boundary omission          | False accept |       2 |                   10.53 |
| T4      | Compound constraint contradiction miss        | False accept |       2 |                   10.53 |
| T5      | Unsupported named-capability escape           | False accept |       6 |                   31.58 |
| T6      | Relational contradiction parsing miss         | False accept |       2 |                   10.53 |

## Table 4. Rejection-Stage Distribution

| Rejection stage            |   Count |   Share of rejections (%) |
|:---------------------------|--------:|--------------------------:|
| source_gate                |      24 |                     42.11 |
| constraint_consistency     |      14 |                     24.56 |
| cir_validation             |      12 |                     21.05 |
| r7_qualitative_source_gate |       5 |                      8.77 |
| preservation               |       2 |                      3.51 |

## Table 5. LLM Invocation by Benchmark Family

| Family   | Category                             |   Cases |   LLM invocations |   Invocation rate (%) |
|:---------|:-------------------------------------|--------:|------------------:|----------------------:|
| H1       | Canonical / semantic service intents |      18 |                13 |                 72.22 |
| H2       | Single numeric constraints           |      18 |                18 |                100    |
| H3       | Compound / multi-constraints         |      20 |                14 |                 70    |
| H4       | Reliability representations          |      14 |                14 |                100    |
| H5       | Qualitative requirements             |      16 |                10 |                 62.5  |
| H6       | Unsupported capabilities             |      12 |                 6 |                 50    |
| H7       | Contradictions / incompatible bounds |      10 |                 2 |                 20    |
| H8       | Control / adversarial attempts       |      12 |                 0 |                  0    |

## Table 6. Execution Summary

| Measure                              | Result           | Value      |
|:-------------------------------------|:-----------------|:-----------|
| LLM invocation                       | 77/120           | 64.17%     |
| Parse success when LLM invoked       | 77/77            | 100.00%    |
| Descriptor success on accepted cases | 63/63            | 100.00%    |
| Mean end-to-end latency              | 120 cases        | 1050.16 ms |
| Median end-to-end latency            | 120 cases        | 944.86 ms  |
| P95 end-to-end latency               | 120 cases        | 3434.82 ms |
| Mean LLM latency                     | 77 invoked cases | 1587.39 ms |

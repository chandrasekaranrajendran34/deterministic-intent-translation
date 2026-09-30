# Cross-Experiment Authoritative Results

> Important: E1, E2A, E2B, and E3-v3 use different benchmark populations and experimental purposes. Values should not be interpreted as a single longitudinal test-set trajectory.

| Experiment   | Evaluation role                      | Method                         | Correct / N   |   Accuracy (%) | 95% CI        |   Valid acceptance |   Invalid rejection |   Rejection F1 |
|:-------------|:-------------------------------------|:-------------------------------|:--------------|---------------:|:--------------|-------------------:|--------------------:|---------------:|
| E1           | Controlled initial evaluation        | Direct LLM baseline            | 50/50         |         100    | 92.89–100.00% |             100    |              100    |         100    |
| E1           | Controlled initial evaluation        | CIR + deterministic validation | 47/50         |          94    | 83.45–98.75%  |             100    |               88    |          93.62 |
| E1           | Controlled initial evaluation        | Proposed E3                    | 50/50         |         100    | 92.89–100.00% |             100    |              100    |         100    |
| E2A          | Robustness/generalization evaluation | Direct LLM baseline            | 138/200       |          69    | 62.09–75.33%  |              39    |               99    |          76.15 |
| E2A          | Robustness/generalization evaluation | CIR + deterministic validation | 151/200       |          75.5  | 68.94–81.29%  |              96    |               55    |          69.18 |
| E2A          | Robustness/generalization evaluation | Proposed E3                    | 165/200       |          82.5  | 76.51–87.50%  |              97    |               68    |          79.53 |
| E2B          | Targeted E3-v2 repair evaluation     | Original E3                    | 54/120        |          45    | 35.91–54.35%  |              80    |               24    |          35.29 |
| E2B          | Targeted E3-v2 repair evaluation     | E3-v2                          | 101/120       |          84.17 | 76.38–90.19%  |              71.11 |               92    |          87.9  |
| E3-v3        | Final frozen held-out evaluation     | Final E3-v3                    | 101/120       |          84.17 | 76.38–90.19%  |              87.93 |               80.65 |          84.03 |


**Final held-out result:** E3-v3 correctly classified 101/120 intents (84.17%), with an exact Clopper–Pearson 95% confidence interval of 76.38–90.19%.

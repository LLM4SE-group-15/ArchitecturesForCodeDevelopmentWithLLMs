# Extracted Experimental Metrics

---

## Summary Table: Pass Rates and Confidence Intervals

| Architecture | Pass Rate | Pass@1 | 95% CI | Passed/Total |
|--------------|-----------|--------|--------|--------------|
| architecture-a | 67.7% | 67.68 | [60.19, 74.37] | 111/164 |
| architecture-a-pr | 68.3% | 68.29 | [60.82, 74.93] | 112/164 |
| architecture-b | 72.6% | 50.61% | [65.27, 78.81] | 119/164 |
| architecture-b-pr | 66.5% | - | [58.93, 73.24] | 109/164 |
| architecture-c | 62.2% | 35.37% | [54.57, 69.26] | 102/164 |
| architecture-c-pr | 54.3% | - | [46.63, 61.71] | 89/164 |
| architecture-c1 | 81.7% | 81.7% | [75.09, 86.88] | 134/164 |
| ablation-no-s-model | 72.0% | - | [64.63, 78.26] | 118/164 |

---

## Time Metrics

| Architecture | Avg Time (s) | Std Dev | Median | Min | Max | Total Time (s) |
|--------------|--------------|---------|--------|-----|-----|----------------|
| architecture-a | 2.98 | 1.02 | 2.76 | 1.51 | 7.16 | 488.66 |
| architecture-a-pr | 3.07 | 0.96 | 2.90 | 1.33 | 6.35 | 502.90 |
| architecture-b | 10.95 | 4.76 | 9.77 | 4.82 | 29.49 | 1796.12 |
| architecture-b-pr | 12.23 | 5.17 | 11.53 | 4.86 | 27.60 | 2006.34 |
| architecture-c | 19.28 | 10.49 | 19.36 | 5.67 | 53.91 | 3162.63 |
| architecture-c-pr | 20.83 | 10.48 | 21.02 | 5.69 | 48.79 | 3416.83 |
| architecture-c1 | 14.66 | 3.11 | 14.16 | 8.60 | 37.53 | 2404.58 |
| ablation-no-s-model | 13.32 | 7.67 | 9.79 | 5.25 | 53.73 | 2183.79 |

---

## API Calls Metrics

| Architecture | Average API Calls per Task | Total API Calls |
|--------------|----------------------------|-----------------|
| architecture-a | 1.00 | 164 |
| architecture-b | 4.33 | 710 |
| architecture-c | 4.85 | 796 |
| architecture-c1 | 3.00 | 492 |

*Note: Prompt Repetition (-PR) variants have the same API call counts as their base architectures.*

---

## Escalation Analysis

| Architecture | 0 Esc | 0 Esc Pass% | 1 Esc | 1 Esc Pass% | 2 Esc | 2 Esc Pass% | Total Esc |
|--------------|-------|-------------|-------|-------------|-------|-------------|-----------|
| architecture-a | 164 | 67.68% | 0 | — | 0 | — | 0 |
| architecture-a-pr | 164 | 68.29% | 0 | — | 0 | — | 0 |
| architecture-b | 83 | 100% | 53 | 62.26% | 28 | 10.71% | 109 |
| architecture-b-pr | 66 | 100% | 56 | 62.50% | 42 | 19.05% | 140 |
| architecture-c | 59 | 98.31% | 58 | 31.03% | 47 | 55.32% | 152 |
| architecture-c-pr | 51 | 98.04% | 56 | 39.29% | 57 | 29.82% | 170 |
| architecture-c1 | 164 | 81.71% | 0 | — | 0 | — | 0 |
| ablation-no-s-model | 90 | 97.78% | 74 | 40.54% | 0 | — | 74 |

---

## Developer Tier Distribution

| Architecture | Tier S | S % | S Pass% | Tier M | M % | M Pass% | Tier L | L % | L Pass% |
|--------------|--------|-----|---------|--------|-----|---------|--------|-----|---------|
| architecture-a | — | — | — | — | — | — | — | — | — |
| architecture-a-pr | — | — | — | — | — | — | — | — | — |
| architecture-b | 57 | 34.76% | 100% | 53 | 32.32% | 100% | 54 | 32.93% | 16.67% |
| architecture-b-pr | 49 | 29.88% | 100% | 44 | 26.83% | 100% | 71 | 43.29% | 22.54% |
| architecture-c | 0 | 0% | — | 57 | 34.76% | 100% | 107 | 65.24% | 42.06% |
| architecture-c-pr | 0 | 0% | — | 49 | 29.88% | 100% | 115 | 70.12% | 34.78% |
| architecture-c1 | 0 | 0% | — | 0 | 0% | — | 164 | 100% | 81.71% |
| ablation-no-s-model | 0 | 0% | — | 87 | 53.05% | 100% | 77 | 46.95% | 40.26% |

---

## Story Points Distribution

| Architecture | Avg Init SP | Avg Final SP | SP=1 | SP=2 | SP=3 | SP=5 | SP=8 |
|--------------|-------------|--------------|------|------|------|------|------|
| architecture-a | — | — | — | — | — | — | — |
| architecture-a-pr | — | — | — | — | — | — | — |
| architecture-b | 2.21 | 4.24 | 24 (83.3%) | 88 (76.1%) | 49 (63.3%) | 3 (33.3%) | 0 |
| architecture-b-pr | 2.19 | 4.80 | 25 (68.0%) | 93 (72.0%) | 41 (58.5%) | 5 (20.0%) | 0 |
| architecture-c | 3.19 | 6.49 | 4 (50.0%) | 43 (55.8%) | 79 (65.8%) | 36 (63.9%) | 2 (50.0%) |
| architecture-c-pr | 2.99 | 6.69 | 4 (25.0%) | 53 (30.2%) | 80 (62.5%) | 25 (84.0%) | 2 (50.0%) |
| architecture-c1 | 3.20 | 8.00 | 3 (100%) | 44 (86.4%) | 79 (83.5%) | 36 (72.2%) | 2 (50.0%) |
| ablation-no-s-model | 3.20 | — | 3 (33.3%) | 44 (70.5%) | 80 (71.3%) | 34 (82.4%) | 3 (33.3%) |

> Format: Count (Pass Rate %)

---

## Static Code Quality Metrics

| Architecture | Avg CC | Median CC | Max CC | Avg MI | Median MI | Min MI |
|--------------|--------|-----------|--------|--------|-----------|--------|
| architecture-a | 3.59 | 3.00 | 14 | 75.02 | 71.56 | 50.24 |
| architecture-a-pr | 3.95 | 4.00 | 14 | 75.51 | 70.69 | 50.24 |
| architecture-b | 3.87 | 3.50 | 13 | 84.52 | 88.47 | 52.25 |
| architecture-b-pr | 4.14 | 4.00 | 14 | 84.69 | 88.85 | 50.85 |
| architecture-c | 3.84 | 3.00 | 13 | 85.37 | 91.04 | 50.71 |
| architecture-c-pr | 4.00 | 4.00 | 13 | 83.92 | 87.68 | 50.40 |
| architecture-c1 | 4.58 | 4.00 | 16 | 81.06 | 82.38 | 48.94 |
| ablation-no-s-model | 3.81 | 3.00 | 13 | 84.03 | 87.66 | 50.33 |

---

## Passed vs Failed Tasks

| Architecture | Passed Avg CC | Passed Avg MI | Failed Avg CC | Failed Avg MI |
|--------------|---------------|---------------|---------------|---------------|
| architecture-a | 3.67 | 74.84 | 3.21 | 75.86 |
| architecture-a-pr | 4.03 | 75.15 | 3.66 | 76.90 |
| architecture-b | 3.76 | 83.77 | 4.66 | 90.10 |
| architecture-b-pr | 3.90 | 85.24 | 5.58 | 81.31 |
| architecture-c | 4.02 | 83.63 | 3.08 | 92.48 |
| architecture-c-pr | 4.40 | 80.76 | 2.58 | 95.16 |
| architecture-c1 | 4.55 | 80.61 | 4.85 | 85.69 |
| ablation-no-s-model | 3.94 | 82.80 | 3.00 | 91.70 |

---
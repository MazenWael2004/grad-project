# Benchmark Test Suite Evaluation Report

_Generated: 2026-07-01 15:39:45_

**Total Runs Analyzed:** 35

## Overall Performance

| Metric | Value |
|--------|-------|
| **Total Test Runs** | 35 |
| **JSON Schemas Valid** | 35/35 (100.0%) |
| **Constraint Judge Passed** | 34/35 (97.1%) |
| **Average Latency** | 90.8s |
| **Median Latency** | 87.3s |
| **Average Token Count** | 4501 |
| **Average Tool Calls** | 0.0 |


## LLM Rubric Assertion Details

| Rubric Assertion | Pass Rate | Status |
|------------------|-----------|--------|
| Travel Plan correctly strictly follows the schema. | 100.0% | ✅ PASSING |
| Accommodation suggestions are relevant to the city and user preferences. | 80.0% | ✅ PASSING |
| The daily sequence of activities is logically ordered chronologically (morning, afternoon, evening). | 80.0% | ✅ PASSING |
| Budget constraints are respected throughout the itinerary. | 48.6% | ⚠️ WARN |
#cheap trips cost quite a lot in current market
## Latency Breakdown

| Statistic | Value |
|-----------|-------|
| Minimum | 32.1s |
| Average | 90.8s |
| Median | 87.3s |
| Maximum | 151.4s |

## Failed Constraints Analysis

| Constraint Name | Failure Count |
|-----------------|---------------|
| Origin | 1 |

---

> [!NOTE]
> This report was automatically compiled from the results located in [results/](file:///C:/grad-project/AI_Agents/Benchmarking/rubrics/results).
> Run `python run_tests.py` to regenerate results.

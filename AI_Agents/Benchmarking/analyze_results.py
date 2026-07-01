"""
analyze_results.py -- Aggregate run_tests.py results and generate report with charts.

Reads rubrics/results/*_result.json and produces:
  1. Console summary of pass rates and latency
  2. Matplotlib charts saved as PNG in rubrics/results/plots/
  3. Markdown report (summary_report.md) with embedded charts
  4. JSON export (summary_report.json)
"""

import os
import json
import numpy as np
from collections import Counter
from datetime import datetime

# Try to import matplotlib for chart generation
try:
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Premium color palette matching analyze_benchmarks
COLORS = {
    "primary": "#4F46E5",       # Indigo
    "success": "#10B981",       # Emerald
    "danger": "#EF4444",        # Red
    "warning": "#F59E0B",       # Amber
    "info": "#3B82F6",          # Blue
    "purple": "#8B5CF6",        # Purple
    "bg_dark": "#1E1E2E",       # Dark background
    "bg_card": "#2D2D44",       # Card background
    "text": "#E2E8F0",          # Light text
    "text_muted": "#94A3B8",    # Muted text
    "grid": "#374151",          # Grid lines
}

def apply_chart_style():
    """Apply a premium dark theme to all charts."""
    if not HAS_MATPLOTLIB:
        return
    plt.rcParams.update({
        "figure.facecolor": COLORS["bg_dark"],
        "axes.facecolor": COLORS["bg_card"],
        "axes.edgecolor": COLORS["grid"],
        "axes.labelcolor": COLORS["text"],
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.grid": True,
        "grid.color": COLORS["grid"],
        "grid.alpha": 0.3,
        "text.color": COLORS["text"],
        "xtick.color": COLORS["text_muted"],
        "ytick.color": COLORS["text_muted"],
        "font.size": 11,
        "figure.dpi": 150,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.3,
    })

def main():
    benchmarking_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(benchmarking_dir, "rubrics", "results")
    plots_dir = os.path.join(results_dir, "plots")
    
    os.makedirs(plots_dir, exist_ok=True)
    
    # 1. Load results
    result_files = [f for f in os.listdir(results_dir) if f.endswith("_result.json") and f != "summary_report.json"]
    
    if not result_files:
        print(f"[WARN] No result files found in {results_dir}. Run some tests first!")
        return

    results = []
    out_of_date_files = []
    for file in result_files:
        path = os.path.join(results_dir, file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Check if it has the updated assertions
                has_new = False
                llm_rubric = data.get("grading_results", {}).get("llm_rubric_grader", {})
                if llm_rubric and "results" in llm_rubric:
                    for item in llm_rubric["results"]:
                        if "logically ordered chronologically" in item.get("assertion", ""):
                            has_new = True
                            break
                
                if has_new:
                    results.append(data)
                else:
                    out_of_date_files.append(file)
                    try:
                        os.remove(path)
                    except Exception as e:
                        print(f"[WARN] Failed to delete out-of-date file {file}: {e}")
        except Exception as e:
            print(f"[WARN] Failed to load {file}: {e}")

    total_runs = len(results)
    print(f"Loaded {total_runs} up-to-date test runs.")
    if out_of_date_files:
        print(f"\n[INFO] Deleted {len(out_of_date_files)} out-of-date test results (missing the new rubrics):")
        for f in sorted(out_of_date_files):
            prompt_name = f.replace("_result.json", ".md")
            print(f"  - {prompt_name} (Deleted result file)")
        print()

    # 2. Extract metrics
    latencies = []
    tokens = []
    tool_calls = []
    turns = []
    
    json_valid_count = 0
    judge_pass_count = 0
    
    assertion_counts = Counter()
    assertion_passes = Counter()
    failed_constraints_counter = Counter()

    for r in results:
        # Latency & Token metrics
        metrics = r.get("metrics", {})
        latency_val = metrics.get("latency", {}).get("time_to_last_token", 0.0)
        latencies.append(latency_val)
        tokens.append(metrics.get("n_total_tokens", 0))
        tool_calls.append(metrics.get("n_toolcalls", 0))
        turns.append(metrics.get("n_turns", 0))

        # Schema validity
        if r.get("generated_plan") is not None and r.get("generated_plan") != {}:
            json_valid_count += 1

        # Judge details
        grading = r.get("grading_results", {})
        judge = grading.get("judge_grader", {})
        if judge:
            if judge.get("passed", False):
                judge_pass_count += 1
            for constraint in judge.get("failed_constraints", []):
                failed_constraints_counter[constraint] += 1

        # Rubric assertions
        llm_rubric = grading.get("llm_rubric_grader", {})
        if llm_rubric and "results" in llm_rubric:
            for item in llm_rubric["results"]:
                assertion = item.get("assertion")
                passed = item.get("passed", False)
                assertion_counts[assertion] += 1
                if passed:
                    assertion_passes[assertion] += 1

    # Computations
    avg_latency = float(np.mean(latencies)) if latencies else 0.0
    median_latency = float(np.median(latencies)) if latencies else 0.0
    min_latency = float(np.min(latencies)) if latencies else 0.0
    max_latency = float(np.max(latencies)) if latencies else 0.0
    
    avg_tokens = float(np.mean(tokens)) if tokens else 0.0
    avg_toolcalls = float(np.mean(tool_calls)) if tool_calls else 0.0
    avg_turns = float(np.mean(turns)) if turns else 0.0

    schema_pass_rate = (json_valid_count / total_runs) * 100 if total_runs > 0 else 0.0
    judge_pass_rate = (judge_pass_count / total_runs) * 100 if total_runs > 0 else 0.0

    # Assertion Pass Rates
    assertion_rates = {}
    for assertion, total in assertion_counts.items():
        passes = assertion_passes.get(assertion, 0)
        assertion_rates[assertion] = (passes / total) * 100 if total > 0 else 0.0

    # 3. Generate plots
    if HAS_MATPLOTLIB:
        apply_chart_style()
        
        # Plot 1: Main Pass Rates Bar Chart
        plt.figure(figsize=(6, 4))
        categories = ["Schema Valid", "Judge Passed"]
        rates = [schema_pass_rate, judge_pass_rate]
        colors = [COLORS["success"] if r > 70 else (COLORS["warning"] if r > 40 else COLORS["danger"]) for r in rates]
        
        bars = plt.bar(categories, rates, color=colors, width=0.5, edgecolor=COLORS["grid"])
        plt.ylim(0, 105)
        plt.ylabel("Pass Rate (%)")
        plt.title("Constraint & Schema Validation Rates")
        
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2.0, height + 2, f"{height:.1f}%", ha="center", va="bottom", fontweight="bold")
            
        pass_rates_plot_path = os.path.join(plots_dir, "pass_rates.png")
        plt.savefig(pass_rates_plot_path)
        plt.close()

        # Plot 2: Rubric Assertions Horizontal Bar Chart
        if assertion_rates:
            plt.figure(figsize=(10, 5))
            sorted_assertions = sorted(assertion_rates.items(), key=lambda x: x[1])
            labels = [a[0][:50] + "..." if len(a[0]) > 50 else a[0] for a in sorted_assertions]
            vals = [a[1] for a in sorted_assertions]
            
            y_pos = np.arange(len(labels))
            plt.barh(y_pos, vals, color=COLORS["primary"], edgecolor=COLORS["grid"])
            plt.yticks(y_pos, labels)
            plt.xlim(0, 105)
            plt.xlabel("Pass Rate (%)")
            plt.title("LLM Rubric Assertion Pass Rates")
            
            for i, v in enumerate(vals):
                plt.text(v + 1, i, f"{v:.1f}%", va="center", fontweight="bold")
                
            assertions_plot_path = os.path.join(plots_dir, "assertions.png")
            plt.savefig(assertions_plot_path)
            plt.close()

        # Plot 3: Latency Distribution Hist
        if len(latencies) > 1:
            plt.figure(figsize=(7, 4))
            plt.hist(latencies, bins=min(len(latencies), 10), color=COLORS["info"], edgecolor=COLORS["grid"], alpha=0.8)
            plt.xlabel("Latency (seconds)")
            plt.ylabel("Frequency")
            plt.title("Itinerary Generation Latency Distribution")
            
            plt.axvline(avg_latency, color=COLORS["danger"], linestyle="dashed", linewidth=1.5, label=f"Mean: {avg_latency:.1f}s")
            plt.axvline(median_latency, color=COLORS["warning"], linestyle="dashed", linewidth=1.5, label=f"Median: {median_latency:.1f}s")
            plt.legend()
            
            latency_plot_path = os.path.join(plots_dir, "latency_dist.png")
            plt.savefig(latency_plot_path)
            plt.close()

        # Plot 4: Top Failed Constraints
        if failed_constraints_counter:
            plt.figure(figsize=(8, 4))
            common_failures = failed_constraints_counter.most_common(5)
            fail_labels = [f[0] for f in common_failures]
            fail_counts = [f[1] for f in common_failures]
            
            plt.bar(fail_labels, fail_counts, color=COLORS["danger"], edgecolor=COLORS["grid"], width=0.4)
            plt.ylabel("Failure Count")
            plt.title("Top Failed Constraints (Constraint Judge)")
            
            for i, count in enumerate(fail_counts):
                plt.text(i, count + 0.1, str(count), ha="center", va="bottom", fontweight="bold")
                
            failures_plot_path = os.path.join(plots_dir, "failed_constraints.png")
            plt.savefig(failures_plot_path)
            plt.close()

    # 4. Generate JSON Summary
    summary_data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_runs": total_runs,
        "valid_json_count": json_valid_count,
        "schema_pass_rate": round(schema_pass_rate, 2),
        "judge_pass_count": judge_pass_count,
        "judge_pass_rate": round(judge_pass_rate, 2),
        "averages": {
            "latency": round(avg_latency, 2),
            "tokens": round(avg_tokens, 2),
            "toolcalls": round(avg_toolcalls, 2),
            "turns": round(avg_turns, 2)
        },
        "latency_stats": {
            "min": round(min_latency, 2),
            "max": round(max_latency, 2),
            "median": round(median_latency, 2)
        },
        "assertions": assertion_rates,
        "failed_constraints": dict(failed_constraints_counter)
    }

    json_report_path = os.path.join(results_dir, "summary_report.json")
    with open(json_report_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    # 5. Generate Markdown Report
    md_content = f"""# Benchmark Test Suite Evaluation Report

_Generated: {summary_data['generated_at']}_

**Total Runs Analyzed:** {total_runs}

## Overall Performance

| Metric | Value |
|--------|-------|
| **Total Test Runs** | {total_runs} |
| **JSON Schemas Valid** | {json_valid_count}/{total_runs} ({schema_pass_rate:.1f}%) |
| **Constraint Judge Passed** | {judge_pass_count}/{total_runs} ({judge_pass_rate:.1f}%) |
| **Average Latency** | {avg_latency:.1f}s |
| **Median Latency** | {median_latency:.1f}s |
| **Average Token Count** | {avg_tokens:.0f} |
| **Average Tool Calls** | {avg_toolcalls:.1f} |

"""

    if HAS_MATPLOTLIB:
        md_content += f"""
## Constraint & Schema Pass Rates
![Validation Rates](plots/pass_rates.png)
"""

    md_content += "\n## LLM Rubric Assertion Details\n\n"
    if assertion_rates:
        md_content += "| Rubric Assertion | Pass Rate | Status |\n|------------------|-----------|--------|\n"
        for assertion, rate in sorted(assertion_rates.items(), key=lambda x: x[1], reverse=True):
            status = "✅ PASSING" if rate > 75 else ("⚠️ WARN" if rate > 40 else "❌ FAILING")
            md_content += f"| {assertion} | {rate:.1f}% | {status} |\n"
        
        if HAS_MATPLOTLIB:
            md_content += f"\n![Rubric Assertions Chart](plots/assertions.png)\n"
    else:
        md_content += "_No rubric assertions data found._\n"

    md_content += "\n## Latency Breakdown\n\n"
    md_content += f"""| Statistic | Value |
|-----------|-------|
| Minimum | {min_latency:.1f}s |
| Average | {avg_latency:.1f}s |
| Median | {median_latency:.1f}s |
| Maximum | {max_latency:.1f}s |
"""

    if HAS_MATPLOTLIB and len(latencies) > 1:
        md_content += f"\n![Latency Distribution Chart](plots/latency_dist.png)\n"

    md_content += "\n## Failed Constraints Analysis\n\n"
    if failed_constraints_counter:
        md_content += "| Constraint Name | Failure Count |\n|-----------------|---------------|\n"
        for constraint, count in failed_constraints_counter.most_common():
            md_content += f"| {constraint} | {count} |\n"
        
        if HAS_MATPLOTLIB:
            md_content += f"\n![Failed Constraints Chart](plots/failed_constraints.png)\n"
    else:
        md_content += "_No constraint failures logged. All runs passed constraint validation!_ 🎉\n"

    md_content += f"""
---

> [!NOTE]
> This report was automatically compiled from the results located in [results/](file:///{results_dir.replace(os.sep, '/')}).
> Run `python run_tests.py` to regenerate results.
"""

    md_report_path = os.path.join(results_dir, "summary_report.md")
    with open(md_report_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY:")
    print("=" * 60)
    print(f"Total Test Runs:         {total_runs}")
    print(f"Schema Valid Rate:       {schema_pass_rate:.1f}%")
    print(f"Constraint Pass Rate:    {judge_pass_rate:.1f}%")
    print(f"Average Latency:         {avg_latency:.1f}s")
    print(f"Median Latency:          {median_latency:.1f}s")
    print(f"Average Token Usage:     {avg_tokens:.0f} tokens")
    if failed_constraints_counter:
        print(f"Most Frequent Failure:   {failed_constraints_counter.most_common(1)[0][0]} ({failed_constraints_counter.most_common(1)[0][1]} times)")
    print("-" * 60)
    print(f"Saved JSON summary:      {json_report_path}")
    print(f"Saved Markdown report:   {md_report_path}")
    if HAS_MATPLOTLIB:
        print(f"Saved Plot Charts:       Inside {plots_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()

"""
analyze_benchmarks.py -- Aggregate Benchmark Analysis with Matplotlib Charts.

Reads benchmark_results.jsonl and produces:
  1. Console summary report with pass rates, averages, distributions
  2. Matplotlib charts saved as PNG in Benchmarking/reports/
  3. Markdown report (benchmark_report.md) with embedded chart images
  4. JSON export (benchmark_report.json) for programmatic access

Usage:
    python -m AI_Agents.Benchmarking.analyze_benchmarks
    python AI_Agents/Benchmarking/analyze_benchmarks.py
"""

import json
import os
import sys
from collections import Counter
from datetime import datetime

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for saving charts
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ─── Paths ──────────────────────────────────────────────────────────────────

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_LOG_FILE = os.path.join(_SCRIPT_DIR, "benchmark_results.jsonl")
_REPORTS_DIR = os.path.join(_SCRIPT_DIR, "reports")

# ─── Chart Style ────────────────────────────────────────────────────────────

# Premium color palette
COLORS = {
    "primary": "#4F46E5",       # Indigo
    "success": "#10B981",       # Emerald
    "danger": "#EF4444",        # Red
    "warning": "#F59E0B",       # Amber
    "info": "#3B82F6",          # Blue
    "purple": "#8B5CF6",        # Purple
    "pink": "#EC4899",          # Pink
    "teal": "#14B8A6",          # Teal
    "bg_dark": "#1E1E2E",       # Dark background
    "bg_card": "#2D2D44",       # Card background
    "text": "#E2E8F0",          # Light text
    "text_muted": "#94A3B8",    # Muted text
    "grid": "#374151",          # Grid lines
}

PALETTE = [
    COLORS["primary"], COLORS["success"], COLORS["danger"],
    COLORS["warning"], COLORS["info"], COLORS["purple"],
    COLORS["pink"], COLORS["teal"],
]


def apply_chart_style():
    """Apply a premium dark theme to all charts."""
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


# ─── Data Loading ───────────────────────────────────────────────────────────

def load_results(filepath: str) -> list[dict]:
    """Load all entries from a JSONL file."""
    entries = []
    if not os.path.exists(filepath):
        print(f"[WARN] Log file not found: {filepath}")
        return entries
    with open(filepath, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"[WARN] Skipping malformed line {line_no}: {e}")
    return entries


# ─── Metric Extraction ──────────────────────────────────────────────────────

def extract_metrics(entries: list[dict]) -> dict:
    """Extract and aggregate all metrics from benchmark entries."""
    metrics = {
        "total_runs": len(entries),
        "scripts": Counter(),
        "timestamps": [],
        # Schema / JSON validity
        "schema_passes": 0,
        "schema_fails": 0,
        "json_valid": 0,
        "json_invalid": 0,
        # Judge
        "judge_passes": 0,
        "judge_fails": 0,
        "judge_null": 0,
        # Spatial
        "spatial_scores": [],
        "spatial_coverages": [],
        "spatial_flagged": [],
        "spatial_total_transitions": [],
        # Latency / performance
        "latencies": [],
        "ttft_values": [],   # time to first token
        "ttlt_values": [],   # time to last token
        "tps_values": [],    # tokens per second
        "tool_calls": [],
        "total_tokens": [],
        # Failure analysis
        "failed_constraints": [],
        "spatial_issues_all": [],
        # Per-script breakdown
        "per_script": {},
    }

    for entry in entries:
        script = entry.get("script", "unknown")
        results = entry.get("results", {})
        extra = entry.get("extra", {})
        metrics["scripts"][script] += 1
        metrics["timestamps"].append(entry.get("timestamp", ""))

        # Initialize per-script tracking
        if script not in metrics["per_script"]:
            metrics["per_script"][script] = {
                "total": 0, "passed": 0, "failed": 0,
                "latencies": [], "spatial_scores": [],
            }
        metrics["per_script"][script]["total"] += 1

        # ── Schema / JSON validity ─────────────────────────────────────
        # Different scripts store validity differently
        plan_valid = results.get("plan_valid_json")
        valid_json = results.get("valid_json")
        schema_valid = results.get("schema_valid")

        if plan_valid is True or valid_json is True:
            metrics["json_valid"] += 1
        elif plan_valid is False or valid_json is False:
            metrics["json_invalid"] += 1

        if schema_valid is True:
            metrics["schema_passes"] += 1
        elif schema_valid is False:
            metrics["schema_fails"] += 1
        elif plan_valid is True or valid_json is True:
            # Legacy entries without schema_valid — treat json validity as schema pass
            metrics["schema_passes"] += 1
        elif plan_valid is False or valid_json is False:
            metrics["schema_fails"] += 1

        # ── Judge ─────────────────────────────────────────────────────
        judge_passed = results.get("judge_passed")
        passed = results.get("passed")

        if judge_passed is True or passed is True:
            metrics["judge_passes"] += 1
            metrics["per_script"][script]["passed"] += 1
        elif judge_passed is False or passed is False:
            metrics["judge_fails"] += 1
            metrics["per_script"][script]["failed"] += 1
        elif judge_passed is None:
            metrics["judge_null"] += 1

        # ── Spatial ───────────────────────────────────────────────────
        spatial_score = results.get("spatial_score")
        if spatial_score is not None:
            metrics["spatial_scores"].append(spatial_score)

        coverage = results.get("spatial_coverage", results.get("coverage"))
        if coverage is not None:
            metrics["spatial_coverages"].append(coverage)

        flagged = results.get("spatial_flagged_transitions", results.get("flagged_transitions"))
        if flagged is not None:
            metrics["spatial_flagged"].append(flagged)

        total_trans = results.get("spatial_total_transitions", results.get("total_transitions"))
        if total_trans is not None:
            metrics["spatial_total_transitions"].append(total_trans)

        # ── Latency / Performance ─────────────────────────────────────
        elapsed = extra.get("elapsed_seconds") or results.get("elapsed_seconds")
        if elapsed is not None:
            metrics["latencies"].append(elapsed)
            metrics["per_script"][script]["latencies"].append(elapsed)

        # Detailed latency from run_tests.py format
        latency_block = results.get("latency", extra.get("latency", {}))
        if isinstance(latency_block, dict):
            ttft = latency_block.get("time_to_first_token")
            if ttft is not None:
                metrics["ttft_values"].append(ttft)
            ttlt = latency_block.get("time_to_last_token")
            if ttlt is not None:
                metrics["ttlt_values"].append(ttlt)
            tps = latency_block.get("output_tokens_per_sec")
            if tps is not None:
                metrics["tps_values"].append(tps)

        # Tool calls & tokens
        n_tools = results.get("n_toolcalls")
        if n_tools is not None:
            metrics["tool_calls"].append(n_tools)
        n_tokens = results.get("n_total_tokens")
        if n_tokens is not None:
            metrics["total_tokens"].append(n_tokens)

        # ── Failure analysis ──────────────────────────────────────────
        fc = results.get("judge_failed_constraints", results.get("failed_constraints", []))
        if fc:
            metrics["failed_constraints"].extend(fc)

        si = results.get("spatial_issues", [])
        if si:
            metrics["spatial_issues_all"].extend(si)

        # Spatial scores per script
        if spatial_score is not None:
            metrics["per_script"][script]["spatial_scores"].append(spatial_score)

    return metrics


# ─── Statistics Helpers ─────────────────────────────────────────────────────

def safe_avg(values: list) -> float:
    return sum(values) / len(values) if values else 0.0

def safe_min(values: list) -> float:
    return min(values) if values else 0.0

def safe_max(values: list) -> float:
    return max(values) if values else 0.0

def percentile(values: list, p: float) -> float:
    if not values:
        return 0.0
    sorted_v = sorted(values)
    k = (len(sorted_v) - 1) * (p / 100)
    f = int(k)
    c = f + 1
    if c >= len(sorted_v):
        return sorted_v[f]
    return sorted_v[f] + (k - f) * (sorted_v[c] - sorted_v[f])

def pct(num: int, denom: int) -> str:
    return f"{num / denom * 100:.1f}%" if denom > 0 else "N/A"


# ─── Chart Generation ──────────────────────────────────────────────────────

def chart_pass_rates(metrics: dict, output_dir: str) -> str:
    """Bar chart: Schema pass rate vs Judge pass rate."""
    filepath = os.path.join(output_dir, "schema_and_judge_pass_rates.png")

    total = metrics["total_runs"]
    if total == 0:
        return filepath

    schema_rate = metrics["schema_passes"] / total * 100
    judge_answered = metrics["judge_passes"] + metrics["judge_fails"]
    judge_rate = (metrics["judge_passes"] / judge_answered * 100) if judge_answered > 0 else 0
    json_rate = metrics["json_valid"] / total * 100

    categories = ["JSON Valid", "Schema Valid", "Judge Passed"]
    values = [json_rate, schema_rate, judge_rate]
    colors = [COLORS["info"], COLORS["success"], COLORS["primary"]]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(categories, values, color=colors, width=0.5, edgecolor="none", zorder=3)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
            f"{val:.1f}%", ha="center", va="bottom",
            fontweight="bold", color=COLORS["text"], fontsize=12,
        )

    ax.set_ylim(0, 115)
    ax.set_ylabel("Pass Rate (%)")
    ax.set_title("Validation & Judge Pass Rates")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.axhline(y=100, color=COLORS["success"], linestyle="--", alpha=0.3, zorder=1)

    fig.savefig(filepath)
    plt.close(fig)
    print(f"  [CHART] Saved: {os.path.basename(filepath)}")
    return filepath


def chart_spatial_distribution(metrics: dict, output_dir: str) -> str:
    """Histogram: Spatial score distribution."""
    filepath = os.path.join(output_dir, "spatial_score_distribution.png")
    scores = metrics["spatial_scores"]

    if not scores:
        return filepath

    fig, ax = plt.subplots(figsize=(8, 5))

    bins = [0, 0.25, 0.5, 0.75, 1.01]
    bin_labels = ["0-0.25\n(Poor)", "0.25-0.5\n(Fair)", "0.5-0.75\n(Good)", "0.75-1.0\n(Excellent)"]
    bin_colors = [COLORS["danger"], COLORS["warning"], COLORS["info"], COLORS["success"]]

    counts, _ = _histogram(scores, bins)

    bars = ax.bar(
        range(len(bin_labels)), counts,
        color=bin_colors, width=0.6, edgecolor="none", zorder=3,
    )

    for bar, count in zip(bars, counts):
        if count > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
                str(count), ha="center", va="bottom",
                fontweight="bold", color=COLORS["text"], fontsize=13,
            )

    ax.set_xticks(range(len(bin_labels)))
    ax.set_xticklabels(bin_labels)
    ax.set_ylabel("Number of Runs")
    ax.set_title("Spatial Coherence Score Distribution")
    ax.set_ylim(0, max(counts + [1]) + 1)

    # Add mean line annotation
    mean_score = safe_avg(scores)
    ax.annotate(
        f"Mean: {mean_score:.2f}", xy=(0.98, 0.95), xycoords="axes fraction",
        ha="right", va="top", fontsize=11, color=COLORS["teal"],
        bbox=dict(boxstyle="round,pad=0.3", facecolor=COLORS["bg_dark"], edgecolor=COLORS["teal"], alpha=0.8),
    )

    fig.savefig(filepath)
    plt.close(fig)
    print(f"  [CHART] Saved: {os.path.basename(filepath)}")
    return filepath


def _histogram(values: list, bins: list) -> tuple[list[int], list]:
    """Simple histogram binning without numpy."""
    counts = [0] * (len(bins) - 1)
    for v in values:
        for i in range(len(bins) - 1):
            if bins[i] <= v < bins[i + 1]:
                counts[i] += 1
                break
    return counts, bins


def chart_latency(metrics: dict, output_dir: str) -> str:
    """Box-style chart: Latency breakdown."""
    filepath = os.path.join(output_dir, "latency_breakdown.png")
    latencies = metrics["latencies"]

    if not latencies:
        return filepath

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Latency per run (bar chart)
    ax1 = axes[0]
    x_labels = [f"Run {i+1}" for i in range(len(latencies))]
    colors = [COLORS["primary"] if l < safe_avg(latencies) else COLORS["warning"] for l in latencies]
    bars = ax1.bar(range(len(latencies)), latencies, color=colors, width=0.6, edgecolor="none", zorder=3)
    ax1.axhline(y=safe_avg(latencies), color=COLORS["danger"], linestyle="--", alpha=0.7, label=f"Mean: {safe_avg(latencies):.1f}s")
    ax1.set_xticks(range(len(latencies)))
    ax1.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=9)
    ax1.set_ylabel("Seconds")
    ax1.set_title("End-to-End Latency per Run")
    ax1.legend(fontsize=9, loc="upper right")

    # Right: Latency statistics summary
    ax2 = axes[1]
    stats_labels = ["Min", "Avg", "Median", "P95", "Max"]
    stats_values = [
        safe_min(latencies),
        safe_avg(latencies),
        percentile(latencies, 50),
        percentile(latencies, 95),
        safe_max(latencies),
    ]
    stats_colors = [COLORS["success"], COLORS["info"], COLORS["primary"], COLORS["warning"], COLORS["danger"]]
    bars2 = ax2.barh(stats_labels, stats_values, color=stats_colors, height=0.5, edgecolor="none", zorder=3)
    for bar, val in zip(bars2, stats_values):
        ax2.text(
            bar.get_width() + max(stats_values) * 0.02, bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}s", va="center", fontweight="bold", color=COLORS["text"], fontsize=11,
        )
    ax2.set_xlabel("Seconds")
    ax2.set_title("Latency Statistics")
    ax2.invert_yaxis()

    fig.tight_layout(pad=2.0)
    fig.savefig(filepath)
    plt.close(fig)
    print(f"  [CHART] Saved: {os.path.basename(filepath)}")
    return filepath


def chart_failure_analysis(metrics: dict, output_dir: str) -> str:
    """Horizontal bar: Most common failed constraints."""
    filepath = os.path.join(output_dir, "failure_analysis.png")

    constraint_counts = Counter(metrics["failed_constraints"])
    issue_counts = Counter()
    # Simplify spatial issues to short labels
    for issue in metrics["spatial_issues_all"]:
        if "km apart" in issue.lower() or "unrealistic" in issue.lower():
            issue_counts["Distance too far"] += 1
        elif "zigzag" in issue.lower():
            issue_counts["Route zigzag"] += 1
        elif "coverage" in issue.lower():
            issue_counts["Low geocode coverage"] += 1
        elif "travel" in issue.lower() and "time" in issue.lower():
            issue_counts["Excessive travel time"] += 1
        else:
            issue_counts["Other spatial issue"] += 1

    all_failures = constraint_counts + issue_counts

    if not all_failures:
        # Create a "no failures" chart
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(
            0.5, 0.5, "No failures recorded yet! 🎉",
            ha="center", va="center", fontsize=16, color=COLORS["success"],
            transform=ax.transAxes,
        )
        ax.set_title("Failure Analysis")
        ax.set_xticks([])
        ax.set_yticks([])
        fig.savefig(filepath)
        plt.close(fig)
        print(f"  [CHART] Saved: {os.path.basename(filepath)}")
        return filepath

    # Sort by count descending, take top 10
    sorted_failures = all_failures.most_common(10)
    labels = [item[0] for item in sorted_failures]
    counts = [item[1] for item in sorted_failures]

    fig, ax = plt.subplots(figsize=(10, max(4, len(labels) * 0.6 + 1)))
    colors_list = []
    for label in labels:
        if label in constraint_counts:
            colors_list.append(COLORS["danger"])
        else:
            colors_list.append(COLORS["warning"])

    bars = ax.barh(range(len(labels)), counts, color=colors_list, height=0.6, edgecolor="none", zorder=3)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("Occurrences")
    ax.set_title("Most Common Failures (Top 10)")

    for bar, count in zip(bars, counts):
        ax.text(
            bar.get_width() + 0.15, bar.get_y() + bar.get_height() / 2,
            str(count), va="center", fontweight="bold", color=COLORS["text"], fontsize=11,
        )

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS["danger"], label="Constraint Violation"),
        Patch(facecolor=COLORS["warning"], label="Spatial Issue"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=9)

    fig.savefig(filepath)
    plt.close(fig)
    print(f"  [CHART] Saved: {os.path.basename(filepath)}")
    return filepath


def chart_per_script(metrics: dict, output_dir: str) -> str:
    """Grouped bar: Pass rates broken down by test script."""
    filepath = os.path.join(output_dir, "per_script_comparison.png")

    per_script = metrics["per_script"]
    if not per_script:
        return filepath

    scripts = list(per_script.keys())
    totals = [per_script[s]["total"] for s in scripts]
    passed = [per_script[s]["passed"] for s in scripts]
    failed = [per_script[s]["failed"] for s in scripts]
    avg_latencies = [safe_avg(per_script[s]["latencies"]) for s in scripts]
    avg_spatial = [safe_avg(per_script[s]["spatial_scores"]) for s in scripts]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Pass/Fail counts per script
    ax1 = axes[0]
    x = range(len(scripts))
    bar_width = 0.35
    bars1 = ax1.bar([i - bar_width / 2 for i in x], passed, bar_width,
                     label="Passed", color=COLORS["success"], edgecolor="none", zorder=3)
    bars2 = ax1.bar([i + bar_width / 2 for i in x], failed, bar_width,
                     label="Failed", color=COLORS["danger"], edgecolor="none", zorder=3)
    ax1.set_xticks(list(x))
    ax1.set_xticklabels([s.replace("_", "\n") for s in scripts], fontsize=9)
    ax1.set_ylabel("Count")
    ax1.set_title("Pass / Fail by Script")
    ax1.legend(fontsize=9)

    # Right: Avg latency per script
    ax2 = axes[1]
    bar_colors = [PALETTE[i % len(PALETTE)] for i in range(len(scripts))]
    bars3 = ax2.bar(range(len(scripts)), avg_latencies, color=bar_colors, width=0.5, edgecolor="none", zorder=3)
    for bar, val in zip(bars3, avg_latencies):
        if val > 0:
            ax2.text(
                bar.get_x() + bar.get_width() / 2, bar.get_height() + max(avg_latencies) * 0.02,
                f"{val:.0f}s", ha="center", va="bottom",
                fontweight="bold", color=COLORS["text"], fontsize=11,
            )
    ax2.set_xticks(range(len(scripts)))
    ax2.set_xticklabels([s.replace("_", "\n") for s in scripts], fontsize=9)
    ax2.set_ylabel("Seconds")
    ax2.set_title("Average Latency by Script")

    fig.tight_layout(pad=2.0)
    fig.savefig(filepath)
    plt.close(fig)
    print(f"  [CHART] Saved: {os.path.basename(filepath)}")
    return filepath


# ─── Console Report ─────────────────────────────────────────────────────────

def print_report(metrics: dict):
    """Print a formatted summary report to the console."""
    total = metrics["total_runs"]

    print("\n" + "=" * 70)
    print("  BENCHMARK ANALYSIS REPORT")
    print("=" * 70)

    # ── Overview ──
    print(f"\n  Total test runs:    {total}")
    print(f"  Scripts used:       {', '.join(metrics['scripts'].keys())}")
    if metrics["timestamps"]:
        dates = sorted([t for t in metrics["timestamps"] if t])
        if dates:
            print(f"  Date range:         {dates[0][:10]} -> {dates[-1][:10]}")

    # -- Validation --
    print(f"\n  -- Validation --")
    print(f"  JSON valid:         {metrics['json_valid']}/{total} ({pct(metrics['json_valid'], total)})")
    print(f"  Schema valid:       {metrics['schema_passes']}/{total} ({pct(metrics['schema_passes'], total)})")

    # -- Judge --
    judge_total = metrics["judge_passes"] + metrics["judge_fails"]
    print(f"\n  -- Judge Evaluation --")
    print(f"  Passed:             {metrics['judge_passes']}/{judge_total} ({pct(metrics['judge_passes'], judge_total)})")
    print(f"  Failed:             {metrics['judge_fails']}/{judge_total}")
    print(f"  Judge unavailable:  {metrics['judge_null']} runs")

    # -- Spatial --
    scores = metrics["spatial_scores"]
    if scores:
        print(f"\n  -- Spatial Coherence --")
        print(f"  Avg score:          {safe_avg(scores):.2f}")
        print(f"  Min / Max:          {safe_min(scores):.2f} / {safe_max(scores):.2f}")
        coverages = metrics["spatial_coverages"]
        if coverages:
            print(f"  Avg coverage:       {safe_avg(coverages):.0%}")

    # -- Latency --
    latencies = metrics["latencies"]
    if latencies:
        print(f"\n  -- Performance --")
        print(f"  Avg latency:        {safe_avg(latencies):.1f}s")
        print(f"  Min / Max:          {safe_min(latencies):.1f}s / {safe_max(latencies):.1f}s")
        print(f"  Median:             {percentile(latencies, 50):.1f}s")
        print(f"  P95:                {percentile(latencies, 95):.1f}s")

    if metrics["tool_calls"]:
        print(f"  Avg tool calls:     {safe_avg(metrics['tool_calls']):.1f}")
    if metrics["total_tokens"]:
        print(f"  Avg tokens:         {safe_avg(metrics['total_tokens']):.0f}")

    # -- Top failures --
    all_failures = Counter(metrics["failed_constraints"])
    if all_failures:
        print(f"\n  -- Top Failed Constraints --")
        for constraint, count in all_failures.most_common(5):
            print(f"    {count}x  {constraint}")

    spatial_issues = metrics["spatial_issues_all"]
    if spatial_issues:
        print(f"\n  -- Spatial Issues ({len(spatial_issues)} total) --")
        for issue in spatial_issues[:5]:
            truncated = issue[:80] + "..." if len(issue) > 80 else issue
            print(f"    - {truncated}")

    print("\n" + "=" * 70)


# ─── Markdown Report ────────────────────────────────────────────────────────

def generate_markdown_report(metrics: dict, chart_paths: dict, output_dir: str) -> str:
    """Generate a markdown report with embedded charts."""
    filepath = os.path.join(output_dir, "benchmark_report.md")
    total = metrics["total_runs"]

    lines = []
    lines.append("# Benchmark Evaluation Report")
    lines.append(f"\n_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")
    lines.append(f"\n**Total Runs Analyzed:** {total}")
    lines.append("")

    # ── Summary Table ──
    judge_total = metrics["judge_passes"] + metrics["judge_fails"]
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total test runs | {total} |")
    lines.append(f"| JSON valid | {metrics['json_valid']}/{total} ({pct(metrics['json_valid'], total)}) |")
    lines.append(f"| Schema pass rate | {metrics['schema_passes']}/{total} ({pct(metrics['schema_passes'], total)}) |")
    lines.append(f"| Judge pass rate | {metrics['judge_passes']}/{judge_total} ({pct(metrics['judge_passes'], judge_total)}) |")
    if metrics["spatial_scores"]:
        lines.append(f"| Avg spatial score | {safe_avg(metrics['spatial_scores']):.2f} |")
    if metrics["latencies"]:
        lines.append(f"| Avg latency | {safe_avg(metrics['latencies']):.1f}s |")
        lines.append(f"| Median latency | {percentile(metrics['latencies'], 50):.1f}s |")
    if metrics["tool_calls"]:
        lines.append(f"| Avg tool calls | {safe_avg(metrics['tool_calls']):.1f} |")
    lines.append("")

    # ── Charts ──
    lines.append("## Validation & Judge Pass Rates")
    lines.append("")
    if "pass_rates" in chart_paths:
        lines.append(f"![Pass Rates]({chart_paths['pass_rates']})")
    lines.append("")

    lines.append("## Spatial Coherence Distribution")
    lines.append("")
    if "spatial" in chart_paths:
        lines.append(f"![Spatial Distribution]({chart_paths['spatial']})")
    lines.append("")

    if metrics["spatial_scores"]:
        lines.append("| Statistic | Value |")
        lines.append("|-----------|-------|")
        lines.append(f"| Mean | {safe_avg(metrics['spatial_scores']):.2f} |")
        lines.append(f"| Min | {safe_min(metrics['spatial_scores']):.2f} |")
        lines.append(f"| Max | {safe_max(metrics['spatial_scores']):.2f} |")
        if metrics["spatial_coverages"]:
            lines.append(f"| Avg Coverage | {safe_avg(metrics['spatial_coverages']):.0%} |")
        lines.append("")

    lines.append("## Latency Analysis")
    lines.append("")
    if "latency" in chart_paths:
        lines.append(f"![Latency Breakdown]({chart_paths['latency']})")
    lines.append("")

    if metrics["latencies"]:
        lines.append("| Statistic | Value |")
        lines.append("|-----------|-------|")
        lines.append(f"| Min | {safe_min(metrics['latencies']):.1f}s |")
        lines.append(f"| Average | {safe_avg(metrics['latencies']):.1f}s |")
        lines.append(f"| Median | {percentile(metrics['latencies'], 50):.1f}s |")
        lines.append(f"| P95 | {percentile(metrics['latencies'], 95):.1f}s |")
        lines.append(f"| Max | {safe_max(metrics['latencies']):.1f}s |")
        lines.append("")

    lines.append("## Failure Analysis")
    lines.append("")
    if "failures" in chart_paths:
        lines.append(f"![Failure Analysis]({chart_paths['failures']})")
    lines.append("")

    constraint_counts = Counter(metrics["failed_constraints"])
    if constraint_counts:
        lines.append("### Most Common Constraint Failures")
        lines.append("")
        lines.append("| Constraint | Count |")
        lines.append("|-----------|-------|")
        for constraint, count in constraint_counts.most_common(10):
            lines.append(f"| {constraint} | {count} |")
        lines.append("")

    lines.append("## Per-Script Comparison")
    lines.append("")
    if "per_script" in chart_paths:
        lines.append(f"![Per Script]({chart_paths['per_script']})")
    lines.append("")

    per_script = metrics["per_script"]
    if per_script:
        lines.append("| Script | Runs | Passed | Failed | Avg Latency |")
        lines.append("|--------|------|--------|--------|-------------|")
        for script, data in per_script.items():
            avg_lat = f"{safe_avg(data['latencies']):.1f}s" if data["latencies"] else "N/A"
            lines.append(f"| {script} | {data['total']} | {data['passed']} | {data['failed']} | {avg_lat} |")
        lines.append("")

    # ── Notes ──
    lines.append("---")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append(f"> This report was generated from {total} benchmark entries. ")
    lines.append("> Run more tests to improve statistical significance.")
    lines.append("")

    report_text = "\n".join(lines)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"  [REPORT] Saved: {os.path.basename(filepath)}")
    return filepath


# ─── JSON Export ────────────────────────────────────────────────────────────

def generate_json_export(metrics: dict, output_dir: str) -> str:
    """Export metrics as structured JSON."""
    filepath = os.path.join(output_dir, "benchmark_report.json")

    total = metrics["total_runs"]
    judge_total = metrics["judge_passes"] + metrics["judge_fails"]

    export = {
        "generated_at": datetime.now().isoformat(),
        "total_runs": total,
        "validation": {
            "json_valid": metrics["json_valid"],
            "json_invalid": metrics["json_invalid"],
            "schema_passes": metrics["schema_passes"],
            "schema_fails": metrics["schema_fails"],
            "json_valid_rate": metrics["json_valid"] / total if total > 0 else 0,
            "schema_pass_rate": metrics["schema_passes"] / total if total > 0 else 0,
        },
        "judge": {
            "passed": metrics["judge_passes"],
            "failed": metrics["judge_fails"],
            "unavailable": metrics["judge_null"],
            "pass_rate": metrics["judge_passes"] / judge_total if judge_total > 0 else 0,
        },
        "spatial": {
            "scores": metrics["spatial_scores"],
            "avg_score": safe_avg(metrics["spatial_scores"]),
            "min_score": safe_min(metrics["spatial_scores"]),
            "max_score": safe_max(metrics["spatial_scores"]),
            "avg_coverage": safe_avg(metrics["spatial_coverages"]),
        },
        "performance": {
            "latencies": metrics["latencies"],
            "avg_latency": safe_avg(metrics["latencies"]),
            "min_latency": safe_min(metrics["latencies"]),
            "max_latency": safe_max(metrics["latencies"]),
            "median_latency": percentile(metrics["latencies"], 50),
            "p95_latency": percentile(metrics["latencies"], 95),
            "avg_tool_calls": safe_avg(metrics["tool_calls"]),
            "avg_total_tokens": safe_avg(metrics["total_tokens"]),
        },
        "failures": {
            "constraint_counts": dict(Counter(metrics["failed_constraints"]).most_common()),
            "total_spatial_issues": len(metrics["spatial_issues_all"]),
        },
        "per_script": {
            script: {
                "total": data["total"],
                "passed": data["passed"],
                "failed": data["failed"],
                "avg_latency": safe_avg(data["latencies"]),
                "avg_spatial_score": safe_avg(data["spatial_scores"]),
            }
            for script, data in metrics["per_script"].items()
        },
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)

    print(f"  [JSON] Saved: {os.path.basename(filepath)}")
    return filepath


# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  TRAVEL PLANNER BENCHMARK ANALYSIS")
    print("=" * 70)

    # Load data
    print(f"\nLoading results from: {os.path.basename(_LOG_FILE)}")
    entries = load_results(_LOG_FILE)

    if not entries:
        print("[ERROR] No benchmark data found. Run tests first.")
        print(f"  Expected file: {_LOG_FILE}")
        sys.exit(1)

    print(f"  Loaded {len(entries)} entries.")

    # Extract metrics
    metrics = extract_metrics(entries)

    # Print console report
    print_report(metrics)

    # Generate charts
    os.makedirs(_REPORTS_DIR, exist_ok=True)
    apply_chart_style()

    print(f"\nGenerating charts in: {os.path.basename(_REPORTS_DIR)}/")
    chart_paths = {}
    chart_paths["pass_rates"] = chart_pass_rates(metrics, _REPORTS_DIR)
    chart_paths["spatial"] = chart_spatial_distribution(metrics, _REPORTS_DIR)
    chart_paths["latency"] = chart_latency(metrics, _REPORTS_DIR)
    chart_paths["failures"] = chart_failure_analysis(metrics, _REPORTS_DIR)
    chart_paths["per_script"] = chart_per_script(metrics, _REPORTS_DIR)

    # Generate reports
    print("\nGenerating reports...")
    generate_markdown_report(metrics, chart_paths, _REPORTS_DIR)
    generate_json_export(metrics, _REPORTS_DIR)

    print(f"\n{'=' * 70}")
    print(f"  DONE - All outputs saved to: {os.path.relpath(_REPORTS_DIR, _SCRIPT_DIR)}/")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()

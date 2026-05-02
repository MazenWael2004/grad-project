"""
benchmark_logger.py -- Shared logging utility for benchmarking scripts.

Appends structured JSON-lines to a local log file so results can be
aggregated later for reporting.  Each entry contains:
  - timestamp (ISO-8601)
  - script name that produced the entry
  - query (if applicable)
  - results dict (varies per script)

Log file: AI_Agents/Benchmarking/benchmark_results.jsonl
"""

import json
import os
from datetime import datetime, timezone


_LOG_DIR = os.path.dirname(os.path.abspath(__file__))
_LOG_FILE = os.path.join(_LOG_DIR, "benchmark_results.jsonl")


def log_result(
    script_name: str,
    results: dict,
    query: str | None = None,
    extra: dict | None = None,
) -> None:
    """
    Append a single benchmark result entry to the log file.

    Args:
        script_name: Name of the calling script (e.g. "manual_verify_travel").
        results:     Dict of result data to persist.
        query:       The user query that was evaluated (optional).
        extra:       Any additional metadata to include (optional).
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "script": script_name,
    }

    if query is not None:
        entry["query"] = query

    entry["results"] = results

    if extra:
        entry["extra"] = extra

    with open(_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"\n[LOG] Result appended to {os.path.relpath(_LOG_FILE, _LOG_DIR)}")

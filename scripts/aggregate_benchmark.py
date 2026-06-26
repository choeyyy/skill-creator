"""Aggregate grading results into benchmark.json.

Usage:
    python aggregate_benchmark.py <evals_directory>

Reads grading files from <evals_directory>/grading/*.json and timing data from
<evals_directory>/timing.json, then writes benchmark.json to the parent directory.

TODO: Full implementation pending — statistical computations, stddev, and
edge-case handling to be completed in a future iteration.
"""

import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_grading_results(evals_dir: Path) -> list[dict]:
    """Load all grading JSON files from the grading subdirectory."""
    grading_dir = evals_dir / "grading"
    if not grading_dir.exists():
        return []
    results = []
    for f in sorted(grading_dir.glob("*.json")):
        with open(f, encoding="utf-8") as fh:
            results.append(json.loads(fh.read()))
    return results


def load_timing(evals_dir: Path) -> list[dict]:
    """Load timing data if available."""
    timing_file = evals_dir / "timing.json"
    if not timing_file.exists():
        return []
    with open(timing_file, encoding="utf-8") as fh:
        return json.loads(fh.read())


def compute_benchmark(grading: list[dict], timing: list[dict]) -> dict:
    """Compute aggregate benchmark from grading and timing data."""
    with_skill = [g for g in grading if g.get("config") == "with_skill"]
    without_skill = [g for g in grading if g.get("config") == "without_skill"]

    def stats(results: list[dict], timing_entries: list[dict], config: str) -> dict:
        pass_rates = [r.get("pass_rate", 0.0) for r in results]
        times = [t["duration_ms"] for t in timing_entries if t.get("config") == config]
        return {
            "pass_rate": statistics.mean(pass_rates) if pass_rates else 0.0,
            "mean_time_ms": statistics.mean(times) if times else 0,
            "stddev_time_ms": statistics.stdev(times) if len(times) > 1 else 0,
        }

    ws = stats(with_skill, timing, "with_skill")
    wos = stats(without_skill, timing, "without_skill")

    return {
        "with_skill": ws,
        "without_skill": wos,
        "delta": {
            "pass_rate": ws["pass_rate"] - wos["pass_rate"],
            "time_ms": ws["mean_time_ms"] - wos["mean_time_ms"],
        },
        "test_count": len(with_skill),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate eval grading into benchmark.json")
    parser.add_argument("evals_dir", type=Path, help="Path to evals/ directory")
    args = parser.parse_args()

    if not args.evals_dir.exists():
        print(f"Error: directory not found: {args.evals_dir}", file=sys.stderr)
        sys.exit(1)

    grading = load_grading_results(args.evals_dir)
    timing = load_timing(args.evals_dir)

    if not grading:
        print("Warning: no grading results found", file=sys.stderr)

    benchmark = compute_benchmark(grading, timing)
    output_path = args.evals_dir.parent / "benchmark.json"
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(benchmark, indent=2, ensure_ascii=False))

    print(f"Benchmark written to {output_path}")
    print(f"  with_skill pass_rate:    {benchmark['with_skill']['pass_rate']:.2%}")
    print(f"  without_skill pass_rate: {benchmark['without_skill']['pass_rate']:.2%}")
    print(f"  delta:                   {benchmark['delta']['pass_rate']:+.2%}")


if __name__ == "__main__":
    main()

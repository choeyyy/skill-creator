#!/usr/bin/env python3
"""Aggregate grading results into benchmark.json with summary statistics.

Usage:
    python aggregate_benchmark.py <iteration-dir> --skill-name <name>

Walks an iteration directory (e.g. workspace/iteration-1) looking for
eval-*/with_skill/ and eval-*/without_skill/ subdirectories that contain
grading.json and optionally timing.json files. Produces benchmark.json
and benchmark.md in the iteration directory.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev
from typing import Any, Dict, List, Optional, Tuple


def _safe_mean(values: List[float]) -> float:
    return mean(values) if values else 0.0


def _safe_stdev(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    return stdev(values)


def _stat_block(values: List[float]) -> Dict[str, float]:
    """Return {mean, stddev, min, max} for a list of numbers."""
    if not values:
        return {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0}
    return {
        "mean": round(_safe_mean(values), 4),
        "stddev": round(_safe_stdev(values), 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
    }


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    """Load a JSON file, returning None on any error."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def _find_eval_dirs(iteration_dir: Path) -> List[Path]:
    """Return sorted list of eval-* subdirectories."""
    if not iteration_dir.is_dir():
        return []
    return sorted(
        p for p in iteration_dir.iterdir()
        if p.is_dir() and p.name.startswith("eval-")
    )


def _collect_runs(iteration_dir: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Walk eval dirs and collect individual run results.

    Returns (runs_list, eval_names).
    """
    runs: List[Dict[str, Any]] = []
    eval_names: List[str] = []
    run_counter: Dict[str, int] = {}

    for eval_dir in _find_eval_dirs(iteration_dir):
        eval_id = eval_dir.name.removeprefix("eval-") if hasattr(str, "removeprefix") else eval_dir.name[5:]
        if eval_id not in eval_names:
            eval_names.append(eval_id)

        for config in ("with_skill", "without_skill"):
            config_dir = eval_dir / config

            grading_path = config_dir / "grading.json"
            if not grading_path.exists():
                # Also check parent-level evals/grading pattern
                alt = iteration_dir / "evals" / "grading" / f"{eval_id}-{config}.json"
                if alt.exists():
                    grading_path = alt
                else:
                    continue

            grading = _load_json(grading_path)
            if grading is None:
                print(f"  [warn] Could not parse {grading_path}", file=sys.stderr)
                continue

            summary = grading.get("summary", {})
            pass_rate = summary.get("pass_rate", 0.0)
            passed = summary.get("passed", 0)
            total = summary.get("total", 0)

            # Timing: look in several places
            time_seconds = 0.0
            tokens = 0
            timing_path = config_dir / "timing.json"
            if not timing_path.exists():
                timing_path = iteration_dir / "evals" / "timing" / f"{eval_id}-{config}.json"

            timing = _load_json(timing_path) if timing_path.exists() else None
            if timing:
                time_seconds = timing.get("total_duration_seconds", 0.0)
                tokens = timing.get("total_tokens", 0)

            # Grading-level timing fallback
            if time_seconds == 0.0 and "timing" in grading:
                dur = grading["timing"].get("duration_seconds", 0)
                if dur:
                    time_seconds = float(dur)

            counter_key = f"{eval_id}-{config}"
            run_counter[counter_key] = run_counter.get(counter_key, 0) + 1

            runs.append({
                "eval_id": eval_id,
                "eval_name": eval_id.replace("-", " ").title(),
                "configuration": config,
                "run_number": run_counter[counter_key],
                "result": {
                    "pass_rate": round(pass_rate, 4),
                    "passed": passed,
                    "total": total,
                    "time_seconds": round(time_seconds, 2),
                    "tokens": tokens,
                },
            })

    return runs, eval_names


def _summarize(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute per-config summary stats and delta."""
    config_data: Dict[str, Dict[str, List[float]]] = {
        "with_skill": {"pass_rate": [], "time_seconds": [], "tokens": []},
        "without_skill": {"pass_rate": [], "time_seconds": [], "tokens": []},
    }

    for run in runs:
        cfg = run["configuration"]
        if cfg not in config_data:
            config_data[cfg] = {"pass_rate": [], "time_seconds": [], "tokens": []}
        r = run["result"]
        config_data[cfg]["pass_rate"].append(r["pass_rate"])
        config_data[cfg]["time_seconds"].append(r["time_seconds"])
        config_data[cfg]["tokens"].append(float(r["tokens"]))

    summary: Dict[str, Any] = {}
    for cfg in ("with_skill", "without_skill"):
        d = config_data.get(cfg, {"pass_rate": [], "time_seconds": [], "tokens": []})
        summary[cfg] = {
            "pass_rate": _stat_block(d["pass_rate"]),
            "time_seconds": _stat_block(d["time_seconds"]),
            "tokens": _stat_block(d["tokens"]),
            "total_runs": len(d["pass_rate"]),
        }

    ws = summary.get("with_skill", {})
    wo = summary.get("without_skill", {})
    summary["delta"] = {
        "pass_rate": round(ws.get("pass_rate", {}).get("mean", 0) - wo.get("pass_rate", {}).get("mean", 0), 4),
        "time_seconds": round(ws.get("time_seconds", {}).get("mean", 0) - wo.get("time_seconds", {}).get("mean", 0), 2),
        "tokens": round(ws.get("tokens", {}).get("mean", 0) - wo.get("tokens", {}).get("mean", 0), 1),
    }

    return summary


def _collect_notes(iteration_dir: Path) -> List[str]:
    """Read analyzer notes if present."""
    notes: List[str] = []
    for candidate in (
        iteration_dir / "analyzer_notes.json",
        iteration_dir / "notes.json",
        iteration_dir / "evals" / "analyzer_notes.json",
    ):
        data = _load_json(candidate) if candidate.exists() else None
        if isinstance(data, list):
            notes.extend(str(n) for n in data)
    return notes


def _write_markdown(
    output_path: Path,
    skill_name: str,
    summary: Dict[str, Any],
    runs: List[Dict[str, Any]],
    notes: List[str],
) -> None:
    """Write a human-readable benchmark.md summary."""
    ws = summary.get("with_skill", {})
    wo = summary.get("without_skill", {})
    delta = summary.get("delta", {})

    def _fmt_pct(v: float) -> str:
        return f"{v * 100:.1f}%"

    def _fmt_delta(v: float) -> str:
        sign = "+" if v >= 0 else ""
        return f"{sign}{v * 100:.1f}%"

    lines = [
        f"# Benchmark — {skill_name}",
        "",
        f"*Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        "## Summary",
        "",
        "| Metric | With Skill | Without Skill | Delta |",
        "|:-------|:-----------|:--------------|:------|",
        f"| Pass Rate | {_fmt_pct(ws.get('pass_rate', {}).get('mean', 0))} | {_fmt_pct(wo.get('pass_rate', {}).get('mean', 0))} | {_fmt_delta(delta.get('pass_rate', 0))} |",
        f"| Avg Time | {ws.get('time_seconds', {}).get('mean', 0):.1f}s | {wo.get('time_seconds', {}).get('mean', 0):.1f}s | {delta.get('time_seconds', 0):+.1f}s |",
        f"| Avg Tokens | {ws.get('tokens', {}).get('mean', 0):.0f} | {wo.get('tokens', {}).get('mean', 0):.0f} | {delta.get('tokens', 0):+.0f} |",
        f"| Runs | {ws.get('total_runs', 0)} | {wo.get('total_runs', 0)} | — |",
        "",
    ]

    # Interpretation
    dp = delta.get("pass_rate", 0)
    if dp > 0.15:
        interp = "Skill provides clear value"
    elif dp >= 0.05:
        interp = "Marginal improvement — investigate which tests benefit"
    elif dp >= -0.05:
        interp = "No significant effect — skill may need rework"
    else:
        interp = "Skill is hurting performance — over-constraining the agent"
    lines.append(f"**Interpretation:** {interp}")
    lines.append("")

    # Per-eval breakdown
    if runs:
        lines.append("## Per-Eval Breakdown")
        lines.append("")
        lines.append("| Eval | Config | Pass Rate | Passed | Total | Time | Tokens |")
        lines.append("|:-----|:-------|:----------|:-------|:------|:-----|:-------|")
        for run in sorted(runs, key=lambda r: (r["eval_id"], r["configuration"])):
            r = run["result"]
            lines.append(
                f"| {run['eval_id']} | {run['configuration']} | "
                f"{_fmt_pct(r['pass_rate'])} | {r['passed']} | {r['total']} | "
                f"{r['time_seconds']:.1f}s | {r['tokens']} |"
            )
        lines.append("")

    if notes:
        lines.append("## Analyzer Notes")
        lines.append("")
        for note in notes:
            lines.append(f"- {note}")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def aggregate(iteration_dir: Path, skill_name: str) -> Dict[str, Any]:
    """Main aggregation logic. Returns the benchmark dict."""
    print(f"Scanning {iteration_dir} ...")

    runs, eval_names = _collect_runs(iteration_dir)
    if not runs:
        print("  [warn] No grading results found.", file=sys.stderr)

    summary = _summarize(runs)
    notes = _collect_notes(iteration_dir)

    # Attempt to extract iteration number from directory name
    iteration_num = 0
    parts = iteration_dir.name.split("-")
    for part in reversed(parts):
        try:
            iteration_num = int(part)
            break
        except ValueError:
            continue

    benchmark: Dict[str, Any] = {
        "metadata": {
            "skill_name": skill_name,
            "iteration": iteration_num,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "eval_count": len(eval_names),
            "evals_run": eval_names,
            "runs_per_configuration": max(
                (r["run_number"] for r in runs), default=0
            ),
        },
        "runs": runs,
        "run_summary": summary,
        "notes": notes,
    }

    return benchmark


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate eval grading results into benchmark.json",
    )
    parser.add_argument(
        "iteration_dir",
        type=Path,
        help="Path to the iteration directory (e.g. workspace/iteration-1)",
    )
    parser.add_argument(
        "--skill-name",
        required=True,
        help="Name of the skill being evaluated",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for benchmark.json (default: <iteration_dir>/benchmark.json)",
    )
    args = parser.parse_args()

    iteration_dir: Path = args.iteration_dir.resolve()
    if not iteration_dir.is_dir():
        print(f"Error: {iteration_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    benchmark = aggregate(iteration_dir, args.skill_name)

    out_json = args.output or (iteration_dir / "benchmark.json")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        json.dumps(benchmark, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {out_json}")

    out_md = out_json.with_suffix(".md")
    _write_markdown(
        out_md,
        args.skill_name,
        benchmark["run_summary"],
        benchmark["runs"],
        benchmark["notes"],
    )
    print(f"Wrote {out_md}")

    # Quick summary
    delta = benchmark["run_summary"].get("delta", {})
    dp = delta.get("pass_rate", 0)
    print(f"\nDelta pass-rate: {dp:+.1%}  |  Runs collected: {len(benchmark['runs'])}")


if __name__ == "__main__":
    main()

"""Generate an HTML review report from eval results.

Usage:
    python generate_review.py <evals_directory> [--output review.html]

Reads benchmark.json, grading results, and timing data to produce a visual
HTML report summarizing eval performance.

TODO: Full implementation pending — HTML template, charts, and detailed
per-test breakdowns to be completed in a future iteration.
"""

import argparse
import json
import sys
from pathlib import Path


HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Skill Eval Review</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; }}
    h1 {{ color: #1a1a2e; }}
    .summary {{ background: #f0f4f8; border-radius: 8px; padding: 1.5rem; margin: 1rem 0; }}
    .metric {{ display: inline-block; margin-right: 2rem; }}
    .metric .value {{ font-size: 2rem; font-weight: bold; color: #2d6a4f; }}
    .metric .label {{ color: #666; font-size: 0.9rem; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
    th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: left; }}
    th {{ background: #f8f9fa; }}
    .pass {{ color: #2d6a4f; font-weight: bold; }}
    .fail {{ color: #d62828; font-weight: bold; }}
  </style>
</head>
<body>
  <h1>Skill Eval Review</h1>
  <div class="summary">
    <div class="metric">
      <div class="value">{with_skill_rate}</div>
      <div class="label">With Skill</div>
    </div>
    <div class="metric">
      <div class="value">{without_skill_rate}</div>
      <div class="label">Without Skill</div>
    </div>
    <div class="metric">
      <div class="value">{delta}</div>
      <div class="label">Delta</div>
    </div>
  </div>
  <p>Tests run: {test_count} | Generated: {timestamp}</p>
  {details_html}
</body>
</html>
"""


def load_benchmark(evals_dir: Path) -> dict:
    """Load benchmark.json from parent of evals directory."""
    benchmark_path = evals_dir.parent / "benchmark.json"
    if not benchmark_path.exists():
        return {}
    with open(benchmark_path, encoding="utf-8") as fh:
        return json.loads(fh.read())


def generate_html(benchmark: dict) -> str:
    """Generate HTML report from benchmark data."""
    ws = benchmark.get("with_skill", {})
    wos = benchmark.get("without_skill", {})
    delta = benchmark.get("delta", {})

    return HTML_TEMPLATE.format(
        with_skill_rate=f"{ws.get('pass_rate', 0):.0%}",
        without_skill_rate=f"{wos.get('pass_rate', 0):.0%}",
        delta=f"{delta.get('pass_rate', 0):+.0%}",
        test_count=benchmark.get("test_count", 0),
        timestamp=benchmark.get("timestamp", "N/A"),
        details_html="<p><em>Detailed per-test breakdown pending implementation.</em></p>",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate HTML eval review report")
    parser.add_argument("evals_dir", type=Path, help="Path to evals/ directory")
    parser.add_argument("--output", type=Path, default=None, help="Output HTML file path")
    args = parser.parse_args()

    if not args.evals_dir.exists():
        print(f"Error: directory not found: {args.evals_dir}", file=sys.stderr)
        sys.exit(1)

    benchmark = load_benchmark(args.evals_dir)
    if not benchmark:
        print("Error: benchmark.json not found. Run aggregate_benchmark.py first.", file=sys.stderr)
        sys.exit(1)

    html = generate_html(benchmark)
    output_path = args.output or (args.evals_dir.parent / "review.html")
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(html)

    print(f"Review written to {output_path}")


if __name__ == "__main__":
    main()

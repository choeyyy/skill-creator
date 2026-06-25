#!/usr/bin/env python3
"""Generate a standalone HTML review page for qualitative eval output inspection.

Usage:
    python generate_review.py <iteration-dir> --skill-name "my-skill" \\
        [--benchmark <benchmark.json>] [--previous-workspace <path>] \\
        [--static <output.html>]

Always produces a self-contained HTML file with inline CSS/JS.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _load_json(path: Path) -> Optional[Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def _read_text(path: Path, max_bytes: int = 200_000) -> str:
    """Read a text file, truncating if very large."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_bytes:
            return text[:max_bytes] + "\n\n... [truncated] ..."
        return text
    except OSError:
        return ""


def _collect_test_cases(
    iteration_dir: Path,
    previous_dir: Optional[Path],
) -> List[Dict[str, Any]]:
    """Gather test-case data from the iteration directory."""
    cases: List[Dict[str, Any]] = []

    eval_dirs = sorted(
        (p for p in iteration_dir.iterdir() if p.is_dir() and p.name.startswith("eval-")),
    ) if iteration_dir.is_dir() else []

    for eval_dir in eval_dirs:
        eval_id = eval_dir.name[5:] if eval_dir.name.startswith("eval-") else eval_dir.name

        for config in ("with_skill", "without_skill"):
            config_dir = eval_dir / config
            if not config_dir.is_dir():
                continue

            # Collect outputs
            outputs_dir = config_dir / "outputs"
            output_files: Dict[str, str] = {}
            if outputs_dir.is_dir():
                for f in sorted(outputs_dir.iterdir()):
                    if f.is_file():
                        output_files[f.name] = _read_text(f)

            # If no outputs/ subdir, grab any non-json files directly
            if not output_files:
                for f in sorted(config_dir.iterdir()):
                    if f.is_file() and f.suffix not in (".json",):
                        output_files[f.name] = _read_text(f)

            # Grading
            grading = _load_json(config_dir / "grading.json")
            if grading is None:
                alt = iteration_dir / "evals" / "grading" / f"{eval_id}-{config}.json"
                grading = _load_json(alt)

            # Timing
            timing = _load_json(config_dir / "timing.json")
            if timing is None:
                alt = iteration_dir / "evals" / "timing" / f"{eval_id}-{config}.json"
                timing = _load_json(alt)

            # Prompt from evals.json
            prompt = ""
            evals_json = _load_json(iteration_dir / "evals" / "evals.json")
            if evals_json is None:
                evals_json = _load_json(iteration_dir.parent / "evals" / "evals.json")
            if evals_json and "evals" in evals_json:
                for e in evals_json["evals"]:
                    if e.get("id") == eval_id:
                        prompt = e.get("prompt", "")
                        break

            # Previous iteration output
            prev_outputs: Dict[str, str] = {}
            if previous_dir:
                prev_config = previous_dir / f"eval-{eval_id}" / config / "outputs"
                if prev_config.is_dir():
                    for f in sorted(prev_config.iterdir()):
                        if f.is_file():
                            prev_outputs[f.name] = _read_text(f)

            cases.append({
                "eval_id": eval_id,
                "config": config,
                "prompt": prompt,
                "outputs": output_files,
                "grading": grading,
                "timing": timing,
                "previous_outputs": prev_outputs,
            })

    return cases


def _benchmark_table_html(benchmark: Dict[str, Any]) -> str:
    """Render benchmark summary as an HTML table."""
    rs = benchmark.get("run_summary", {})
    ws = rs.get("with_skill", {})
    wo = rs.get("without_skill", {})
    delta = rs.get("delta", {})

    def _pct(v: Any) -> str:
        if isinstance(v, dict):
            v = v.get("mean", 0)
        return f"{float(v) * 100:.1f}%"

    def _num(v: Any, fmt: str = ".1f") -> str:
        if isinstance(v, dict):
            v = v.get("mean", 0)
        return f"{float(v):{fmt}}"

    def _delta_pct(v: float) -> str:
        sign = "+" if v >= 0 else ""
        return f"{sign}{v * 100:.1f}%"

    rows = [
        ("Pass Rate", _pct(ws.get("pass_rate", 0)), _pct(wo.get("pass_rate", 0)),
         _delta_pct(delta.get("pass_rate", 0))),
        ("Avg Time", _num(ws.get("time_seconds", 0)) + "s",
         _num(wo.get("time_seconds", 0)) + "s",
         f"{delta.get('time_seconds', 0):+.1f}s"),
        ("Avg Tokens", _num(ws.get("tokens", 0), ".0f"),
         _num(wo.get("tokens", 0), ".0f"),
         f"{delta.get('tokens', 0):+.0f}"),
        ("Runs", str(ws.get("total_runs", 0)),
         str(wo.get("total_runs", 0)), "—"),
    ]

    row_html = ""
    for label, a, b, d in rows:
        row_html += f"<tr><td>{label}</td><td>{a}</td><td>{b}</td><td>{d}</td></tr>\n"

    return f"""
    <table class="bench-table">
      <thead><tr><th>Metric</th><th>With Skill</th><th>Without Skill</th><th>Delta</th></tr></thead>
      <tbody>{row_html}</tbody>
    </table>"""


def _escape(text: str) -> str:
    return html.escape(text, quote=True)


def _generate_html(
    skill_name: str,
    cases: List[Dict[str, Any]],
    benchmark: Optional[Dict[str, Any]],
) -> str:
    """Build the complete standalone HTML string."""

    # Serialize cases to JSON for JS consumption
    cases_json = json.dumps(cases, ensure_ascii=False, indent=None)
    benchmark_html = _benchmark_table_html(benchmark) if benchmark else "<p>No benchmark data provided.</p>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Eval Review — {_escape(skill_name)}</title>
<style>
:root {{
  --bg: #0d1117; --surface: #161b22; --border: #30363d;
  --text: #e6edf3; --muted: #8b949e; --accent: #58a6ff;
  --green: #3fb950; --red: #f85149; --yellow: #d29922;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
       background: var(--bg); color: var(--text); line-height: 1.5; padding: 0; }}
header {{ background: var(--surface); border-bottom: 1px solid var(--border);
          padding: 16px 24px; display: flex; align-items: center; gap: 16px; }}
header h1 {{ font-size: 20px; font-weight: 600; }}
header .meta {{ color: var(--muted); font-size: 13px; }}
.tabs {{ display: flex; gap: 0; border-bottom: 2px solid var(--border);
         background: var(--surface); padding: 0 24px; }}
.tab {{ padding: 10px 20px; cursor: pointer; color: var(--muted); font-size: 14px;
        font-weight: 500; border-bottom: 2px solid transparent; margin-bottom: -2px;
        transition: color .15s, border-color .15s; }}
.tab:hover {{ color: var(--text); }}
.tab.active {{ color: var(--accent); border-bottom-color: var(--accent); }}
.panel {{ display: none; padding: 24px; max-width: 1100px; margin: 0 auto; }}
.panel.active {{ display: block; }}

/* Navigation */
.nav-bar {{ display: flex; align-items: center; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }}
.nav-bar button {{ background: var(--surface); border: 1px solid var(--border); color: var(--text);
                   padding: 6px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; }}
.nav-bar button:hover {{ border-color: var(--accent); }}
.nav-bar button:disabled {{ opacity: .4; cursor: default; }}
.nav-bar .counter {{ color: var(--muted); font-size: 13px; }}
.nav-bar select {{ background: var(--surface); border: 1px solid var(--border); color: var(--text);
                   padding: 6px 10px; border-radius: 6px; font-size: 13px; }}

/* Cards */
.card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
         margin-bottom: 16px; overflow: hidden; }}
.card-header {{ padding: 12px 16px; border-bottom: 1px solid var(--border);
                font-weight: 600; font-size: 14px; display: flex;
                justify-content: space-between; align-items: center; }}
.card-body {{ padding: 16px; }}
.badge {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px;
          font-weight: 600; text-transform: uppercase; }}
.badge-pass {{ background: rgba(63,185,80,.15); color: var(--green); }}
.badge-fail {{ background: rgba(248,81,73,.15); color: var(--red); }}
.badge-config {{ background: rgba(88,166,255,.15); color: var(--accent); }}

pre {{ background: #0d1117; border: 1px solid var(--border); border-radius: 6px;
       padding: 12px; overflow-x: auto; font-size: 13px; line-height: 1.45;
       color: var(--text); white-space: pre-wrap; word-break: break-word; max-height: 500px;
       overflow-y: auto; }}

/* Grading expectations */
.expect-list {{ list-style: none; }}
.expect-list li {{ padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 13px; }}
.expect-list li:last-child {{ border-bottom: none; }}
.expect-icon {{ margin-right: 6px; }}

/* Benchmark */
.bench-table {{ width: 100%; border-collapse: collapse; }}
.bench-table th, .bench-table td {{ padding: 10px 14px; text-align: left;
                                     border-bottom: 1px solid var(--border); font-size: 14px; }}
.bench-table th {{ color: var(--muted); font-weight: 600; }}
.bench-table td:last-child {{ font-weight: 600; }}

/* Feedback */
.feedback-area {{ width: 100%; min-height: 80px; background: var(--bg);
                  border: 1px solid var(--border); border-radius: 6px; color: var(--text);
                  padding: 10px; font-size: 13px; font-family: inherit; resize: vertical; }}
.btn-primary {{ background: var(--accent); color: #fff; border: none; padding: 10px 24px;
                border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600;
                margin-top: 12px; }}
.btn-primary:hover {{ opacity: .85; }}

/* Side-by-side */
.side-by-side {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
@media (max-width: 768px) {{ .side-by-side {{ grid-template-columns: 1fr; }} }}

.file-tab-bar {{ display: flex; gap: 0; margin-bottom: 8px; flex-wrap: wrap; }}
.file-tab {{ padding: 4px 12px; cursor: pointer; color: var(--muted); font-size: 12px;
             border: 1px solid var(--border); border-bottom: none; border-radius: 6px 6px 0 0;
             background: transparent; }}
.file-tab.active {{ color: var(--text); background: var(--surface); }}
</style>
</head>
<body>
<header>
  <h1>Eval Review</h1>
  <span class="meta">{_escape(skill_name)} &middot; Generated {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}</span>
</header>

<div class="tabs">
  <div class="tab active" data-panel="outputs">Outputs</div>
  <div class="tab" data-panel="benchmark">Benchmark</div>
  <div class="tab" data-panel="feedback">Feedback</div>
</div>

<!-- OUTPUTS PANEL -->
<div id="outputs" class="panel active">
  <div class="nav-bar">
    <button id="prev-btn" onclick="navigate(-1)">&larr; Prev</button>
    <span class="counter" id="case-counter">1 / 0</span>
    <button id="next-btn" onclick="navigate(1)">Next &rarr;</button>
    <select id="case-select" onchange="jumpTo(this.value)"></select>
  </div>
  <div id="case-content"></div>
</div>

<!-- BENCHMARK PANEL -->
<div id="benchmark" class="panel">
  <h2 style="margin-bottom:16px;">Benchmark Summary</h2>
  {benchmark_html}
</div>

<!-- FEEDBACK PANEL -->
<div id="feedback" class="panel">
  <h2 style="margin-bottom:16px;">Review Feedback</h2>
  <p style="color:var(--muted);margin-bottom:16px;font-size:13px;">
    Add feedback per test case. Click "Submit All Reviews" to save feedback.json.
  </p>
  <div id="feedback-list"></div>
  <button class="btn-primary" onclick="submitFeedback()">Submit All Reviews</button>
  <div id="feedback-status" style="margin-top:8px;color:var(--green);font-size:13px;"></div>
</div>

<script>
// --- Data ---
const CASES = {cases_json};
let currentIdx = 0;

// --- Tab switching ---
document.querySelectorAll('.tab').forEach(tab => {{
  tab.addEventListener('click', () => {{
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(tab.dataset.panel).classList.add('active');
  }});
}});

// --- Case navigation ---
function navigate(dir) {{
  currentIdx = Math.max(0, Math.min(CASES.length - 1, currentIdx + dir));
  renderCase();
}}
function jumpTo(idx) {{
  currentIdx = parseInt(idx, 10);
  renderCase();
}}

function renderCase() {{
  if (!CASES.length) {{
    document.getElementById('case-content').innerHTML = '<p style="color:var(--muted)">No test cases found.</p>';
    return;
  }}
  const c = CASES[currentIdx];
  document.getElementById('case-counter').textContent = (currentIdx + 1) + ' / ' + CASES.length;
  document.getElementById('prev-btn').disabled = currentIdx === 0;
  document.getElementById('next-btn').disabled = currentIdx === CASES.length - 1;

  // Selector
  const sel = document.getElementById('case-select');
  sel.innerHTML = CASES.map((cc, i) =>
    '<option value="' + i + '"' + (i === currentIdx ? ' selected' : '') + '>' +
    cc.eval_id + ' (' + cc.config + ')' + '</option>'
  ).join('');

  let h = '';

  // Header
  h += '<div class="card"><div class="card-header">' +
       '<span>' + esc(c.eval_id) + '</span>' +
       '<span class="badge badge-config">' + esc(c.config) + '</span></div>';
  if (c.prompt) {{
    h += '<div class="card-body"><strong>Prompt:</strong><pre>' + esc(c.prompt) + '</pre></div>';
  }}
  h += '</div>';

  // Outputs
  const files = Object.keys(c.outputs || {{}});
  if (files.length) {{
    h += '<div class="card"><div class="card-header">Output Files</div><div class="card-body">';
    h += renderFileTabs('out', files, c.outputs);
    h += '</div></div>';
  }}

  // Previous outputs
  const prevFiles = Object.keys(c.previous_outputs || {{}});
  if (prevFiles.length) {{
    h += '<div class="card"><div class="card-header">Previous Iteration Outputs</div><div class="card-body">';
    h += renderFileTabs('prev', prevFiles, c.previous_outputs);
    h += '</div></div>';
  }}

  // Grading
  if (c.grading) {{
    const g = c.grading;
    const s = g.summary || {{}};
    h += '<div class="card"><div class="card-header"><span>Grading</span>' +
         '<span class="badge ' + (s.pass_rate >= 0.8 ? 'badge-pass' : s.pass_rate >= 0.5 ? 'badge-config' : 'badge-fail') + '">' +
         ((s.pass_rate || 0) * 100).toFixed(0) + '% (' + (s.passed||0) + '/' + (s.total||0) + ')</span></div>';
    h += '<div class="card-body"><ul class="expect-list">';
    (g.expectations || []).forEach(ex => {{
      const icon = ex.passed ? '<span class="expect-icon" style="color:var(--green)">&#10003;</span>' :
                               '<span class="expect-icon" style="color:var(--red)">&#10007;</span>';
      const text = ex.text || ex.assertion || '';
      const evidence = ex.evidence || '';
      h += '<li>' + icon + '<strong>' + esc(text) + '</strong>';
      if (evidence) h += '<br><span style="color:var(--muted);font-size:12px;">' + esc(evidence) + '</span>';
      h += '</li>';
    }});
    h += '</ul></div></div>';
  }}

  document.getElementById('case-content').innerHTML = h;
  activateFileTabs();
}}

function renderFileTabs(prefix, files, data) {{
  if (files.length === 1) {{
    return '<pre>' + esc(data[files[0]]) + '</pre>';
  }}
  let h = '<div class="file-tab-bar">';
  files.forEach((f, i) => {{
    h += '<div class="file-tab' + (i === 0 ? ' active' : '') + '" data-group="' + prefix + '" data-idx="' + i + '">' + esc(f) + '</div>';
  }});
  h += '</div>';
  files.forEach((f, i) => {{
    h += '<pre class="file-panel-' + prefix + '" style="' + (i > 0 ? 'display:none' : '') + '">' + esc(data[f]) + '</pre>';
  }});
  return h;
}}

function activateFileTabs() {{
  document.querySelectorAll('.file-tab').forEach(tab => {{
    tab.onclick = function() {{
      const group = this.dataset.group;
      const idx = parseInt(this.dataset.idx);
      document.querySelectorAll('.file-tab[data-group="' + group + '"]').forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      const panels = document.querySelectorAll('.file-panel-' + group);
      panels.forEach((p, i) => {{ p.style.display = i === idx ? '' : 'none'; }});
    }};
  }});
}}

// --- Feedback ---
function buildFeedbackPanel() {{
  const container = document.getElementById('feedback-list');
  if (!CASES.length) {{
    container.innerHTML = '<p style="color:var(--muted)">No test cases to review.</p>';
    return;
  }}
  let h = '';
  CASES.forEach((c, i) => {{
    h += '<div class="card" style="margin-bottom:12px;">' +
         '<div class="card-header"><span>' + esc(c.eval_id) + ' (' + esc(c.config) + ')</span></div>' +
         '<div class="card-body">' +
         '<textarea class="feedback-area" id="fb-' + i + '" placeholder="Your feedback for this test case..."></textarea>' +
         '</div></div>';
  }});
  container.innerHTML = h;
}}

function submitFeedback() {{
  const feedback = {{}};
  CASES.forEach((c, i) => {{
    const text = document.getElementById('fb-' + i).value.trim();
    if (text) {{
      const key = c.eval_id + '-' + c.config;
      feedback[key] = {{ eval_id: c.eval_id, config: c.config, feedback: text }};
    }}
  }});
  const blob = new Blob([JSON.stringify(feedback, null, 2)], {{type: 'application/json'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'feedback.json';
  a.click();
  document.getElementById('feedback-status').textContent = 'feedback.json downloaded!';
}}

function esc(s) {{ const d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }}

// --- Init ---
renderCase();
buildFeedbackPanel();
</script>
</body>
</html>"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a standalone HTML review page for eval output inspection",
    )
    parser.add_argument(
        "iteration_dir",
        type=Path,
        help="Path to the iteration directory (e.g. workspace/iteration-1)",
    )
    parser.add_argument(
        "--skill-name",
        required=True,
        help="Name of the skill being reviewed",
    )
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=None,
        help="Path to benchmark.json (if omitted, looks in iteration dir)",
    )
    parser.add_argument(
        "--previous-workspace",
        type=Path,
        default=None,
        help="Path to previous iteration directory for diff comparison",
    )
    parser.add_argument(
        "--static",
        type=Path,
        default=None,
        help="Output path for the HTML file (default: <iteration_dir>/review.html)",
    )
    args = parser.parse_args()

    iteration_dir: Path = args.iteration_dir.resolve()
    if not iteration_dir.is_dir():
        print(f"Error: {iteration_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Load benchmark
    benchmark: Optional[Dict[str, Any]] = None
    bench_path = args.benchmark or (iteration_dir / "benchmark.json")
    if bench_path.exists():
        benchmark = _load_json(bench_path)
        if benchmark:
            print(f"Loaded benchmark from {bench_path}")

    prev_dir: Optional[Path] = None
    if args.previous_workspace:
        prev_dir = args.previous_workspace.resolve()
        if not prev_dir.is_dir():
            print(f"  [warn] Previous workspace {prev_dir} not found, ignoring", file=sys.stderr)
            prev_dir = None

    cases = _collect_test_cases(iteration_dir, prev_dir)
    print(f"Collected {len(cases)} test case(s)")

    html_content = _generate_html(args.skill_name, cases, benchmark)

    output_path = args.static or (iteration_dir / "review.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()

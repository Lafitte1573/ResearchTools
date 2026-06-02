#!/usr/bin/env python3
"""grade.py — assertion-based grader for image-to-chart runs.

Usage:
  python3 grade.py <workspace-iteration-dir>
    e.g. python3 grade.py /path/to/image-to-chart-workspace/iteration-1

Looks for runs in:
  <workspace>/eval-<N>/{with_skill,without_skill}/outputs/

Each run directory must contain:
  - chart.py     (the generated script)
  - output.png   (the rendered chart)
  - eval_metadata.json with an "assertions" array

Writes:
  <workspace>/eval-<N>/{with_skill,without_skill}/grading.json

Assertion schema (one of these `kind` values):
  - "file_exists"            : path relative to the run dir, must exist
  - "tex_contains"           : (alias for code_contains) regex pattern in chart.py
  - "code_contains"          : regex pattern in chart.py
  - "code_contains_text"     : substring in chart.py
  - "code_contains_all"      : list of substrings, all must appear
  - "code_contains_any"      : list of substrings, at least one must appear
  - "output_png_dimensions"  : (min_w, min_h) — output.png must be at least that big

grading.json output:
  {
    "eval_id": 0,
    "expectations": [
      {"text": "file_exists: chart.py", "passed": true, "evidence": "..."},
      ...
    ],
    "pass_rate": 0.83,
    "n_passed": 5,
    "n_total": 6
  }
"""
import json
import re
import sys
from pathlib import Path


def grade_assertion(run_dir: Path, assertion: dict) -> dict:
    """Return one {text, passed, evidence} entry."""
    kind = assertion["kind"]
    text = assertion.get("text") or assertion.get("name") or kind
    chart_py = run_dir / "chart.py"
    output_png = run_dir / "output.png"

    def fail(reason: str) -> dict:
        return {"text": text, "passed": False, "evidence": reason}

    def ok(reason: str) -> dict:
        return {"text": text, "passed": True, "evidence": reason}

    if kind == "file_exists":
        rel = assertion["path"]
        p = run_dir / rel
        if not p.exists():
            return fail(f"missing file: {rel}")
        if p.stat().st_size == 0:
            return fail(f"file exists but is empty: {rel}")
        return ok(f"found {rel} ({p.stat().st_size} bytes)")

    if kind in ("tex_contains", "code_contains"):
        pattern = assertion["pattern"]
        if not chart_py.exists():
            return fail("chart.py not found")
        try:
            content = chart_py.read_text()
        except Exception as e:
            return fail(f"could not read chart.py: {e}")
        if re.search(pattern, content):
            return ok(f"matched /{pattern}/ in chart.py")
        return fail(f"no match for /{pattern}/ in chart.py")

    if kind == "code_contains_text":
        needle = assertion["text"]
        if not chart_py.exists():
            return fail("chart.py not found")
        content = chart_py.read_text()
        if needle in content:
            return ok(f"found substring {needle!r} in chart.py")
        return fail(f"substring {needle!r} not found in chart.py")

    if kind == "code_contains_all":
        if not chart_py.exists():
            return fail("chart.py not found")
        content = chart_py.read_text()
        missing = [s for s in assertion["substrings"] if s not in content]
        if not missing:
            return ok(f"all {len(assertion['substrings'])} substrings present")
        return fail(f"missing substrings: {missing}")

    if kind == "code_contains_any":
        if not chart_py.exists():
            return fail("chart.py not found")
        content = chart_py.read_text()
        if any(s in content for s in assertion["substrings"]):
            return ok(f"at least one of {assertion['substrings']!r} present")
        return fail(f"none of {assertion['substrings']!r} present")

    if kind == "output_png_dimensions":
        if not output_png.exists():
            return fail("output.png not found")
        try:
            from PIL import Image  # type: ignore
        except ImportError:
            return fail("Pillow not installed; cannot read PNG dimensions")
        with Image.open(output_png) as img:
            w, h = img.size
        min_w = assertion.get("min_width", 0)
        min_h = assertion.get("min_height", 0)
        if w >= min_w and h >= min_h:
            return ok(f"output.png is {w}x{h} (>= {min_w}x{min_h})")
        return fail(f"output.png is {w}x{h}, expected >= {min_w}x{min_h}")

    return fail(f"unknown assertion kind: {kind!r}")


def grade_run(run_dir: Path) -> dict:
    """Grade a single run directory. Writes grading.json in-place."""
    metadata_path = run_dir / "eval_metadata.json"
    if not metadata_path.exists():
        return {"error": f"no eval_metadata.json in {run_dir}"}
    meta = json.loads(metadata_path.read_text())
    eval_id = meta.get("eval_id", -1)
    assertions = meta.get("assertions", [])

    results = [grade_assertion(run_dir, a) for a in assertions]
    n_passed = sum(1 for r in results if r["passed"])
    n_total = len(results)
    pass_rate = n_passed / n_total if n_total else 0.0

    out = {
        "eval_id": eval_id,
        "expectations": results,
        "pass_rate": pass_rate,
        "n_passed": n_passed,
        "n_total": n_total,
    }
    (run_dir / "grading.json").write_text(json.dumps(out, indent=2))
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: grade.py <workspace-iteration-dir>", file=sys.stderr)
        return 2
    workspace = Path(sys.argv[1])
    if not workspace.is_dir():
        print(f"not a directory: {workspace}", file=sys.stderr)
        return 1

    eval_dirs = sorted(workspace.glob("eval-*"))
    if not eval_dirs:
        print(f"no eval-* directories under {workspace}", file=sys.stderr)
        return 1

    print(f"Grading {len(eval_dirs)} evals under {workspace}")
    for eval_dir in eval_dirs:
        for config in ("with_skill", "without_skill"):
            run_dir = eval_dir / config
            if not (run_dir / "outputs").is_dir():
                # The "outputs" subdir is the convention; some workspaces put
                # chart.py directly in the run_dir. Try both.
                run_dir_alt = run_dir
            else:
                run_dir_alt = run_dir / "outputs"
            if not (run_dir_alt / "chart.py").exists():
                print(f"  [skip] {run_dir.relative_to(workspace)}: no chart.py")
                continue
            result = grade_run(run_dir_alt)
            if "error" in result:
                print(f"  [skip] {run_dir.relative_to(workspace)}: {result['error']}")
            else:
                pr = result["pass_rate"]
                print(f"  {run_dir.relative_to(workspace)}: "
                      f"{result['n_passed']}/{result['n_total']} ({pr*100:.0f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

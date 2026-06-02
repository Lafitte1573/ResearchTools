#!/usr/bin/env python3
"""Grader for image-to-latex evals.

Reads eval_metadata.json from each eval directory, evaluates the assertions
against the outputs/ contents, and writes grading.json next to the metadata.
"""

import json
import re
import sys
from pathlib import Path


def find_tex(outputs_dir: Path) -> str:
    """Concatenate the contents of all .tex files in the outputs dir."""
    parts = []
    for p in outputs_dir.rglob("*.tex"):
        try:
            parts.append(p.read_text(encoding="utf-8"))
        except Exception:
            try:
                parts.append(p.read_text(encoding="latin-1"))
            except Exception:
                pass
    return "\n".join(parts)


def file_exists(outputs_dir: Path, pattern: str) -> tuple[bool, str]:
    matches = list(outputs_dir.rglob(pattern))
    if matches:
        return True, f"found {len(matches)} file(s): {matches[0].name}"
    return False, f"no files matching {pattern!r} under {outputs_dir}"


def tex_contains(tex: str, pattern: str) -> tuple[bool, str]:
    try:
        m = re.search(pattern, tex)
        if m:
            return True, f"matched: {m.group(0)[:80]!r}"
        return False, f"pattern {pattern!r} not found"
    except re.error as e:
        return False, f"bad regex: {e}"


def tex_contains_text(tex: str, pattern: str) -> tuple[bool, str]:
    if pattern in tex:
        return True, f"substring {pattern!r} found"
    return False, f"substring {pattern!r} not found"


def tex_contains_all(tex: str, patterns: list[str]) -> tuple[bool, str]:
    missing = [p for p in patterns if p not in tex]
    if not missing:
        return True, f"all {len(patterns)} substrings present"
    return False, f"missing {len(missing)}/{len(patterns)}: {missing[:3]}"


def tex_contains_any(tex: str, patterns: list[str]) -> tuple[bool, str]:
    for p in patterns:
        try:
            if re.search(p, tex):
                return True, f"matched pattern: {p!r}"
        except re.error:
            if p in tex:
                return True, f"matched substring: {p!r}"
    return False, f"none of {len(patterns)} patterns matched"


def evaluate_assertion(a: dict, tex: str, outputs_dir: Path) -> tuple[bool, str]:
    ct = a.get("check_type", "")
    if ct == "file_exists":
        return file_exists(outputs_dir, a["pattern"])
    if ct == "tex_contains":
        return tex_contains(tex, a["pattern"])
    if ct == "tex_contains_text":
        return tex_contains_text(tex, a["pattern"])
    if ct == "tex_contains_all":
        return tex_contains_all(tex, a["patterns"])
    if ct == "tex_contains_any":
        return tex_contains_any(tex, a["patterns"])
    return False, f"unknown check_type: {ct!r}"


def grade_run(run_dir: Path, assertions: list[dict]) -> dict:
    """Grade a single run directory (e.g. with_skill/ or without_skill/)."""
    outputs = run_dir / "outputs"
    tex = find_tex(outputs) if outputs.exists() else ""

    results = []
    for a in assertions:
        passed, evidence = evaluate_assertion(a, tex, outputs)
        results.append({
            "text": a["text"],
            "passed": passed,
            "evidence": evidence,
        })

    pass_count = sum(1 for r in results if r["passed"])
    return {
        "total": len(results),
        "passed": pass_count,
        "pass_rate": pass_count / len(results) if results else 0.0,
        "expectations": results,
    }


def main():
    if len(sys.argv) != 2:
        print("usage: grade.py <iteration-dir>", file=sys.stderr)
        sys.exit(1)

    iteration_dir = Path(sys.argv[1]).resolve()
    if not iteration_dir.is_dir():
        print(f"error: not a directory: {iteration_dir}", file=sys.stderr)
        sys.exit(1)

    eval_dirs = sorted(d for d in iteration_dir.iterdir()
                       if d.is_dir() and d.name.startswith("eval-"))

    for eval_dir in eval_dirs:
        meta_path = eval_dir / "eval_metadata.json"
        if not meta_path.exists():
            print(f"skip {eval_dir.name}: no eval_metadata.json")
            continue

        meta = json.loads(meta_path.read_text())
        assertions = meta.get("assertions", [])
        if not assertions:
            print(f"skip {eval_dir.name}: no assertions")
            continue

        for run_name in ("with_skill", "without_skill"):
            run_dir = eval_dir / run_name
            if not run_dir.exists():
                continue
            grading = grade_run(run_dir, assertions)
            (run_dir / "grading.json").write_text(
                json.dumps(grading, indent=2, ensure_ascii=False)
            )
            print(f"{eval_dir.name}/{run_name}: "
                  f"{grading['passed']}/{grading['total']} passed "
                  f"({grading['pass_rate']*100:.0f}%)")


if __name__ == "__main__":
    main()

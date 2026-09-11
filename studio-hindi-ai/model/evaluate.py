"""
Evaluate the trained model on held-out Hindi coding questions:
  1. does it generate valid Python?
  2. does the code run without error?
  3. if the code has a `# output: X` comment on a print line, does actual output match?
Writes reports/eval_report.md (Hindi) and reports/eval_results.json
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate import load_model, generate_code  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
REPORTS = os.path.join(os.path.dirname(HERE), "reports")


def run_code(code: str, timeout=6):
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "gen.py")
        with open(p, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            r = subprocess.run([sys.executable, "-I", p], capture_output=True,
                               text=True, timeout=timeout, cwd=td)
            return r.returncode == 0, r.stdout.strip(), r.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "", "timeout"
        except Exception as e:
            return False, "", str(e)


def extract_expected(code: str):
    """find last '# output: X' comment -> expected string"""
    outs = re.findall(r"# output: (.+)$", code, flags=re.M)
    return outs[-1].strip() if outs else None


def close(actual, expected):
    try:
        a, e = float(actual), float(expected)
        return abs(a - e) <= max(1e-6, abs(e) * 1e-4)
    except (ValueError, TypeError):
        return str(actual).strip() == str(expected).strip()


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--ckpt", default="best.pt")
    ap.add_argument("--greedy", action="store_true", default=True)
    args = ap.parse_args()

    os.makedirs(REPORTS, exist_ok=True)
    with open(os.path.join(DATA, "docs_dev.jsonl"), encoding="utf-8") as f:
        dev = [json.loads(l) for l in f]
    import random
    random.seed(7)
    sample = random.sample(dev, min(args.n, len(dev)))

    model, tok = load_model(args.ckpt)
    results = []
    n_valid = n_run = n_exact = 0
    t0 = time.time()

    for i, item in enumerate(sample):
        q, ref = item["q"], item["code"]
        code = generate_code(model, tok, q, max_new=320, greedy=args.greedy)
        ok_run, out, err = run_code(code)
        try:
            compile(code, "<gen>", "exec")
            valid = True
        except SyntaxError:
            valid = False
        exp = extract_expected(code)
        exact = False
        if exp is not None and ok_run:
            lines = [l for l in out.splitlines() if l.strip()]
            if lines:
                exact = close(lines[-1], exp)
        n_valid += int(valid)
        n_run += int(ok_run)
        n_exact += int(exact)
        results.append({"q": q, "code": code, "valid": valid, "run": ok_run,
                        "exact": exact, "out": out[-400:], "err": err[-300:],
                        "ref": ref})
        status = "PASS" if (ok_run and (exp is None or exact)) else ("RUN" if ok_run else "FAIL")
        print(f"[{i+1}/{len(sample)}] {status}  {q[:50]}", flush=True)

    tot = len(sample)
    report = f"""# Hindi Coder - Model Evaluation Report

**Model:** {args.ckpt}
**Test set:** held-out Hindi questions (n={tot})
**Date:** {time.strftime('%Y-%m-%d %H:%M')}

## Results (Nateeje)

| Metric | Value |
|---|---|
| Valid Python (syntax theek) | {n_valid}/{tot} ({100*n_valid/tot:.0f}%) |
| Runs without error (chalta hai) | {n_run}/{tot} ({100*n_run/tot:.0f}%) |
| Output exact match | {n_exact}/{tot} ({100*n_exact/tot:.0f}%) |
| Avg gen+run time | {round((time.time()-t0)/tot,1)}s per question |

## Samples (Naye sawal par generated code)

"""
    for r in results[:12]:
        report += f"### Q: {r['q']}\n\n**Generated code:**\n```python\n{r['code']}\n```\n"
        if r["out"]:
            report += f"\n**Output:**\n```\n{r['out']}\n```\n"
        if r["err"]:
            report += f"\n**Error:**\n```\n{r['err']}\n```\n"
        report += f"\n**Status:** {'PASS' if r['exact'] or (r['run'] and not r['valid']) else ('RUN-OK' if r['run'] else 'FAIL')}\n\n---\n\n"

    with open(os.path.join(REPORTS, "eval_report.md"), "w", encoding="utf-8") as f:
        f.write(report)
    with open(os.path.join(REPORTS, "eval_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print(f"\nDONE: valid={n_valid}/{tot} run={n_run}/{tot} exact={n_exact}/{tot}")
    print("report:", os.path.join(REPORTS, "eval_report.md"))


if __name__ == "__main__":
    main()

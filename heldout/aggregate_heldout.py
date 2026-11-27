"""Recompute the held-out tables from results/*.csv (standard library only).

    python3 heldout/aggregate_heldout.py
"""
import csv
import math
from pathlib import Path

HERE = Path(__file__).parent
MODELS = ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5", "claude-fable-5-2"]
FOCUS = ["名字様", "一般手順", "文字起こし崩れ", "発売済み機能", "問題なし"]


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def load(m, v):
    with open(HERE / "results" / f"judgments_{m}_{v}.csv", encoding="utf-8") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def cell(k, n):
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {k / max(1, n):.1%} [{lo:.1%}–{hi:.1%}]"


print("| type | model | v1 | v2 |\n|---|---|---|---|")
for ct in FOCUS + ["VIOLATIONS (gold = deduct)"]:
    for m in MODELS:
        a, b = load(m, "v1"), load(m, "v2")
        if ct.startswith("VIOL"):
            ids = [i for i in a if i in b and a[i]["gold_deduct"] == "1"]
        else:  # false deductions: only conversations of this type whose gold is "no deduction" (label revisions respected)
            ids = [i for i in a if i in b and a[i]["case_type"] == ct and a[i]["gold_deduct"] == "0"]
        k1 = sum(a[i]["deduct"] == "1" for i in ids)
        k2 = sum(b[i]["deduct"] == "1" for i in ids)
        print(f"| {ct} | {m} | {cell(k1, len(ids))} | {cell(k2, len(ids))} |")

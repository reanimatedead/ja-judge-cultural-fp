"""outputs/<model>_<before|after>.csv を正解と比べて採点する。

使い方: python3 score.py
出力: 一致率・Cohenのκ（95%ブートストラップ区間）・precision/recall・種類別の誤減点
"""
import csv
import io
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score, precision_score, recall_score

HERE = Path(__file__).parent
gold = pd.read_csv(HERE / "cases.csv")[["id", "case_type", "split", "gold"]]


def load(path):
    """モデルの出力からCSV行だけ拾う（前後の説明文や```を無視）。"""
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*(C\d{2})\s*,\s*([01])\s*,\s*(\d)", line)
        if m:
            rows.append({"id": m[1], "deduct": int(m[2]), "criterion": int(m[3])})
    df = pd.DataFrame(rows).drop_duplicates("id", keep="last")
    return df


def kappa_ci(y, p, n=1500, seed=0):
    rng = np.random.default_rng(seed)
    y, p = np.asarray(y), np.asarray(p)
    vals = []
    for _ in range(n):
        idx = rng.integers(0, len(y), len(y))
        if len(set(y[idx])) < 2:
            continue
        # 判定器が全件同じ答えのときκは0（偶然以上の一致なし）
        vals.append(0.0 if len(set(p[idx])) < 2 else cohen_kappa_score(y[idx], p[idx]))
    return np.percentile(vals, [2.5, 97.5]) if vals else (float("nan"), float("nan"))


def summarize(df, label):
    y, p = df.gold, df.deduct
    k = 0.0 if p.nunique() < 2 else cohen_kappa_score(y, p)
    lo, hi = kappa_ci(y, p)
    return {
        "対象": label, "件数": len(df),
        "一致率": f"{(y == p).mean():.0%}",
        "κ": f"{k:.2f}", "κ95%区間": f"{lo:.2f}–{hi:.2f}",
        "precision": f"{precision_score(y, p, zero_division=0):.2f}",
        "recall": f"{recall_score(y, p, zero_division=0):.2f}",
        "誤減点": int(((y == 0) & (p == 1)).sum()),
        "見逃し": int(((y == 1) & (p == 0)).sum()),
    }


def main():
    results, fp_rows = [], []
    for path in sorted((HERE / "outputs").glob("*.csv")):
        model, cond = path.stem.rsplit("_", 1)
        out = load(path)
        df = gold.merge(out, on="id", how="left")
        missing = df.deduct.isna().sum()
        if missing:
            print(f"!! {path.name}: {missing}件の出力が欠けています -> 欠けた分は採点から除外")
        df = df.dropna(subset=["deduct"])
        df["deduct"] = df.deduct.astype(int)
        test = df[df.split == "test"]
        for label, sub in [(f"全{len(df)}件", df), (f"test{len(test)}件", test)]:
            r = summarize(sub, label)
            results.append({"モデル": model, "条件": cond, **r})
        neg = df[df.gold == 0]
        for t, g in neg.groupby("case_type"):
            fp_rows.append({"モデル": model, "条件": cond, "種類": t,
                            "減点不要の件数": len(g), "誤減点": int(g.deduct.sum())})

    pd.set_option("display.width", 200)
    res = pd.DataFrame(results)
    fp = pd.DataFrame(fp_rows)
    print(res.to_string(index=False))
    print()
    if len(fp):
        print(fp.pivot_table(index="種類", columns=["モデル", "条件"], values="誤減点", aggfunc="sum").to_string())
    res.to_csv(HERE / "results_summary.csv", index=False)
    fp.to_csv(HERE / "results_false_deductions.csv", index=False)


if __name__ == "__main__":
    main()

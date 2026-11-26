"""繰り返し実行（r1〜r3）をモデル×条件ごとにまとめる。

出力: 実行回数、κの最小〜最大、平均の誤減点・見逃し、種類別の誤減点が出た回数
"""
import re
from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score

from score import gold, load

HERE = Path(__file__).parent
rows, type_rows = [], []
for path in sorted((HERE / "outputs").glob("*.csv")):
    name, cond = path.stem.rsplit("_", 1)
    model = re.sub(r"-r\d+$", "", name)
    df = gold.merge(load(path), on="id", how="inner")
    y, p = df.gold, df.deduct.astype(int)
    k = 0.0 if p.nunique() < 2 else cohen_kappa_score(y, p)
    rows.append({"model": model, "cond": cond, "run": name, "kappa": k,
                 "fp": int(((y == 0) & (p == 1)).sum()), "fn": int(((y == 1) & (p == 0)).sum())})
    for t, g in df[df.gold == 0].groupby("case_type"):
        type_rows.append({"model": model, "cond": cond, "run": name, "type": t,
                          "fp": int(g.deduct.astype(int).sum()), "n": len(g)})

r = pd.DataFrame(rows)
summary = r.groupby(["model", "cond"]).agg(
    実行回数=("run", "count"),
    κ最小=("kappa", "min"), κ最大=("kappa", "max"),
    誤減点平均=("fp", "mean"), 見逃し平均=("fn", "mean"),
).round(2)
print(summary.to_string())
print()
t = pd.DataFrame(type_rows)
t["出た"] = t.fp > 0
by_type = t.groupby(["model", "cond", "type"]).agg(
    誤減点の平均=("fp", "mean"), 誤減点が出た回数=("出た", "sum"), 実行回数=("run", "count"), 減点不要の件数=("n", "first"),
).round(1)
print(by_type.to_string())
summary.to_csv(HERE / "results_by_model.csv")
by_type.to_csv(HERE / "results_by_type.csv")

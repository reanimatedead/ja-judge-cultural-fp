"""Label audit (2026-11-27): apply the confirmed identity-verification rule to the 999 (v2) and 300 (held-out) sets,
then rebuild every table from the saved judgments (no API calls).

Rule: identity is verified only when the customer actually answers their name plus one registered detail and the
agent checks it. A vague answer or no answer followed by "確認が取れました" is not verification.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from ..core import ROOT, write_jsonl

RULE_JA = ("本人確認は、顧客が「氏名＋登録情報1項目（登録メール・電話番号・会員番号・生年月日など）」を実際に答え、"
           "担当が照合した場合のみ可とする。曖昧な回答（「登録したメールです」等）や無回答のまま「確認が取れました」とするのは不可。")
GAP = "生成時に意図しない本人確認不足が混入（{}）。正解付けの規則（氏名＋登録情報1項目を顧客が実際に答え、担当が照合した場合のみ可）により減点（基準5）に修正"

HELDOUT = {
    "H0110": GAP.format("名前を尋ねたが答えを得ないまま契約を扱った"),
    "H0200": GAP.format("名前を尋ねたが答えを得ないまま登録情報を扱った"),
    "H0158": GAP.format("氏名と生年月日を尋ねたが答えを得ないまま請求を扱った"),
}
HELDOUT_KEEP_VIOLATION = {  # gold already "deduct"; note why it stays
    "H0220": "登録電話番号のみ（登録情報1項目・氏名なし）で契約を扱った。正解付けの規則により減点（基準5）のまま",
}
V2_999 = {
    "C0005": GAP.format("登録メールを答えないまま請求を扱った"),
    "C0011": GAP.format("登録メールを答えないまま登録メールを変更した"),
    "C0014": GAP.format("登録メールを答えないまま解約を扱った"),
    "C0040": GAP.format("氏名・生年月日の回答がないまま解約を扱った"),
    "C0129": GAP.format("氏名を答えず、メールの先頭だけで請求を扱った"),
    "C0138": GAP.format("氏名を答えず、メールの先頭だけで請求を扱った"),
    "C0275": GAP.format("登録メールを答えないまま請求を扱った"),
    "C0347": GAP.format("氏名・生年月日の月の回答がないまま請求を扱った"),
    "C0845": GAP.format("確認用の情報を具体的に答えないまま登録メールを変更した"),
    "C0882": GAP.format("登録メールを答えないまま請求を扱った"),
    "C0948": GAP.format("登録メールを答えないまま登録メールの変更を進めた"),
}


def apply(path: Path, revisions: dict[str, str], keep: dict[str, str] | None = None) -> list[dict]:
    dataset = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l]
    for d in dataset:
        if d["id"] in revisions:
            d.setdefault("gold_deduct_original", d["gold_deduct"])
            d["gold_deduct"], d["gold_criterion"], d["label_note"] = 1, 5, revisions[d["id"]]
        elif keep and d["id"] in keep:
            d["gold_deduct"], d["gold_criterion"], d["label_note"] = 1, 5, keep[d["id"]]
            if d.get("gold_deduct_original") == 1:
                d.pop("gold_deduct_original")
    write_jsonl(path, dataset)
    return dataset


def resync_csv_gold(results: Path, dataset: list[dict]) -> None:
    gold = {d["id"]: d["gold_deduct"] for d in dataset}
    for f in results.glob("judgments_*.csv"):
        rows = list(csv.DictReader(open(f, encoding="utf-8")))
        for r in rows:
            r["gold_deduct"] = gold[r["id"]]
        with open(f, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)


def rebuild_999(repo: Path, job: dict) -> dict:
    from . import evals_v2
    from .evals import aggregate, load_results
    dataset = apply(repo / "data" / "conversations.jsonl", V2_999)
    _, v1 = load_results(repo)
    _, v2 = load_results(repo, "_v2")
    s1 = aggregate(dataset, v1, repo)
    s2 = aggregate(dataset, v2, repo / "v2")
    for p in (repo / "v2" / "results").glob("*.csv"):
        p.unlink()
    (repo / "v2" / "results").rmdir()
    resync_csv_gold(repo / "results", dataset)
    diff = evals_v2.compare(dataset, v1, v2, repo)
    (repo / "tables" / "summary.json").write_text(json.dumps(s1, ensure_ascii=False, indent=2))
    (repo / "v2" / "tables" / "summary.json").write_text(json.dumps(s2, ensure_ascii=False, indent=2))
    evals_v2.write_readme(repo, dataset, s1, s2, diff, job)
    return diff


def rebuild_heldout(repo: Path) -> dict:
    from .evals_heldout import compare, write_tables
    dataset = apply(repo / "data" / "conversations.jsonl", HELDOUT, HELDOUT_KEEP_VIOLATION)
    resync_csv_gold(repo / "results", dataset)
    models = ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5", "claude-fable-5-2"]
    res = {}
    for m in models:
        for v in ("v1", "v2"):
            rows = csv.DictReader(open(repo / "results" / f"judgments_{m}_{v}.csv", encoding="utf-8"))
            res[(m, v)] = {r["id"]: {"deduct": int(r["deduct"]), "criterion": int(r["criterion"])} for r in rows}
    t = compare(dataset, res, models)
    write_tables(repo, dataset, t, models, {})
    return t


if __name__ == "__main__":
    import yaml
    job = yaml.safe_load((ROOT / "jobs" / "evals_v2.yaml").read_text(encoding="utf-8"))
    d999 = rebuild_999(ROOT / "outputs" / "2026-11" / "evals" / "ja-cs-judge-evals", job)
    dh = rebuild_heldout(ROOT / "outputs" / "2026-11" / "evals_heldout" / "ja-cs-judge-evals-heldout")
    print(json.dumps({"999_violations": d999["_violations"], "999_surname": d999["名字様"],
                      "heldout_violations": dh["violations"], "heldout_surname": dh["by_type"]["名字様"]},
                     ensure_ascii=False, indent=1, default=str))

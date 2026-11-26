"""cases.py から、ID付きデータ・dev/test分割・判定プロンプトを作る。"""
import csv
import random
from collections import defaultdict
from pathlib import Path

from cases import CASES

random.seed(20261126)
OUT = Path(__file__).parent

# 種類ごとに dev/test を約6:4で層化分割
by_type = defaultdict(list)
for c in CASES:
    by_type[c["case_type"]].append(c)
for items in by_type.values():
    random.shuffle(items)
    n_test = round(len(items) * 0.4)
    for i, c in enumerate(items):
        c["split"] = "test" if i < n_test else "dev"

# 判定器が順番から種類を推測できないよう、全体をシャッフルしてIDを振る
order = CASES[:]
random.shuffle(order)
for i, c in enumerate(order, 1):
    c["id"] = f"C{i:02d}"

with open(OUT / "cases.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["id", "case_type", "split", "gold", "why", "text"])
    w.writeheader()
    for c in order:
        w.writerow({k: c[k] for k in w.fieldnames})

RUBRIC = """あなたはカスタマーサポートの品質監査員です。以下の評価基準で、各会話の「担当」の対応を監査してください。

【評価基準】1つでも満たしていなければ「減点」
1. 呼称：顧客をファーストネーム（下の名前）で呼び、親しみのある対応をしている
2. 機密：未発表の製品・機能の情報を話していない
3. 手順：社内手順書（下記）に沿って案内している
4. 言葉遣い：丁寧な言葉遣いをしている
5. 本人確認：アカウント情報を扱う前に本人確認をしている
6. 正確さ：誤った情報や、できない約束をしていない

【社内手順書（抜粋）】
- アプリが起動しない／表示されない：アプリのバージョンを確認 → 解決しなければ二次窓口へ転送
- 接続できない：アプリから再接続 → 解決しなければ二次窓口へ転送
- 動作が遅い：二次窓口へ転送

【社内ナレッジ（正しい情報）】
- ソラバンド2：50メートル防水（手洗い・水泳は可、お湯・サウナは不可）
- ミドリクラウド：月の途中で解約しても、その月の料金は返金しない
- 修理：通常5営業日かかる。期日の確約はしない
"""

CORRECTION = """
【補正ルール】（評価基準より優先する）
A. 日本の顧客を「名字＋様」で呼ぶのは丁寧な呼称であり、基準1を満たす。呼び捨てやため口は減点。
B. 会話の中で発売済み・提供中と述べられている製品や機能は、未発表として扱わない。基準2で減点するのは、担当者が自ら未公表・内緒と述べる情報を話した場合だけ。
C. 再起動・キャッシュ削除・通信の切り替え・更新・再ログインなど、公開されている一般的で安全な手順は、社内手順書になくても基準3の違反としない。データが消える操作を警告なしに勧めたり、非公式なツールを勧めたりした場合は減点。
D. 会話は音声認識による文字起こしである。ローマ字化・英語の混入・誤変換・途切れなど、文字起こしの崩れは担当者の言葉遣いの問題として扱わない。担当者自身の乱暴な言葉は減点。
"""

OUTPUT_SPEC = """
【出力形式】
説明や前置きは書かず、次のCSVだけを出力してください（1会話1行、見出し行あり）。
id,deduct,criterion
- deduct：減点なら1、減点なしなら0
- criterion：減点の場合はいちばん主な基準の番号（1〜6）、減点なしなら0
"""


def conversations(cases):
    return "\n\n".join(f"### {c['id']}\n{c['text']}" for c in cases)


batches = [order[:25], order[25:]]
for cond, extra in [("before", ""), ("after", CORRECTION)]:
    for bi, batch in enumerate(batches, 1):
        prompt = RUBRIC + extra + OUTPUT_SPEC + "\n【会話】\n\n" + conversations(batch) + "\n"
        (OUT / f"prompt_{cond}_{bi}.txt").write_text(prompt, encoding="utf-8")

    # 50件まとめた版（ブラウザのチャットにはこちらを1回で貼る）
    all_prompt = RUBRIC + extra + OUTPUT_SPEC + "\n【会話】\n\n" + conversations(order) + "\n"
    (OUT / f"prompt_{cond}_all.txt").write_text(all_prompt, encoding="utf-8")

counts = defaultdict(lambda: [0, 0])
for c in order:
    counts[(c["case_type"], c["split"])][c["gold"]] += 1
for k in sorted(counts):
    print(k, "gold0/gold1 =", counts[k])
print("total", len(order), "positives", sum(c["gold"] for c in order))

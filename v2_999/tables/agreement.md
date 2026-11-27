# 正解との一致（全モデル共通に判定できた会話のみ）

対象: 995 件

| judge | 一致率 | Cohen's κ | 減点の適合率 | 違反の再現率 | 文化差誤減点 (件/対象) |
|---|---|---|---|---|---|
| claude-fable-5-2 | 0.733 | 0.489 | 0.537 | 0.974 | 260 / 549 |
| claude-haiku-5-5 | 0.710 | 0.457 | 0.515 | 0.987 | 279 / 549 |
| claude-opus-5-5 | 0.733 | 0.493 | 0.536 | 0.993 | 263 / 549 |
| claude-sonnet-5-5 | 0.755 | 0.528 | 0.558 | 0.993 | 244 / 549 |

# ジャッジ間の一致（同じルーブリック、減点するか否か）

| pair | 一致率 | Cohen's κ |
|---|---|---|
| claude-fable-5-2 vs claude-haiku-5-5 | 0.888 | 0.772 |
| claude-fable-5-2 vs claude-opus-5-5 | 0.980 | 0.959 |
| claude-fable-5-2 vs claude-sonnet-5-5 | 0.952 | 0.902 |
| claude-haiku-5-5 vs claude-opus-5-5 | 0.901 | 0.796 |
| claude-haiku-5-5 vs claude-sonnet-5-5 | 0.903 | 0.801 |
| claude-opus-5-5 vs claude-sonnet-5-5 | 0.958 | 0.914 |

全ジャッジが一致: 0.868

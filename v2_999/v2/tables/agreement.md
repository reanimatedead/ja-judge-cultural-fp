# 正解との一致（全モデル共通に判定できた会話のみ）

対象: 999 件

| judge | 一致率 | Cohen's κ | 減点の適合率 | 違反の再現率 | 文化差誤減点 (件/対象) |
|---|---|---|---|---|---|
| claude-haiku-5-5 | 0.965 | 0.919 | 0.896 | 1.000 | 29 / 549 |
| claude-sonnet-5-5 | 0.977 | 0.946 | 0.929 | 1.000 | 19 / 549 |
| claude-opus-5-5 | 0.981 | 0.956 | 0.940 | 1.000 | 11 / 549 |
| claude-fable-5-2 | 0.990 | 0.976 | 0.968 | 1.000 | 7 / 549 |

# ジャッジ間の一致（同じルーブリック、減点するか否か）

| pair | 一致率 | Cohen's κ |
|---|---|---|
| claude-haiku-5-5 vs claude-sonnet-5-5 | 0.966 | 0.923 |
| claude-haiku-5-5 vs claude-opus-5-5 | 0.966 | 0.923 |
| claude-haiku-5-5 vs claude-fable-5-2 | 0.967 | 0.925 |
| claude-sonnet-5-5 vs claude-opus-5-5 | 0.982 | 0.959 |
| claude-sonnet-5-5 vs claude-fable-5-2 | 0.983 | 0.961 |
| claude-opus-5-5 vs claude-fable-5-2 | 0.987 | 0.970 |

全ジャッジが一致: 0.954

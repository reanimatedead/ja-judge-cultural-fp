# 正解との一致（全モデル共通に判定できた会話のみ）

対象: 999 件

| judge | 一致率 | Cohen's κ | 減点の適合率 | 違反の再現率 | 文化差誤減点 (件/対象) |
|---|---|---|---|---|---|
| claude-fable-5-2 | 0.991 | 0.979 | 0.987 | 0.984 | 7 / 549 |
| claude-haiku-5-5 | 0.964 | 0.918 | 0.910 | 0.981 | 29 / 549 |
| claude-opus-5-5 | 0.988 | 0.972 | 0.969 | 0.994 | 11 / 549 |
| claude-sonnet-5-5 | 0.986 | 0.968 | 0.960 | 0.997 | 19 / 549 |

# ジャッジ間の一致（同じルーブリック、減点するか否か）

| pair | 一致率 | Cohen's κ |
|---|---|---|
| claude-fable-5-2 vs claude-haiku-5-5 | 0.967 | 0.925 |
| claude-fable-5-2 vs claude-opus-5-5 | 0.987 | 0.970 |
| claude-fable-5-2 vs claude-sonnet-5-5 | 0.983 | 0.961 |
| claude-haiku-5-5 vs claude-opus-5-5 | 0.966 | 0.923 |
| claude-haiku-5-5 vs claude-sonnet-5-5 | 0.966 | 0.923 |
| claude-opus-5-5 vs claude-sonnet-5-5 | 0.982 | 0.959 |

全ジャッジが一致: 0.954

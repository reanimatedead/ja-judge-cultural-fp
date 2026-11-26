#!/bin/zsh
# 同じ指示文を新しいセッションで繰り返し、判定のぶれ（再現性）を見る
cd "$(dirname "$0")"
for r in 2 3; do
  for cond in before after; do
    claude -p --output-format json < prompt_${cond}_all.txt > raw/claude-r${r}_${cond}.json 2>/dev/null
    python3 -c "import json;d=json.load(open('raw/claude-r${r}_${cond}.json'));print(d.get('result',''))" > outputs/claude-r${r}_${cond}.csv
  done
done
echo DONE > raw/claude_repeat_done.txt

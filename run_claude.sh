#!/bin/zsh
# Claude Code (claude -p) で補正前・補正後の判定を実行し、outputs/ に保存する
cd "$(dirname "$0")"
mkdir -p outputs raw
for cond in before after; do
  claude -p --output-format json < prompt_${cond}_all.txt > raw/claude_${cond}.json 2> raw/claude_${cond}.err
  python3 -c "import json;d=json.load(open('raw/claude_${cond}.json'));print(d.get('result',''))" > outputs/claude_${cond}.csv
done
echo DONE > raw/claude_done.txt

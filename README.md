# ja-judge-cultural-fp

Do LLM judges penalize Japanese customer-support agents for things that are *normal in Japan*?
This repo measures false deductions by LLM-as-a-judge on 50 **synthetic** Japanese support conversations,
with 4 models × repeated runs, before and after adding 4 lines of correction rules.

All conversations, companies and products are fictional. No real customer data is used.

## Key findings (Nov 2026)

| Judge | Condition | Runs | Cohen's κ (min–max) | Mean false deductions |
|---|---|---|---|---|
| Claude (claude-opus-4-8, Claude Code CLI) | baseline | 3 | 0.86 | 3.0 |
| Claude | + correction rules | 3 | 1.00 | 0.0 |
| DeepSeek (web) | baseline | 3 | 0.54–0.78 | 6.3 |
| DeepSeek | + correction rules | 3 | 1.00 | 0.0 |
| Gemini (web, auto mode) | baseline | 3 | 0.44–0.86 | 10.7 |
| Gemini | + correction rules | 3 | 0.95–1.00 | 0.7 |
| Qwen3.7-Plus (web, auto) | baseline | 2 | 0.00–0.47 | 25.0 |
| Qwen | + correction rules | 2 | 0.95–1.00 | 0.0 (0.5 misses) |

1. **Run-to-run instability.** With the identical prompt, Gemini (2/3 runs), DeepSeek (1/3) and Qwen (2/2) penalized all 7 conversations where the agent addressed the customer as *surname + 様* (the polite norm in Japan); other runs did not. Claude never did.
2. **"Not in the internal procedure" = violation** was the one error shared by every model in every baseline run (restart, clear cache, update).
3. **Literal rubric application.** The rubric deliberately translates a common global template ("address the customer by first name"). In one run Qwen applied it to every conversation and penalized all 50.
4. **Correction rules work, except where rules collide.** Gemini still penalized one case in 2/3 runs where the procedure ("slow device → escalate") conflicts with correction rule C. Qwen missed a privacy leak in 1/2 corrected runs — check misses, not only false deductions, after adding rules.

## Files

| File | What it is |
|---|---|
| `cases.py` | 50 synthetic conversations with designed ground truth |
| `build.py` | Shuffles IDs, stratified dev/test split, writes prompts (`prompt_before_all.txt`, `prompt_after_all.txt`) |
| `score.py` | Agreement, Cohen's κ with bootstrap 95% CI, precision/recall, false deductions by type |
| `aggregate.py` | Summarizes repeated runs per model and condition |
| `run_claude.sh`, `run_claude_repeat.sh` | Runs Claude Code headless (`claude -p`) |
| `outputs/` | Raw CSV outputs of every run (`<model>[-rN]_<before|after>.csv`) |

Prompt SHA-256: before `404ed03b…5b7900`, after `259fec6f…a5bf24`. Browser runs were checked against these hashes before sending.

## Reproduce

```bash
python3 build.py        # writes cases.csv and prompts
./run_claude.sh         # or paste prompt_*_all.txt into any chat UI and save the CSV to outputs/
python3 score.py
python3 aggregate.py
```

## Limitations

- Conversations, ground truth and correction rules were written by the same author, so post-correction scores are optimistic.
- Ground truth is designed, not independently annotated; no human–human baseline.
- n = 50 and 1–3 runs per condition; κ intervals are wide.
- Web UIs do not pin model versions or sampling settings.

## License

MIT

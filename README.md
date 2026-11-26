# ja-judge-cultural-fp

Do LLM judges penalize Japanese customer-support agents for things that are *normal in Japan*?
This repo measures false deductions by LLM-as-a-judge on 50 **synthetic** Japanese support conversations,
with 4 models × repeated runs, before and after adding 4 lines of correction rules.

All conversations, companies and products are fictional. No real customer data is used.

Write-up (Japanese): https://zenn.dev/quent/articles/2329d74464eff5

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
| `build.py` | Shuffles IDs and writes prompts (`prompt_before_all.txt`, `prompt_after_all.txt`). The `split` column (dev/test) is kept for future use but was not used here: the correction rules came from prior field experience, not from tuning on this data |
| `score.py` | Agreement, Cohen's κ with bootstrap 95% CI, precision/recall, false deductions by type |
| `aggregate.py` | Summarizes repeated runs per model and condition (`--exclude-ambiguous` for the sensitivity check) |
| `review.csv` | Post-publication review of contested ground-truth labels |
| `run_claude.sh`, `run_claude_repeat.sh` | Runs Claude Code headless (`claude -p`) |
| `outputs/` | Raw CSV outputs of every run (`<model>[-rN]_<before|after>.csv`) |

Prompt SHA-256: before `404ed03b…5b7900`, after `259fec6f…a5bf24`. Browser runs were checked against these hashes before sending. Exception: Gemini's input box adds line breaks on paste (6,354 → 6,646 characters as displayed), so Gemini may have received different line breaks.

Single-run κ intervals are wide: bootstrap 95% CI for run 1 was 0.68–1.00 (Claude baseline), 0.55–0.95 (DeepSeek baseline), 0.27–0.68 (Gemini baseline).

## Reproduce

```bash
python3 build.py        # writes cases.csv and prompts
./run_claude.sh         # or paste prompt_*_all.txt into any chat UI and save the CSV to outputs/
python3 score.py
python3 aggregate.py
```

## Ground-truth review

Conversations and ground truth were drafted with an AI assistant (Claude). After publication, every case where any judge disagreed with the ground truth (38 cases) was reviewed (`review.csv`); no labels were changed. Two cases that looked contestable (C31: the procedure says "escalate" for slow devices; C46: the agent may have viewed account settings without identity verification) were re-read by the author, a practitioner who validates AI audit decisions at work, and both were confirmed as "no deduction". Excluding them (`python3 aggregate.py --exclude-ambiguous`) leaves the conclusions unchanged. Only these two cases were independently re-checked, not all 50.

## Limitations

- Conversations, ground truth and correction rules came from the same side (AI-drafted, author-checked), so post-correction scores are optimistic.
- Ground truth is designed, not independently annotated; no human–human baseline.
- n = 50 and 1–3 runs per condition; κ intervals are wide.
- Web UIs do not pin model versions or sampling settings.

## License

MIT

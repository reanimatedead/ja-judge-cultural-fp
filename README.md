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
   Because criterion 1 here is an unconditional requirement, penalizing surname + 様 (and Qwen's 50/50) is literal compliance with the rubric, not necessarily a cultural misreading. "False deduction" in this repo means disagreement with the Japanese practitioner ground truth.
4. **Correction rules work, except where rules collide.** Gemini still penalized one case in 2/3 runs where the procedure ("slow device → escalate") conflicts with correction rule C. Qwen missed a privacy leak in 1/2 corrected runs — check misses, not only false deductions, after adding rules.

## Follow-up: v2 (999 conversations, regional-norm notes)

A larger follow-up re-ran the question on **999 synthetic** conversations with 4 Claude judges (Haiku 5.5, Sonnet 5.5, Opus 5.5, Fable 5.2; Message Batches API).
v1 is the translated "global template" rubric (criterion 1 scoped to "when the agent uses the customer's name"); v2 adds three regional-norm notes
(surname + 様 is correct / safe generic troubleshooting is allowed / speech-to-text artifacts are not the agent's language problem).
Rate = share of conversations penalized, with Wilson 95% CI. Gold = no deduction in all three categories.

| Category (n) | Judge | v1 | v2 | Diff (pp) |
|---|---|---|---|---|
| surname + 様 (199) | Haiku 5.5 | 93.0% [88.5–95.8] | 2.5% [1.1–5.7] | −90.5 |
| | Sonnet 5.5 | 99.5% [97.2–99.9] | 2.5% [1.1–5.7] | −97.0 |
| | Opus 5.5 | 100.0% [98.1–100.0] | 1.0% [0.3–3.6] | −99.0 |
| | Fable 5.2 | 100.0% [98.1–100.0] | 1.0% [0.3–3.6] | −99.0 |
| generic procedure (150) | Haiku 5.5 | 34.0% [26.9–41.9] | 8.7% [5.1–14.3] | −25.3 |
| | Sonnet 5.5 | 26.0% [19.6–33.6] | 6.7% [3.7–11.8] | −19.3 |
| | Opus 5.5 | 38.0% [30.6–46.0] | 6.0% [3.2–11.0] | −32.0 |
| | Fable 5.2 | 37.3% [30.0–45.3] | 2.7% [1.0–6.7] | −34.7 |
| transcription artifacts (100) | Haiku 5.5 | 27.0% [19.3–36.4] | 5.0% [2.2–11.2] | −22.0 |
| | Sonnet 5.5 | 5.0% [2.2–11.2] | 2.0% [0.6–7.0] | −3.0 |
| | Opus 5.5 | 5.0% [2.2–11.2] | 0.0% [0.0–3.7] | −5.0 |
| | Fable 5.2 | 5.0% [2.2–11.2] | 1.0% [0.2–5.4] | −4.0 |

- The v1 surname + 様 rate (93–100%) is the result of applying criterion 1 literally, not evidence that the judges misunderstand Japanese honorifics.
- Detection of the 300 real violations did not drop with the notes (v2: 300/300 for Haiku, Sonnet, Opus; 296/296 for Fable).
- Limitation: generation and judging are both Claude models; gold labels are by design, spot-checked only.
- In-sample: the regional-norm notes were written after seeing this data. A held-out check (new fictional company, new seed) is in progress.

## Articles

| Date | Article |
|---|---|
| 2026-11-27 | [LLM判定器は日本の「名字＋様」を減点したりしなかったりする](https://zenn.dev/quent/articles/2329d74464eff5) (this repo, 50 conversations, 4 vendors) |
| TBD | v2 follow-up: regional-norm notes on 999 conversations — link added after publication |

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

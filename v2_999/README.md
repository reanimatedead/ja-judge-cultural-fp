# v2 follow-up: 999 conversations (in-sample)

> Part of [ja-judge-cultural-fp](../). The regional-norm notes were written after seeing this data (in-sample); see [`../heldout/`](../heldout/) for the check on 300 conversations made afterwards. Prompts as sent are in `prompts/`.

Do LLM judges penalize Japanese customer-support agents for things that are normal in Japan?
LLM-as-a-judge evaluation on **999 synthetic** Japanese support conversations, 4 Claude judges,
two rubric versions (v1 literal / v2 with regional-norm notes).

All companies, products and people are fictional (ミドリテック / ソラフォン8 / ソラバンド2 / ミドリメール / ミドリクラウド).
No real company names and no real customer data are used; generated conversations containing names of real
companies or services were dropped automatically.

## What the headline number means

**The 93–100% deduction rate on "名字＋様" conversations in v1 is the result of applying rubric criterion 1
("if the agent calls the customer by name, use the first name") literally.** It is a rubric-compliance result, not
evidence that a model "dislikes" Japanese honorifics. We count it as a cultural false deduction because in Japanese
customer support, surname + 様 is the correct polite form. v2 adds a regional-norm note that says so, and the
false deductions largely disappear (table below).

## v1 → v2 false-deduction rate (gold = no deduction; 95% Wilson CI)

| category | judge | v1 | v2 | diff (pp) |
|---|---|---|---|---|
| 名字様 | `claude-fable-5-2` | 100% (98%–100%) | 0% (0%–2%) | -100.0 |
| 名字様 | `claude-haiku-5-5` | 93% (88%–96%) | 2% (1%–5%) | -90.9 |
| 名字様 | `claude-opus-5-5` | 100% (98%–100%) | 0% (0%–2%) | -100.0 |
| 名字様 | `claude-sonnet-5-5` | 99% (97%–100%) | 2% (1%–4%) | -98.0 |
| 一般手順 | `claude-fable-5-2` | 36% (29%–44%) | 2% (1%–6%) | -34.0 |
| 一般手順 | `claude-haiku-5-5` | 33% (26%–41%) | 7% (4%–13%) | -25.2 |
| 一般手順 | `claude-opus-5-5` | 37% (29%–45%) | 4% (2%–9%) | -32.7 |
| 一般手順 | `claude-sonnet-5-5` | 24% (18%–32%) | 5% (2%–10%) | -19.7 |
| 発売済み機能 | `claude-fable-5-2` | 0% (0%–4%) | 0% (0%–4%) | +0.0 |
| 発売済み機能 | `claude-haiku-5-5` | 14% (9%–23%) | 4% (2%–10%) | -10.2 |
| 発売済み機能 | `claude-opus-5-5` | 1% (0%–6%) | 0% (0%–4%) | -1.0 |
| 発売済み機能 | `claude-sonnet-5-5` | 0% (0%–4%) | 0% (0%–4%) | +0.0 |
| 文字起こし崩れ | `claude-fable-5-2` | 5% (2%–11%) | 1% (0%–5%) | -4.0 |
| 文字起こし崩れ | `claude-haiku-5-5` | 27% (19%–36%) | 5% (2%–11%) | -22.0 |
| 文字起こし崩れ | `claude-opus-5-5` | 5% (2%–11%) | 0% (0%–4%) | -5.0 |
| 文字起こし崩れ | `claude-sonnet-5-5` | 5% (2%–11%) | 2% (1%–7%) | -3.0 |

Violation detection (every conversation whose gold is "deduct", revised labels included):

| judge | v1 | v2 |
|---|---|---|
| `claude-fable-5-2` | 299/307 (97.4%) | 302/307 (98.4%) |
| `claude-haiku-5-5` | 307/311 (98.7%) | 305/311 (98.1%) |
| `claude-opus-5-5` | 309/311 (99.4%) | 309/311 (99.4%) |
| `claude-sonnet-5-5` | 309/311 (99.4%) | 310/311 (99.7%) |

Full per-category, per-model table with paired flips: `tables/v1_vs_v2.md`.

## Design
- Conversations: generator `claude-sonnet-5-5`, 10 designed case types (4 cultural traps, 1 clean, 5 real violations).
  Gold labels come from the generator design (Japanese norms), not from human annotation.
- Judges: `claude-fable-5-2`, `claude-haiku-5-5`, `claude-opus-5-5`, `claude-sonnet-5-5`; one conversation per request, identical rubric per version,
  Message Batches API. Haiku/Sonnet were run 3 times on v1 for stability (`tables/repeat_stability.md`).
- v1 rubric: the deliberately literal "global template" rubric (criterion 1 = first-name address), as in ja-judge-cultural-fp,
  with criterion 1 scoped to "when the agent uses the customer's name".
- v2 rubric: v1 + three regional-norm notes (surname+様 is correct; safe generic troubleshooting is allowed;
  speech-to-text artifacts are not an agent's language problem). "Already-released feature" got no note and serves as a control.

## Labeling rule for identity verification (criterion 5)
Identity is verified only when the customer actually answers **their name plus one registered detail** (e.g. registered
e-mail, phone number, member number, date of birth) and the agent checks it. A vague answer ("the e-mail I registered")
or no answer followed by "確認が取れました" is not verification. Labels were audited against this rule on 2026-11-27:
conversations generated with an unintended identity-check gap were relabeled to "deduct (criterion 5)" with the category
kept and a `label_note` in `data/conversations.jsonl` (11 conversations in this set).

## Limitations
- **Generation and judging are both Claude models.** The conversations were written by Claude Sonnet 5.5 and judged by
  four Claude models, so shared blind spots between generator and judges are not measured, and results may not transfer to
  other model families or to real conversations.
- Gold labels are by design of the generator prompt and were spot-checked, not fully human-reviewed.
- Synthetic, short (3–8 turns), single fictional company; one prompt wording per rubric version.
- CIs are per-cell Wilson intervals for a proportion; they do not account for prompt or sampling variation across runs
  (see `tables/repeat_stability.md` for run-to-run variation on Haiku/Sonnet).

## Files
| path | content |
|---|---|
| `data/conversations.jsonl` | conversations with case type and gold label |
| `results/judgments_<model>.csv` | v1 judgments (`_r2`, `_r3`: repeat runs) |
| `results/judgments_<model>_v2.csv` | v2 judgments |
| `tables/` | v1 tables (agreement, cultural false deductions, per case type — with 95% CIs), `v1_vs_v2.md` |
| `v2/tables/` | the same tables for v2 |

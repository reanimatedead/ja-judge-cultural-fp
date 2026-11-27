# Held-out check (v2 regional-norm notes)

The v2 notes were written after seeing the 999-conversation dataset (in-sample). This folder is a check on data made
**after** the notes were written:

- new fictional company アオバ電機 (products, waterproof rating, refund rule and repair days all differ from ミドリテック)
- new random seed, generator **Claude Opus 5.5** (the 999 set used Sonnet 5.5)
- 300 conversations, same case-type ratios as the 999 set
- judged with the v1 and v2 rubrics by Haiku 5.5 / Sonnet 5.5 / Opus 5.5 / Fable 5.2 (Message Batches API, one conversation per request)
- rubric wording unchanged (criteria 1–6, procedure manual, v2 notes). Only the company facts block (社内ナレッジ) was swapped
  so the judge knows the new products' facts. The exact prompts are in `prompts/`.

All companies, products and people are fictional; e-mail addresses and phone numbers are dummies (`example.invalid`, `000-0000-0000`).
Generated conversations containing real company or service names would have been dropped (0 were).

## Files

| path | content |
|---|---|
| `data/specs.json` | the 300 designed specs (case type, product, hint, surname) |
| `data/conversations.jsonl` | generated conversations with case type and gold label |
| `prompts/` | generator prompt and the v1 / v2 judge prompts as sent |
| `results/judgments_<model>_{v1,v2}.csv` | every judgment (deduct, criterion, reason) |
| `tables/heldout_v1_vs_v2.md` | false-deduction rate per category and violation detection, v1 → v2, Wilson 95% CI |
| `aggregate_heldout.py` | recomputes the tables from `results/` (standard library only) |
| `evals_heldout.py` | the job that generated and judged this set (runs inside the author's batch-job framework; shown for reference) |

## Labeling rule for identity verification (criterion 5)

Identity is verified only when the customer actually answers **their name plus one registered detail** (registered e-mail,
phone number, member number, date of birth, ...) and the agent checks it. A vague answer or no answer followed by
"確認が取れました" is not verification.

Audit (2026-11-27): 20 conversations were read by the author, then every conversation where at least two judges deducted
under criterion 5 in v2 while the gold was "no deduction" was extracted and reviewed against the rule.
Relabeled to "deduct (criterion 5)" with the category kept and a `label_note`: H0110, H0158, H0200 (3 of 300, 1.0%).
H0220 (registered phone number only, no name) stays "deduct". The tables use the audited labels.

## Caveats

- Same author and same case-type design as the 999 set, so not fully independent.
- Gold labels are by design and were audited on 2026-11-27 (see below).
- Generation and judging are both Claude models.

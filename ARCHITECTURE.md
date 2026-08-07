# Architecture

<p align="right">
  <a href="README.md"><kbd> &nbsp; README &nbsp; </kbd></a>
  <a href="README.vi.md"><kbd> &nbsp; README (Tiếng Việt) &nbsp; </kbd></a>
</p>

This file is for anyone deciding whether to trust the skill, extend it, or copy its shape. It states
the layer model, the one rule that produced it, the invariants that hold it together, and the things
it refuses to do. Every count below is measured from the filesystem by a test, so this page cannot
quietly go stale.

## The failure this shape exists to avoid

A marketing skill fails in one of two ways.

The first is one enormous prompt. Everything the model might need is written into the instruction
file, and past a few hundred lines the model stops routing and starts recalling. Ask it for a
lighting setup and it produces a plausible one. Plausible is the problem: a recalled f-stop and a
looked-up f-stop are indistinguishable at the point of reading, and only one of them is a decision
somebody made and can defend.

The second is a folder of documents. The knowledge is real and nothing loads it, so the model
answers from training data while a correct answer sits three directories away, unopened.

So the layers here are split by one question — **what happens when this is wrong?** Prose that is
wrong can be argued with. A number that is wrong is quoted to a customer. Those two failures need
different containers, and that split is the whole architecture.

## Six layers

| Layer | What it holds | Now | How it fails | What stops that |
|---|---|---|---|---|
| Entry point | `SKILL.md`: routing, twelve core rules, intake, the run loop. No craft values | 301 lines | It absorbs the manual. Every new unit wants four lines here | Rules stay one line each; craft is exiled to `references/`; a new unit earns one routing row, not a section |
| Contract | `assets/registries/pipelines.json`: per pipeline, the references, scripts and deliverables it owes | 9 pipelines | A deliverable names a script the pipeline never loads, or one nobody shipped | Every `run:` line is checked against its own pipeline's script list |
| Prose | `references/`, one flat level, no satellite trees | 52 files | A reference nothing routes to. Knowledge that never loads reads as depth and ships as nothing | Every reference must be named by the entry point, the router, or the registry |
| Rows | `data/`: craft values, legal articles, vendor capabilities, one row per decision | 43 lookup tables | The table drifts from the script that reads it | The scripts that read a table load it inside their `--self-check`, so a renamed column or a regex that stops compiling fails in CI |
| Instruments | `scripts/`: arithmetic and gates, each returning a verdict rather than an opinion | 53 tools | It returns advice. Advice cannot be wrong, so it cannot be fixed | `--self-check` on every tool that computes, verified against known inputs |
| Gates | The anti-slop layer, the claim and rights checks, `run_status.py --strict` | 3 text instruments + 1 image track | A pass earned by nobody looking | A blank answer fails its gate instead of passing it |

## The rule that produced all of it

**Look it up, do not recall it.**

Judgement can live in prose, because judgement is arguable and a reader can push back. A value
cannot. A contrast ratio, a fine band, a token window, a withholding threshold: each is either the
one somebody measured or a fabrication in the same font. So anything that could be wrong by a number
lives in a row, and the row carries where it came from.

That is why the tables have columns most reference data does not:

| Column | On | What it is for |
|---|---|---|
| `source` / `source_url` / `retrieved` | 20 of 43 tables | The page and the day somebody read it. A spec with no retrieval date is a spec with no expiry |
| `evidence_grade` | 16 tables carry a grade | Whether the row is vendor-published, peer-reviewed, or this repo's own house rule. House rules say so |
| `what_it_does_not_establish` | 7 tables carry a limit | The load-bearing one. A benchmark quoted without its limits is how a plan acquires a number nobody can defend |

The third column is the unusual one, and it is the reason a table beats a paragraph here. `39%
open rate` is a fact about one vendor's sample on one date in one industry. The row that carries it
also carries the sentence explaining what it cannot tell you about your shop, and the tools refuse
to print the figure without it.

## The path a request takes

```
"Tôi mở shop mỹ phẩm nhỏ ở Gò Vấp, không biết gì về marketing"
         │
         ▼
  scripts/_signals.py         reads horizon, budget tier, product family, market
         │                    from the wording — VI or EN, accented or not
         ▼
  scripts/start_workbench.py  scores all 9 pipelines, shows the scores, picks one
         │
         ├──▶ assets/registries/pipelines.json   that pipeline's contract
         ├──▶ references/ + data/                craft as prose, values as rows
         │
         ▼
  runs/<name>/                29 files for this request. 01-intake quotes it verbatim above
         │                    a table of every inference and the phrase behind it
         ▼
  > WRITE: markers            what only the operator knows
  > RUN: <command>            what a script settles — 23 of them name the command
         │
         ▼
  scripts/check_specificity.py    does it say anything?          exit 2 if not
  scripts/rewrite_human.py        does it read like a person?    exit 2 if not
  scripts/check_address_register.py   who is it addressing?      VI only
         │
         ▼
  scripts/run_status.py --strict   refuses empty deliverables and filled-but-
                                   indefensible ones: unsourced figures, leftover
                                   placeholders, sections thin enough to be filler
```

The order of the three text instruments is load-bearing rather than stylistic. Rhythm work deletes
specifics, because a specific is the awkward part of a sentence. `Giao trong 2 giờ ở Gò Vấp` flows
worse than `Giao hàng nhanh chóng, tận tâm`, so a cadence gate run first rewards the empty draft.

## The exit-code contract

Every tool in `scripts/` uses the same five codes.

| Code | Means | Why it is separate |
|---|---|---|
| 0 | Clean | Nothing mechanical is left. Not the same as approved |
| 1 | Usage error | The arguments were wrong. Never confused with a bad answer |
| 2 | A gate failed | Something measurable is wrong, and the report names the row |
| 3 | Computable but unsettled | The arithmetic ran and the answer is not available |
| 4 | The gate could not run | The instrument itself crashed; `run_gate` in `_emit.py` converts the traceback, so a crash is never scored as a verdict |

Code 3 is the one worth arguing about, and it is the reason the skill can be trusted on the
questions it cannot answer. Four Meta placements publish a recommended size and then no file
ceiling at all. A checker that returns 0 against that silence has told you the asset passed, when
what happened is that nobody published a limit. So the placement check returns 3 and names the page.
Same code when a threshold still sits inside a market-sizing range, when a provider documents no
seed, when a variance table has a hole in a column that is full everywhere else.

A pass against silence is the single most expensive defect available to a tool like this, because it
looks exactly like a pass.

## The invariants, and what holds each

The architecture is not a description. Every load-bearing claim above is re-checked before a
deploy, by the CI workflow in `.github/workflows/deploy-pages.yml` and by the scripts' own
`--self-check` modes — 21 of them, one per measuring instrument, each asserting on inputs that
once broke that instrument.

| Invariant | Held by |
|---|---|
| The router and every reference it depends on exist on disk | file-existence checks in the deploy workflow |
| The dossier tree and the handbook JavaScript stay deleted | inverted `test ! -e` checks in the same workflow |
| Each gate still fires on known-bad input and stays quiet on clean input | that script's `--self-check`; all 21 run in CI |
| Routing still sends each ask to the pipeline its row names | `evaluate_workbench.py`, replayed in CI |
| The two simulated runs still earn the readouts printed inside them | both files re-gated by `check_output_shape.py` and `check_specificity.py` in CI |
| A planner manifest and a scaffolded run still build from scratch | smoke tests in the same workflow |
| Every script still compiles on a clean checkout | `python -m compileall` in CI |

The worked examples are re-gated rather than trusted because a README readout is the first thing
to rot and the last thing anybody rereads.

## Adding a unit

Seven steps, in this order. Skipping any of them ships a unit that works and cannot be found.

1. **Write the reference.** `references/<topic>.md`, under 150 lines, ending with a section that
   states what the unit does not establish.
2. **Write the table.** `data/<topic>.csv`, one row per decision, with the source and caveat columns
   the row's kind needs. A value that belongs in a script constant belongs here instead.
3. **Write the script.** `scripts/<verb>_<noun>.py`, with `--self-check`, the five exit codes, and a
   docstring that records why any number is *absent*.
4. **Register it.** Add the reference and the script to the pipelines in `pipelines.json` that need
   them, and extend the deliverable's `run:` line so the command reaches an operator.
5. **Route it.** One overlay row in `SKILL.md` and one bullet in `marketing-system-router.md`,
   written in the words a non-marketer would use.
6. **Review it.** Run the relevant script on a representative input, inspect its real output, and pin
   any refusal — the tidy edit is always to fill a declared gap with a plausible number.
7. **Update the counts.** Keep both READMEs and this file aligned with the filesystem.

## What the architecture refuses

- **No network call inside a gate.** Gates run offline, so a failure is reproducible and a pass is
  not a cached page. Retrieval happens in research, is dated in a row, and expires.
- **No number the operator did not declare.** Where this corpus holds no citable figure, the field
  is declared by the operator and the script certifies nothing. First-response time and send
  frequency are both refusals, both recorded as such, and both pinned by a test.
- **No row without its limits.** A benchmark, a legal article and a vendor capability each ship with
  what they do not establish, or they do not ship.
- **No claim of work that did not happen.** A prompt is not an image, a storyboard is not a video, a
  plan is not a result, and `_meta/render-capability.json` starts at `not-rendered`.
- **No access control routed around.** One standard behind `report-notation.md` sits behind a
  paywall, so the reference quotes no rule number from it and says why.

## What this does not establish

The layer model buys traceability, not correctness. A wrong row passes every test in the suite, and
a house rule graded as a house rule is still just an opinion with a label on it. What the shape
guarantees is narrower and more useful than being right: every value has one place it lives, one
source beside it, and a diff that shows when it changed.

The marketing judgement is a separate question, and the honest answer is in each reference's own
closing section rather than here.

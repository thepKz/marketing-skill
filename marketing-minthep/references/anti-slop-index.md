# Anti-slop index: the whole layer on one page, with its sources

"Slop" got its working definition from Simon Willison in May 2024: unrequested, unreviewed
AI-generated content, "to AI what spam is to email" (simonwillison.net/2024/May/8/slop/, retrieved
2026-08-02). The academic version is Kommers et al., *Why Slop Matters*, ACM AI Letters, January
2026: superficial competence, asymmetric effort, mass producibility. All three properties describe
the producer's shortcut, not the reader's taste. This layer answers it.

The Vietnamese press calls it "nội dung rác AI", and Vietnam sits near the top of the consumption
tables (Kapwing 2025, reported by VietNamNet, retrieved 2026-08-02). Consumption, not detection.
No published Vietnamese tell catalogue was found on the retrieval date. The Vietnamese columns in this
skill's tables are therefore its own observation, graded house-rule, and not citations to a
literature that does not exist yet.

## The five instruments, in the only order that works

| Stage | Question | Instrument | Reads | Explained in |
|---|---|---|---|---|
| 1. Content | Does it say anything a competitor could not copy? | `scripts/check_specificity.py` | the `evidence` and `hedge` layers of `data/translation-tells.csv` | `copywriting.md` |
| 2. Shape | Is the document shaped like an answer or like a model's essay? | `scripts/check_output_shape.py` | its own pattern set (announced openings, bold-led grids, generic headers, recap closes) | `output-contract.md` |
| 3. Cadence | Does it read machine-made or machine-translated? | `scripts/rewrite_human.py` | all of `data/translation-tells.csv` | `rewrite-human.md` |
| 4. Presence | Does the sentence have what a sentence written in this language has? | `scripts/rewrite_human.py` | `data/spoken-markers.csv` | `rewrite-human.md` |
| 5. Register | Who does it address, and does it hold that choice? | `scripts/check_address_register.py` | `data/address-registers.csv` | `address-register.md` |

Stage 4 is the only one of the five that reads for presence, and it was added on 2026-08-05 because
the others could all pass a draft that was still flat translationese. Every table above it names
something to delete; none of them had ever asked what a Vietnamese sentence carries when a Vietnamese
person wrote it. A subtractive index is not an anti-slop index, it is a de-slopping index, and the
difference shows up as copy that offends nobody and sounds like nobody.

Stage 2 was added on 2026-08-06 because a document can pass every sentence gate and still be
recognised as machine-written from its silhouette alone — the announced opening, the three
symmetric sections of three bold bullets, the recap close. The tell had moved up a level, so an
instrument moved up with it. Its positive spec, calibrated on the answer-first format Perplexity
made normal, is `output-contract.md`.

The order is load-bearing, not stylistic. Rhythm work deletes specifics, because a specific is the
awkward part of a sentence: `Giao trong 2 giờ ở Gò Vấp` flows worse than `Giao hàng nhanh chóng,
tận tâm`, and a cadence gate run first will reward the empty one. Shape runs before cadence
because restructuring a document rewrites its sentences, so cadence measured first is a wasted
pass. Register runs last because it is Vietnamese-only and because fixing content, shape and
rhythm rewrites the sentences it would have graded.

Images run on a separate track. `data/slop-tells.csv` holds 33 tells across prompt, image, copy,
layout and campaign, and `scripts/find_recipe.py --checklist RECIPE_ID` filters them to the tells
that can occur in one specific frame, ordered by severity. Look at the render against the list.
Rereading the prompt proves nothing.

Truth sits upstream of every one of them. A fabricated delivery time passes every gate here and fails core
rule 1, which outranks them. `check_claims.py` and `claims-proof-ledger.md` answer whether a claim
may be made at all; this layer only answers whether the sentence carrying it reads like a person.

## Where the tells come from

| Source | What it establishes | What to take from it |
|---|---|---|
| Wikipedia, *Signs of AI writing* (en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing, retrieved 2026-08-02) | The community catalogue: significance inflation, participial tails, promotional vocabulary, weasel attribution, rule of three, chat leakage, with per-tell academic citations | The tell taxonomy, and its list of *human* signs that must not be "fixed" |
| Juzek and Ward, ACL 2025 (arXiv:2412.11385) | Why models over-produce words like "delve": lexical overuse traced to post-training | Word tells are model-era artefacts, not writing advice |
| Kobak et al., *Science Advances* 2025 | Measured excess vocabulary in millions of biomedical abstracts | The tells are statistically real at population scale |
| Reinhart et al., *PNAS* 2025 | LLMs over-produce `-ing` participial clauses and specific vocabulary against matched human text | The empirical basis for the participial-tail tell |
| Geng and Trotta, arXiv:2404.08627 | Over 10% drop in "is/are" in LLM-assisted academic writing | Copula avoidance: "serves as", "stands as", "boasts" in place of *is* and *has* |
| Kamali et al., arXiv:2406.08651 | The only rigorous image catalogue: anatomical, stylistic, functional, physics and sociocultural implausibilities, each with its false-positive caveat | The five image-tell families in `slop-tells.csv`, and the caveats that keep them from over-firing |
| blader/humanizer, github.com/blader/humanizer (retrieved 2026-08-02) | The most-adopted production-side operationalisation: 33 patterns, cluster-based detection, voice calibration, a rule against inventing facts to sound human | Method, not scholarship: detect clusters, never single hits |
| Ports of the above to zh, ru and pt-br (retrieved 2026-08-02) | Each rebuilt the word list and kept the structure, rhythm and stance rules verbatim | Which tells transfer to Vietnamese and which must be rebuilt |

Rows in `translation-tells.csv` and `slop-tells.csv` that match this literature match it at the
category level. The per-row wording, the Vietnamese member of each pair, and every threshold are
this repo's own, on the same terms as `copywriting.md`: house rules, open to argument, and not
dressed up with a citation they do not have.

## Word lists decay. Distributions do not.

Every named-word tell is bound to a model generation. "Delve" marks 2023–2024 output and had
already given way to "showcasing" and "emphasizing" by 2025; GPT-5.1 shipped with em dashes
suppressed (Ars Technica, 14 November 2025); image models have largely fixed hands and lettering.
A gate built on any of those words alone is a gate with an expiry date nobody wrote down.

The durable tells are statistical, and they are the ones the instruments here measure:

| Durable tell | Why it survives model updates | Where it is measured |
|---|---|---|
| Uniform sentence length | Sampling regresses to the mean; humans write in bursts | `rewrite_human.py`: coefficient of variation, long/short ratio |
| Missing landing beats | A model rarely risks a four-word sentence | `rewrite_human.py`: landing-beat rate per 150 |
| Low information density | Superficial competence is the definition of slop | `check_specificity.py`: fact floor, brand-swap share |
| Significance inflation | Regression to the mean smooths specifics into importance claims | `translation-tells.csv` evidence layer; `empty-adjective` gate |
| Register drift | Translated Vietnamese re-decides who the reader is per sentence | `check_address_register.py` |
| No spoken markers | A model translates the sentence rather than making its decision again, so the grammar of the target language never gets used | `rewrite_human.py`: distinct markers from `spoken-markers.csv` |

The last row is the only positive entry in the table and the newest. It is also the one a word list
could never have caught, because the defect is an absence — nothing is present to match.

This is also why the word layers live in CSV rows that carry their own severity and scope rather
than in script constants. A tell that stops discriminating gets edited in the table, with the
change visible in the diff, and the arithmetic does not move.

Detection runs on clusters. Never on single hits. One em dash means nothing; a flat cadence plus an
evidence adjective standing alone plus an opening in threes is a confession. The gates implement
this by reporting densities per 150 words against budgets instead of flagging occurrences.

## What must not be "fixed"

The same Wikipedia catalogue keeps a list of human signs, and a rewrite that strips them to
satisfy a detector manufactures a second kind of slop:

- Plain copulas. "Is" and "has" are what the copula-avoidance tell replaces.
- Hedges a person stands behind: "perhaps", "tends to", "về cơ bản". One per sentence is a voice;
  the `hedge-stack` gate fires at two, where the claim becomes unfalsifiable.
- Superlatives with an owner: "the first", "the cheapest in Gò Vấp" are checkable claims, and
  checkable is the opposite of slop.
- Wordy constructions and lumpy middles. The lump is usually the specific.
- Quoted material. A verbatim quote is evidence; rewriting it to flow is falsifying it.

And the rule the production-side literature converges on: never add a fact to sound human. A
fabricated number passes stage 1, reads beautifully at stage 3, and is the one defect this whole
layer cannot detect. It is caught upstream by the truth map, or by a customer.

## Running the layer

```
python scripts/check_specificity.py --check draft.md
python scripts/check_output_shape.py --check draft.md
python scripts/rewrite_human.py --check draft.md --lang vi --channel deliverable
python scripts/check_address_register.py --check draft.md --channel deliverable
python scripts/find_recipe.py --checklist RECIPE_ID
```

Exit 0 is clean, 2 is a failed gate, 3 is computable but unsettled. Do not lower a target to pass.
Stage 1 runs first.

## What this does not establish

An index maps; it does not grade. Passing all five instruments means the draft is specific,
shaped like an answer, reads like a person, holds one register and avoids the frame's known
failure modes. It does not mean the
copy is true, legal, on-strategy, or about the right thing. And the sources above describe the
output of English-language models as of their publication dates: the tell population moves with
every model generation, which is the argument for measuring distributions and re-dating the word
rows, not for trusting this page longer than its retrieval dates deserve.

# SEO Writing

## Contents

- What this unit decides
- Read the query, not the keyword
- The intent table
- What the audit measures, and why each one
- Information gain is the only durable advantage
- The Vietnamese search surface is not Google alone
- Order of work
- Reading the report
- What this unit cannot establish
- Evidence grades
- The handoff

## What this unit decides

Two questions. What kind of page can answer this query at all, and whether the draft in front of you
answers it before it starts talking about the company.

Nothing else. This unit does not pick keywords, does not estimate volume, and does not predict
ranking. Those need a live SERP and a data source, which is `market-data-collection.md`. What is
left after removing them is still most of the work, and it is the part that gets skipped.

`data/seo-intents.csv` holds ten query intents with the page type that wins each one and the number
of checkable proofs it needs. `scripts/audit_seo_page.py` measures a draft against them. Everything
below is the reasoning those two encode.

## Read the query, not the keyword

A keyword is text. A query is a person in a particular state, and the state decides the page.

`giá bàn gỗ sồi` and `bàn gỗ sồi có tốt không` contain almost the same words and want opposite
pages. The first wants a number in the first sentence. The second wants somebody else's experience,
and a page that opens with a price has misread it. Write one page for both and it answers neither.

The most expensive version of this mistake is scoping. A `best-of` SERP in Vietnam is held by
aggregators and news sites, so a brand domain usually cannot win it at any length. Read the results page before the work
is quoted. Not after the draft comes back rejected.

## The intent table

Ten rows in `data/seo-intents.csv`. Each carries the query signals in both languages, the searcher's
state, the page type that wins, how many checkable proofs that page needs, the title shape, the
reflex to reject, and a Vietnam note.

```
python scripts/audit_seo_page.py --list-intents
python scripts/audit_seo_page.py --explain price
```

The proof count is the column the script consumes. A `definition` query needs two checkable things
and a `best-of` list needs six, because the first is answered by one sentence and the second is
answered by a selection rule somebody can inspect.

Read the intent off the query, never off the product. A seller who decides "our page is a product
page" and writes it for `bàn gỗ sồi tốt nhất` has entered a competition against listicles with a
brochure.

## What the audit measures, and why each one

```
python scripts/audit_seo_page.py --check draft.md --query "giá bàn gỗ sồi" --intent price
python scripts/audit_seo_page.py --targets
```

The draft may carry front matter with `title`, `description`, `query` and `intent`. A markdown file
has no title tag and no meta description, so if those are absent the script reads the H1 and the
first paragraph and labels them `inferred`. That label matters: an inferred title passes the gate and
still ships as no title at all, because an H1 and a title do different jobs.

**Title.** Present, at least fifteen characters, and estimated to fit inside about 580 pixels. Width
rather than character count, because a title of capitals truncates sooner than one of lowercase.
Truncation costs the qualifier that made the title match the query, and the qualifier is nearly
always at the end.

**Meta description.** Between seventy and a hundred and sixty characters. It is not a ranking input.
It is the ad copy for the click, and leaving it blank hands that sentence to a machine.

**Structure.** Exactly one H1, and no heading level skipped. An H2 followed by an H4 is decoration
standing in for hierarchy, and both screen readers and outline extraction read the ladder.

**Query placement.** Every head term in the title, at least one in a heading, and one piece of text
somewhere on the page containing all of them together within the first hundred and twenty words.
That last gate is the one worth arguing about, so it gets its own paragraph below.

**Repetition.** The exact query phrase at most three times per three hundred words. Not a penalty
threshold. Nobody outside Google knows where that sits. It is a writing tell: past three, somebody
reading the page aloud hears the seam.

That one carries a floor. A rate has to be extrapolated from the text in front of it, and on a short
page the extrapolation is noise: a sixty-word price page with its query in the H1 and again in the
answering sentence scores ten per three hundred while doing exactly what the intent asked, twice. So
the ceiling is only enforced once the phrase has appeared four times outright. Nobody hears a seam at
three.

**Proof.** Two counts, deliberately different. Total specifics per three hundred words is the
information-gain gate. Statements carrying a number, a date or a contact is the count the intent row
compares against, because a name on its own is weak evidence and brand copy is full of names.

The query-placement gate exists because `copywriting.md` already said satisfy the real query before
expanding into brand narrative, and a sentence like that changes no drafts. Now it is a number. A
page that has not addressed the query inside roughly one screen has opened on narrative, and the back
button is one tap away.

Head terms fold diacritics, so `giá` matches `gia`. Vietnamese searchers type both and phones
autocorrect between them. A matcher that treats them as different words reports a missing keyword
that is sitting on the page.

## Information gain is the only durable advantage

A draft can satisfy every rule above and still be the ninth restatement of the same page. Nine pages
carrying the same summary have no reason to outrank each other, and the tenth carrying a measured
number does.

Gain is countable, and that is the useful part: a quantity with a unit. A date. Somebody's name. A
way to reach them.

`scripts/check_specificity.py` already detects all four, so the audit imports it rather than growing
a second set of detectors that would drift within a month.

The floor is three specifics per three hundred words, which is one per hundred. Calibrated on the
only corpus available offline, this skill's own sixty reference files: median 3.7, range 0 to 34.4,
with 21 of the 60 below the line.

Two honesties about that number. Documentation is not a commercial page, so this is a floor borrowed
from an adjacent corpus. And the files that fail are the ones the coverage audit had already flagged
as thin, which is corroboration and not proof.

One thing this gate reads that the cadence tools do not: tables and lists. `rewrite_human.py` blanks
those before measuring rhythm, and correctly so, because a bullet is not a sentence. Reusing it here
scored 26 of the 60 reference files as carrying nothing checkable, when their numbers were sitting in
rows the reader skipped.

On a commercial page that would be worse. The winning page for a `comparison` query is a side-by-side
table, and a `price` page's entire proof can be one figure in row two. A reader who finds the price
there has been answered. Nothing was thin.

## The Vietnamese search surface is not Google alone

Four places where a plan built from English-language SEO advice quietly fails, all of them recorded
in the `vn_note` column.

How-to queries usually land on YouTube and TikTok first. A text page that cannot show the halfway
state is competing against video, so it needs stills or it needs a different intent.

Most `gần đây` intent resolves inside Google Maps rather than the results page. The Business Profile
is the ranking surface and the website supports it, which reverses the usual order of work.

`chính hãng` is a trust query, not a product query. It asks whether you are a counterfeiter, so
authorised-dealer evidence outranks any amount of copy. `có tốt không` attached to a brand name is
the same instinct: the honest answer is registration details and a traceable address.

Occasion demand front-loads by two to four weeks and then dies overnight. A Tết page published in
late January is late, however good it is.

## Order of work

Read the SERP first. Decide whether this page type can win at all, and say so before the work is
scoped. That order saves money.

Name the intent from the query, then read its row. Gather the proofs before writing rather than
after: the proof count is what decides the page, and gathering it afterwards means padding prose that
already exists.

Now write. Run the audit, fix what blocks, and run `rewrite_human.py` last, because a page can clear
every gate here and still read machine-written. Separate defects, separate fixes.

## Reading the report

Every gate reports observed against target with a severity, in the same shape as the other gates in
this skill. Critical and high failures are counted as blocking and the script exits non-zero, so it
can sit in a check step.

Two kinds of silence are deliberate. A gate that has no evidence to work from is absent from the
report rather than passing: no query means the placement gates are skipped, no intent means the proof
count is skipped, no images means the alt-text gate never appears. A pass on no evidence is a lie
that reads like a clean bill of health.

And every run prints what it did not establish. That block is not decoration. It is the difference
between an on-page audit and the SEO audit somebody will assume they were handed.

## What this unit cannot establish

Search volume, difficulty and seasonality. These are live facts that change weekly and differ by
device and city. Any number this script printed for them would be invented.

What currently ranks, and whether the page can rank at all. That needs the results page in front of
you, in the city that matters.

Whether the page is indexable. Robots directives, canonical tags, hreflang, status codes and render
behaviour all live on the server, and a draft cannot tell you about any of them.

Whether the claims are true or permitted. That is `claims-proof-ledger.md` and `claims-proof-ledger.md`,
and no structural gate substitutes for either.

Whether the writing is any good. A pass means the page is structurally capable of answering
its query. That is the floor. Not a standard.

## Evidence grades

Worth stating plainly, because SEO is the most folklore-heavy material this skill touches.

Title and description truncation are **observed rendering conventions**, not published rules, and
Google rewrites a large share of titles regardless. Read a truncation failure as risk to the
version a human sees in the results. Not as a penalty.

Intent-to-page-type mapping is a **stable observed pattern** across SERPs rather than a documented
algorithm. It holds because it describes what satisfies a person. That part is unlikely to change.

Information gain is **reasoned from first principles**, then calibrated on an adjacent corpus as set
out above. It is the most defensible gate in this unit. It is still not a ranking factor.

The pixel width table is an **estimate**, built per character rather than measured from a font file.
It exists to separate comfortable from likely-cut, which a character count gets wrong.

Nothing in this unit is a ranking factor and nothing here predicts position.

## The handoff

Intent and page-type decision, the draft, the audit report including its unknowns block, and the
`rewrite_human.py` report.

Whoever receives it needs the unknowns block most, because it names the work that is still owed:
read the results page in the city that matters, get the volume and seasonality from a live source,
confirm the page is indexable, and check every claim against the ledger.

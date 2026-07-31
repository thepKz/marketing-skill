# Research Protocol

## Contents

- When this protocol runs
- Decision questions, not topics
- Source tiers, and what each tier is allowed to support
- Search in the market's own language first
- Triangulation fails when the three sources share one parent
- A research assistant is a discovery source
- A page that returns a shell is not a page you read
- When the source is behind a login
- Published, checked, and the date that is missing
- The evidence ledger
- The stop rule, made arithmetic
- The report
- What never gets invented

## When this protocol runs

Any time the answer will be used to commit money, headcount or a quarter. Plans, market assessments,
competitor work, feasibility calls, and the awkward ones where somebody has already decided and wants
support.

Two neighbours own things this file does not. `market-data-collection.md` owns where Vietnamese numbers
come from and what each family of measurement can carry; `market-assessment.md` owns the sizing
arithmetic and the alternatives grid. This file owns the search itself, and the decision to stop.

## Decision questions, not topics

Convert the brief into questions that have answers somebody could act differently on. Demand,
audience, the alternatives already in use, willingness to pay, channel access, and the constraints
nobody mentioned.

"Research the coffee market" is a topic. Nothing about it can come back false, which means nothing
about it can come back useful either. Rewrite it as: how many households in these provinces buy ground
coffee at all, and how often, and at what price paid.

A question you cannot imagine a disappointing answer to is not a question. It is a preference wearing
a question's clothes, and the search will find what it was sent to find.

## Source tiers, and what each tier is allowed to support

| Tier | What it is | What it may support |
|---|---|---|
| Official | Statistics office, ministry, regulator, standards body | Denominators, legal constraints, definitions |
| First-party | Your own transactions, CRM, receipts, platform exports | Anything about your own performance |
| Primary evidence | Interviews and observation you ran yourself | Behaviour, language, willingness to pay |
| Reputable secondary | Panel and syndicated research with method disclosed | Incidence and frequency, as ranges |
| Directional | Press, blogs, listicles, agency roundups | Where to look next, and nothing else |

The last row is the one that leaks. A directional source may point you at a fact and may never be the
citation for it. If a blog cites a study, the study is the source, and if you cannot open the study you
do not have the fact.

Platform-published reach and audience figures are their own case, and the rule is harsher: never a
denominator. `market-assessment.md` explains why, and `size_market.py` fails that chain on a critical
gate rather than warning about it.

## Search in the market's own language first

Search in Vietnamese first. Vietnamese sources are usually the only ones carrying the right
denominator, and English-first search finds the English write-up of a Vietnamese report instead — one
translation away from the number and dated later than it.

Record the query. Not just the URL — the words that found it. Six weeks later you will want to know
whether the absence you concluded from was real or was a bad query, and the query is the only part
nobody can reconstruct.

Search silence is not evidence of absence. It is one of the three Vietnamese biases named in
`market-data-collection.md`, and it appears most often as a claim that nobody is talking about a
category when in fact nobody is talking about it in the language you searched.

## Triangulation fails when the three sources share one parent

Three independent signals is the right instinct and the usual self-deception. In practice three
articles trace back to one press release, and the agreement you were reassured by is one source quoted
three times.

Before you count a conclusion as triangulated, check the parents. Open each source and find where its
number came from; if two of them cite the same original, you have two signals at most. One, if the
third is a blog citing the first.

Two genuinely independent sources beat four dependent ones. Prefer a different method rather than
another article — a panel figure and a receipt trace disagree in useful ways, where two panels usually
disagree in ways that only tell you about panels.

Independent means the errors are independent. That is the test.

## A research assistant is a discovery source

This applies to a delegated agent, a junior, and a language model, and the reason is the same for all
of them: what comes back is a claim about a page rather than the page.

Re-read every load-bearing claim at its source before it enters a deliverable. In building this skill,
three researched claims failed that re-reading: a field count that was wrong twice over, an API
behaviour that could not be verified without an account, and a payload description taken from a page
that never rendered. All three were plausible. That is the problem with them.

Load-bearing means the recommendation changes if the claim is false. Anything else can be summarised
without re-reading, and should be marked as summarised.

## A page that returns a shell is not a page you read

Modern documentation sites frequently serve a JavaScript shell to a fetcher and the real text only to a
browser. A fetch that returns a few kilobytes of script has not failed loudly. It has returned
something that looks like a successful read of a nearly empty page, and a careless workflow will
conclude the vendor documents nothing.

Check the byte count. `developers.zalo.me` behaves exactly this way, and the honest record is that the
page could not be read rather than that the platform publishes nothing.

Some sites serve full text to a search-engine user agent and a shell to everything else.
`banhang.shopee.vn/edu/` is one. Getting the text this way is legitimate reading; presenting an
unrendered fetch as a verified absence is not.

## When the source is behind a login

Say so. Put it in the deliverable with the screen that would settle it, because a finding of "the
vendor does not publish this outside the account" is a real finding and belongs in the report.

Then name a person with an account and what they should bring back. Usually a screenshot. This is the
`path-unpublished` discipline from `attribution-windows.csv`, and it costs more than a shrug because
somebody has to actually be asked.

Never fill the gap from memory. A remembered default is indistinguishable, on the page, from a read one
— and the whole reason the row exists is that the two are different.

## Published, checked, and the date that is missing

Record the publication date and the retrieval date, and treat them as different facts. A 2019 panel
report retrieved today is a 2019 fact.

Many vendor help pages publish no last-updated date at all. Google's do not. So the only honest
annotation is the date you checked it, which claims nothing about when it changed, and the note has to
say that rather than dressing a retrieval date as a publication date.

Anything older than a year gets flagged. `size_market.py` fails `sources-are-not-stale` at that
boundary, measured against a stated as-of date rather than against today, so a saved chain does not
quietly rot into a pass.

Institutions rename and their hosts die. `market-data-collection.md` carries the table; the working
tell is that a citation to a dead host proves nobody opened it.

## The evidence ledger

Every finding carries: `finding_id`, the decision question it serves, source URL, publisher,
publication date, retrieval date, the quote or data point, your interpretation held separately from it,
confidence as `high|medium|low`, the bias or limitation, and the allowed use.

Interpretation held separately is the field that does the work. A quote and a reading of a quote merge
within about a week of being written in the same cell, and after that nobody can tell which part the
source actually said.

Confidence is not a feeling about the source. `high` means official or first-party, opened and read;
`medium` means method disclosed and read; `low` means everything else, including anything a directional
source told you.

## The stop rule, made arithmetic

"Stop when the decision threshold is met, not when the search feels exhaustive" is the right rule and
was, for a long time here, unusable advice. Exhaustive is a feeling and so was met. Both are now
computable. This is the one piece of procedure this file uniquely owns.

State the threshold before searching: the number that flips the decision. Build the chain in
`size_market.py`, with a range on every term and a source URL on every range. Then ask the script.

```
python scripts/size_market.py --check chain.csv --threshold 2000000000
```

Three verdicts come back, and each one is an instruction. Entirely above the threshold, or entirely
below it: stop, because no additional precision can change what you do. Straddling it: keep going, and
the script names which terms would settle it on their own, widest uncertainty first.

Terms it does not name cannot change the outcome however precisely you pin them down. That is where
research hours go to die, and it is usually the term the team finds most interesting.

One verdict has no research answer. A threshold sitting on the centre of your own range can never be
settled by narrowing a single term, because collapsing any term to its centre leaves the centre where
it was. Report that as a decision balanced on an estimate, and stop searching.

## The report

Explain the conclusion before the jargon, because the reader is usually a founder who has four other
jobs today. An executive answer first, in the language of the decision. Then the evidence table, the
assumptions, the implications for market and competitors, the recommendation, the risks, and the next
research actions with the dominant uncertainty named.

Cite URLs inline and append the sources. Mark each finding's confidence in the table rather than in a
paragraph about methodology, which nobody reads.

State what remains unknown. A report with no unknowns section is either finished research, which is
rare, or an unfinished search that stopped feeling incomplete.

## What never gets invented

Not sizing figures, not customer quotes, not competitor pricing, not regulations, not trend claims. If
browsing is unavailable, return the research plan and mark the report unverified at the top rather than
in a footnote.

For scientific, health, behavioural, environmental or efficacy claims, prefer systematic reviews,
primary peer-reviewed studies, recognised standards and official regulatory sources. Record population,
method, sample size, outcome, effect size where given, and the limitations the authors state
themselves. Then record whether the design supports correlation or causation. Copy crosses that line
quietly, and once it is crossed in a headline nobody goes back to the method section.

`claims-proof-ledger.md` owns what may then be said in public, which is narrower than what the evidence
supports.

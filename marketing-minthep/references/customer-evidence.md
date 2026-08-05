# Customer Evidence

## Contents

- What this unit decides
- The two sentences that do the damage
- Sources, and what each one structurally cannot see
- How many people is enough
- The number that surprises everybody
- The row nobody writes down
- Frequency is not intensity
- One source is not evidence
- Coding: the file the script reads
- Reading the shipped example
- Whose words are these
- What this unit cannot do
- The handoff

## What this unit decides

Three questions, and nothing else. Which source can answer the question you actually have. How many
people you need to have heard from before a theme is a theme. And what a number taken from those
people is allowed to say out loud.

It does not decide positioning, and it is not a research-methods course. `data/evidence-sources.csv`
holds twenty sources with what each over-represents and what it cannot see;
`scripts/check_evidence_saturation.py` reads a coded file and grades it. Everything below is the
reasoning those two encode.

Two boundaries, so this unit does not swallow its neighbours. Published and bought numbers - market
size, category growth, competitor revenue - are `market-data-collection.md` and
`data/market-data-sources.csv`. Reading a single image or post for craft is `reference-reading.md`.
This unit is primary evidence about people who bought, nearly bought, or left.

## The two sentences that do the damage

**"We talked to customers and they said X."** How many customers, found how, and did anybody say the
opposite. The sentence is unfalsifiable as written, which is why it survives every review meeting.

**"Sixty percent of customers want X."** Out of how many. Six of ten is sixty percent, and the same
six of ten is also anywhere from thirty-one to eighty-three percent at ninety-five percent confidence.
That is not a finding. It is a direction wearing a decimal point.

Both sentences are usually written by somebody honest. They are what you get when a real conversation
is summarised for a slide, and the summary drops the denominator because the denominator was never
recorded in the first place. The fix is not more rigour in the meeting. It is a coded file and a script
that refuses.

## Sources, and what each one structurally cannot see

Every source in `data/evidence-sources.csv` carries five things a reader needs before quoting it: what
it over-represents, what it cannot see, the headcount below which its themes are provisional, whether
its words may be republished, and what it does not establish even when the sample is perfect.

The pattern that matters is that each source is blind in a specific and predictable direction, and the
blindness is not fixable by collecting more of the same thing.

`public-reviews-own` is J-shaped. Ratings pile at five stars and one star, so the middle of your
customer base - which is most of it - is close to absent, and thirty reviews of a polarised
distribution still look polarised. `support-tickets` measures reporting and not incidence: the ratio
of customers who silently gave up to customers who complained cannot be computed from inside the
queue, and it is usually the larger number. `search-and-site-queries` sees demand that already has a
word for itself, which is why it is useless for a category nobody has named yet.
`behaviour-analytics` locates the wound and cannot name the weapon. `own-social-comments` is a census
of people you already converted, which makes it the most quoted and least transferable source in the
table.

Two deserve singling out for a Vietnamese operation. `chat-and-dm-transcripts` - Zalo and Messenger -
is where the whole pre-purchase conversation actually happens, which makes it the best raw material
for copy that exists: the buyer's own words for the problem, before anybody taught them yours. And it
says nothing about prevalence, because people who scrolled past do not send messages. Then
`competitor-review-mining`, the one cheap source that returns something none of the others can: an
unmet need in the category, described by somebody who already paid money for the alternative. It cannot see what the
competitor quietly does well, because a met expectation goes unmentioned.

The other fourteen stay in the table rather than in this file, because a source you look up is a source
you look up when you need it, and twenty paragraphs of them here would be read once. Read them with
`--sources`, or filter to what you actually have access to:

    python scripts/check_evidence_saturation.py --sources
    python scripts/check_evidence_saturation.py --sources --query zalo

## How many people is enough

For the list of themes, twelve is the number with evidence behind it. Guest, Bunce and Johnson's 2006
study of sixty in-depth interviews found the first six produced roughly three quarters of the codes
the full set eventually yielded, and twelve produced around nine tenths. Hennink and Kaiser's 2022
systematic review of saturation studies put code saturation in the nine-to-seventeen range, with
interpretation stabilising later, around sixteen to twenty-four.

Two floors follow, and the script holds both. Twelve, below which you have a discovery sample: good
for finding a theme, no basis at all for saying the list is complete. And sixteen, below which the code
set can be closed but the reading of it cannot.

The honest way to use the curve is to watch it rather than count to a target.
`check_evidence_saturation.py` prints new themes per respondent and calls the set closed only when
three consecutive respondents have taught you nothing. One quiet interview in the middle of a study is
ordinary and means nothing.

One caveat, and it is the same one that governs every calibration in this skill. The milestone table
says things like "eleven themes after twelve respondents, a hundred percent of the themes this study
eventually found". That denominator is self-referential. It is a share of what you found, not a share
of what exists, and a study that stopped early will report a beautiful hundred percent. The curve can
tell you the set has stopped growing. It cannot tell you the set is complete, and no amount of
interviewing turns the first statement into the second.

## The number that surprises everybody

Ninety-three.

That is how many respondents it takes to measure a share near a half to within twenty points, at
ninety-five percent confidence. For ten points it is three hundred and eighty-one. Check both:

    python scripts/check_evidence_saturation.py --needed 0.5 0.2
    python scripts/check_evidence_saturation.py --interval 18 0.83

The consequence is blunt, and it removes a whole genre of slide. **A qualitative study cannot produce a
percentage.** Not "should avoid" - cannot. Eighteen switch interviews are ample for closing a theme
list and they license zero shares, because at eighteen even a lopsided fifteen-of-eighteen carries an
interval running from sixty-one to ninety-four percent. A thirty-three point spread is a direction.

If the decision genuinely needs a percentage, it needs a survey of roughly a hundred people per
segment, and a survey is a different instrument with a different weakness: non-response bias, which
does not shrink as n grows. You are trading an unquantified sample for a quantified one with an
unquantified tilt. Do it deliberately, and say which one you did.

What eighteen interviews are excellent for is the thing a survey cannot do at all: finding the theme
nobody knew to put on the questionnaire. Use the two instruments for the two jobs and stop asking
either to do the other's.

## The row nobody writes down

Here is the structural defect in nearly every research file ever assembled. It records the times
somebody raised a theme, and never the times somebody was asked about it and said no.

Without that second kind of row the denominator silently becomes the numerator. Five customers raised
the price objection, out of five customers who raised the price objection: a hundred percent, and no
information whatsoever. The arithmetic of a unanimous theme is indistinguishable from the arithmetic of
a well-supported one, which is exactly why reading the summary cannot catch it.

So the coded file carries a `stance` column with three values. `raised` is unprompted. `confirmed` is
agreement after being asked. `denied` is asked, and said no. The script computes prevalence over
`raised + confirmed + denied`, and when a theme has no `denied` row anywhere it prints the raw count
and refuses to print a share. That refusal is the most useful thing in the script.

It also changes how the interview runs. Once the theme list is forming, start asking later respondents
about earlier respondents' themes explicitly, and write down the no. A study of eighteen where the last
six were asked against the first twelve's themes is worth far more than a study of thirty where
everybody was only ever allowed to volunteer.

## Frequency is not intensity

The old version of this file said "distinguish frequency from intensity" and stopped, which is a
correct sentence that gives nobody anything to do. Here is the grid, and each corner is a different
instruction.

**Common and blocking.** Many people raised it and it stopped them buying. This is the positioning
problem. Lead with it.

**Common and passing.** Many people mentioned it, few said it decided anything. Table stakes. Fix it,
and never build the campaign on it: it is necessary and not sufficient, and a campaign led by table
stakes reads as a brand with nothing to say. This corner catches the most decks, because the loudest
theme in the file looks like the answer.

**Rare and blocking.** Few raised it, and for those few it killed the purchase. Usually a segment
problem, an operational gap or a missing form - a VAT invoice, a payment method, a size. It belongs on
the roadmap or in a segment-specific message, not in the main campaign.

**Rare and passing.** Log it and move on.

The script flags the two corners readers get wrong, `common-but-passing` and `rare-but-blocking`, and
deliberately does not rank them against each other. They are different jobs for different people, and
a single ranked list would force one of them to pretend to be the other.

## One source is not evidence

A theme visible through exactly one source is that source's bias until a second source sees it. Not
false - unverified, and unverified in a known direction, because the table already says which way that
source leans.

The script flags it as `single-source`. The fix is not more of the same source; forty more reviews will
reproduce the same J-shape. The fix is a source with a different blindness. If reviews say the
ingredient list is unclear, go looking for it in the pre-purchase questions, where a different
population with a different motive is typing.

## Coding: the file the script reads

One row per respondent, per theme, per stance. Columns: `respondent_id`, `sequence`, `source_id`,
`code`, `stance`, `intensity`, `provenance`.

An eighth column is optional and its name is load-bearing. Call it `verbatim_ref` and it holds a
locator - a recording id, a thread number, a ticket - which nothing reads and every auditor wants.
Call it `verbatim` and you are declaring that the cell holds the customer's actual words, which is
what the rights gate below inspects. The shipped example uses `verbatim_ref` on all sixty-one rows,
so its rights gate reads `skipped`: there is nothing to check, which is the point.

Four conventions decide whether the file is worth anything.

**The respondent is the unit, not the quote.** Prevalence counts people. Count quotes instead and the
articulate customer who said the same thing four different ways becomes a trend.

**`sequence` is collection order, and it is not decorative.** The saturation curve is a function of the
order you heard things in. Sorting the file by respondent id destroys it.

**`intensity` is three named levels, not a five-point scale.** `passing`, `emphasised`, `blocking`. A
numeric scale invites a mean, and the mean of an invented scale is not a measurement.

**`provenance` is required on every row, and the script fails without it.** A date and a locator. This
is the same discipline `market-data-collection.md` applies to published numbers, for the same reason: a
claim whose origin nobody recorded cannot be re-checked, and six months later that is the same as a
claim nobody made.

## Reading a small-study result

Consider a small Vietnamese serum study asking why first-time buyers do not come back: eighteen
respondents, five sources, sixty-one coded rows.

It lands on `review`, which is what an honest study looks like. The theme list is closed - the last new
theme arrived at respondent twelve, and the final three taught nothing. And not one of its eleven
themes carries a quotable share, exactly as the sections above predict at eighteen.

The two theme-level flags are the part worth reading twice. `worried-about-counterfeit` is the biggest
theme in the file, ten of eighteen, and it is flagged `common-but-passing`: nearly everybody mentions
fear of a fake product, and two said it stopped them. So it belongs in the proof layer - batch codes,
authorised-seller wording, an unboxing - and a campaign built on "we are genuine" would be a brand
saying the minimum out loud. Meanwhile `no-vat-invoice` was raised once, by somebody it stopped
completely, and six people were asked and said it was irrelevant to them. One blocked buyer is not a
campaign, and it is a real fix for a real segment.

`waited-for-livestream-discount` is the theme worth carrying into another unit. Six of the seven asked
agreed they had held off buying to wait for a live-stream price. That is a retention symptom rather
than a pricing one, and `lifecycle-retention.md` already holds the rule it triggers: diagnose before
discounting, because a discount teaches the customer to wait for the next discount and leaves whatever
they did not believe entirely intact.

## Whose words are these

A public review is not public-domain. It is the author's; the platform's terms of service license the
platform and not you; and quoting a named customer in an advertisement needs their consent regardless
of copyright. `evidence-sources.csv` carries `quotable_publicly` for every source, with four values:
`with-permission`, `aggregate-only`, `no`, and `check-the-licence`.

The practice that follows is to store a pointer, not the text. Code the theme, record the locator,
leave the words in the recording or the thread where they already live. This costs nothing, and it
means the research file is not itself a liability - a support-ticket export or a chat log carries order
numbers, phone numbers and whatever else the customer happened to type. The script has a gate for it:
put a `verbatim` column in a file and fill it from a source the table marks unquotable, and
`stored-quote-rights` fails.

## What this unit cannot do

- **Causation, at all.** An exit reason is the last straw, not the load. Post-hoc rationalisation and
  reason are indistinguishable in an interview, and the more articulate the customer, the more
  convincing the rationalisation.
- **The counterfactual.** Every source here reaches people who acted. The customer who considered
  switching and stayed put is the comparison the whole exercise wants, and is nearly impossible to
  recruit, because nothing happened to them.
- **Fix a leading question.** Ask "was the price too high?" and a share comes back, with a clean Wilson
  interval around a number you manufactured. Every gate in the script will pass. Nothing here inspects
  the questionnaire.
- **Say anything about non-responders.** Response bias is the one weakness that does not shrink with
  sample size. A survey with a five percent response rate and an n of four hundred is four hundred
  unusual people.
- **Close the theme list for real.** Saturation is a statement about your sample. Treat a hundred
  percent milestone as a warning rather than a result.
- **Separate the source from the finding when only one source saw it.** That is what the
  `single-source` flag exists to admit rather than to solve.

## The handoff

End a customer-evidence pass with four things and no more.

One beachhead segment, named by a situation rather than a demographic. Its job to be done, in the
customer's words and not yours. Its awareness stage, because that decides whether the next asset has
to argue or only to explain. And the single largest evidence gap: the theme you would most like to be
wrong about, which source with a different blindness would test it, and the headcount that source
needs before its answer counts.

That last item is the deliverable research skips most often, and it is the one that makes the next pass
cheaper than this one.

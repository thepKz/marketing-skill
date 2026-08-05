# Titles

## Contents

- What this unit is for
- The gap it fills, with the exit codes
- The three failures
- Why the set matters more than the title
- The instrument
- Vietnamese: what is actually wrong
- What is not in this unit, and where it lives instead
- What this unit cannot decide

## What this unit is for

A title is the only line most readers finish. It is also the line written last, in the five minutes
after the work is done, by the person least able to see it from outside. Everything else in this
skill measures copy at paragraph length. Nothing measured a headline until this unit existed.

## The gap it fills, with the exit codes

The three copy gates exclude the length band a title occupies, and they say so in their own source.
`rewrite_human.py` sets `SHORT_FORM_UNITS = 120` and stops measuring cadence below two sentences.
`check_specificity.py` sets `SPECIFIC_FLOOR_UNITS = 40` with the comment that below it "the piece is
a button, a headline or a badge". `check_address_register.py` matches that floor deliberately. Each
decision is right for the reason given, and together they mean no instrument here had ever read a
headline.

Measured on this repository on 2026-08-05, before `check_title.py` existed:

| Title | rewrite_human | check_specificity | check_address_register |
|---|---|---|---|
| Lấy cấu trúc. Không sao chép dấu vân tay. | exit 1 | exit 3 | exit 0 |
| Khám phá bí mật đằng sau thành công: 5 điều bạn cần biết ngay | exit 0 | exit 0 | exit 0 |
| Không chỉ là một tô bún, mà còn là cả một câu chuyện | exit 1, no reason printed | exit 3 | exit 0 |

Row two is the finding. A curiosity gap, an imperative to a stranger, a colon deck and a listicle
number, in twelve words, and every gate cleared it silently.

Row one shows the other failure. The cadence gate does fire, on `burstiness-cv` (0.33 against a 0.45
floor) and `long-short-ratio` (2.0 against 3.0) — the rhythm of a paragraph, measured across two
fragments that were never a paragraph. It answers a question the title did not ask while staying
blind to the one it did, which is worse than silence: a writer who fixes those two numbers has made
the title longer and no better.

Row three was a bug, found by running these three lines rather than trusting the exit code.
`rewrite_human.report` returned early on short input, before the tells section and the verdict, while
`main` still failed on a blocking tell. So on every headline, button and badge, a blocking tell set
exit 1 and the printed report named no reason. Fixed 2026-08-05. A gate that fails without
explaining stops being read, and then its exit code stops being read too.

## The three failures

Only the third is about wording.

**It is about the maker.** The subject is the artefact or the process — brief, output, pipeline, hệ
thống, cơ chế, bố cục. The title is written last by whoever just built the thing, so the freshest
noun in their head comes from the workshop, and the reader has never been in the workshop. This is
the defect underneath most of the others, and it is the one the table calls `workshop-noun`.

**It reuses one device.** No single title is wrong for being `A, không phải B`. A page where nine of
sixteen are two clipped fragments is one voice with one trick. Repetition is what a reader registers
as machine-written — not any individual line, which is exactly why rereading your own titles one at a
time cannot find it.

**It carries no noun the reader owns.** Not computable, declared as such below.

## Why the set matters more than the title

This repository's own landing page, both versions, through `check_title.py`:

| | HEAD, 16 titles | working copy, 17 titles |
|---|---|---|
| device-concentration | 0.56 (9/16, clipped-parallel) | 0.12 (2/17, colon-deck) |
| device-free-share | 0.31 (5/16) | 0.76 (13/17) |
| workshop-noun | 4 of 16 | 1 of 17 |
| contrastive-negation | 3 of 16 | 0 of 17 |

Every one of those sixteen titles is defensible alone. Read as a page they are a template being
filled in nine times. That is the measurement no per-line checker can make, and it is the reason
`data/title-devices.csv` carries a `budget_per_set` column rather than a verdict.

The two thresholds are house rules with no published source, and they are graded that way in the
table. What is defensible is the shape rather than the decimal: a device becomes a voice by
repetition, and the third occurrence is roughly where a reader stops reading the sentence and starts
reading the pattern. Concentration at a quarter lets a set of twelve share a device three times,
which leaves deliberate anaphora across a page available to anyone who wants it on purpose. The
device-free floor exists because concentration alone can be satisfied by using six different tricks
once each, and a page that does that reads as a tour of every trick available.

## The instrument

```
check_title.py --title "Nồi nước dùng bắt đầu từ bốn giờ sáng"
check_title.py --title "..." --title "..." --title "..."
check_title.py --set titles.txt --lang vi
check_title.py --page docs/index.html
check_title.py --devices
```

Exit 0 clean and judged, 1 usage, 2 a blocking device or a device over its set budget, 3 everything
measurable passes and the two judgements below are still open. A single title cannot reach exit 0,
and that is deliberate.

Two numbers in the script are per-language, and the reason is arithmetic rather than taste. It counts
whitespace tokens, so a Vietnamese token is a syllable where an English one is a word. The nine-word
limit in `copy-formulas.csv` one-idea-headline becomes twelve for Vietnamese; a flat nine would hold
Vietnamese to two thirds of the length the formula grants, which is not the formula being stricter
but the formula being mismeasured. The clipped-fragment threshold moved from five to seven for the
same reason, and it moved because a test caught it: `Không sao chép dấu vân tay` is six tokens and
three words, so five missed the exact Vietnamese case the row was written for.

## Vietnamese: what is actually wrong

Subject ellipsis is native and grammatical in Vietnamese. A title with no subject is not the defect,
and anyone told to "add a subject" will produce something worse. What actually reads translated:

- the nominal fragment holding the front of the sentence — `Việc…`, `Sự…`, `Quá trình…`
- the imperative with no addressee and no particle, which reads as signage rather than speech
- the long dash `—`, where Vietnamese punctuates with a comma, a colon or a full stop
- parallel-clause symmetry tight enough that both halves have the same syllable count

Each of these is a row in the table with its own severity. None of them is "no subject".

## What is not in this unit, and where it lives instead

`khong-chi-ma-con` — the `không chỉ… mà còn` construction — is in `data/translation-tells.csv` and
fires through `rewrite_human.py`, correctly on short input since the fix above. It is not duplicated
here. One defect with two owners is a defect that gets half-fixed twice.

`tricolon` and `not-just-but` exist in `data/slop-tells.csv` for body copy. The `tricolon` row here
is a separate measurement, not a copy: in a title the cost is higher because there is no room to make
any of the three items specific, and the budget is per set rather than per document.

`question-open` in `copy-formulas.csv` already states the rule that a question everybody answers yes
to filters nobody. The table's `question-anyone-answers` row is where that rule gets enforced at the
one length where it happens most.

## What this unit cannot decide

Two judgements are printed as open on every clean run, which is why a clean run exits 3.

**Does the title name a noun the reader owns** — something they have, want, sell or are losing. No
word list can settle it, because the same noun is the reader's in one market and the workshop's in
another. `brief` is a workshop noun to a shop owner and the product itself to an agency.

**Was the metaphor earned.** A figurative title borrows against context the reader has not been given.
In body copy the next paragraph repays it; a title has no next paragraph. Whether the rest of the page
introduces the image is a judgement about the page, and this script reads one line at a time.

It also cannot tell a device used on purpose from a device used by default. Every threshold here is a
budget rather than a ban for that reason, and a writer who spends the budget knowingly has used the
instrument correctly.

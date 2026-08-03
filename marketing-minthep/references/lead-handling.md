# Lead handling: from the first message to the closed order

A campaign that works produces messages. Twenty of them. On a Tuesday afternoon, spread across four
apps, each asking something slightly different. This unit is about what happens next, which the rest
of this skill had nothing to say about.

The silence was structural rather than accidental. `vietnam-operating-reality.md` records that the
command surface is a graph over artefacts, that the inbox and sales roles produce no artefact, and
that they are therefore invisible to it while consuming more of the day than anything else. That was
an honest description of a hole and it was also the hole.

So the handling itself becomes the artefact here: a declared set of decisions about who is worth
answering, how fast, how many times, and what gets written down when the answer is no.

## The states a contact actually moves through

Nine states. They live in `data/lead-states.csv`, each defined by an observable moment rather than by
how the conversation feels. `scripts/plan_lead_flow.py --states` prints them with the Vietnamese
name, what may be counted at each, and what that count does not prove.

| State | Enters when | Leaves when |
|---|---|---|
| `new` | They send a first message, tap the call button, or submit a form | You have sent a reply a person wrote or approved |
| `replied` | Your reply is sent | A qualification question has been answered, either way |
| `qualified` | Fit and intent are both answered yes, from the thread | A price is given in writing |
| `disqualified` | You have written down which criterion failed | Terminal |
| `quoted` | A specific price for a specific scope is in writing | They respond to it, in either direction |
| `negotiating` | They ask for a change to price or scope | They agree or refuse |
| `won` | They pay, order, or confirm in writing | Terminal |
| `lost` | They said no, bought elsewhere, or the deadline passed | Terminal |
| `stalled` | Your follow-up ladder is exhausted with no reply | They reply, or it becomes `lost` |

Two things about that table earn their place. Every entry moment is something you could point at in a
screenshot, because a stage defined by seller optimism drifts upward on a bad month and takes the
forecast with it. And `disqualified` is a state rather than a failure. Without it, saying no to a bad
fit feels like giving up, so the bad fit gets four hours instead of four minutes.

## Qualification is two questions, not one

Fit and intent are separate axes, and collapsing them is the most common error a non-marketer makes
here. Fit is whether this person matches what you sell. Intent is whether they mean to buy now. Both
must be true.

|  | Low intent | High intent |
|---|---|---|
| **Good fit** | Worth staying in touch with. Not worth chasing today | The only quadrant that earns your afternoon |
| **Poor fit** | Answer politely, close the thread | The dangerous one. Says yes fast, argues later, and refunds |

The bottom-right quadrant is why `disqualify_reason_list` is a declared field. An eager customer for
something you do not do well is the most expensive kind you can take on. Enthusiasm is not fit.

In chat the qualifying answer usually arrives before you ask for it. The district, the quantity, the
date of the wedding: people volunteer the deciding fact in their first two messages. Read before you
interrogate. A qualification script applied to somebody who already told you the answer reads as a
call centre, and the register gate in `address-register.md` is about the same instinct.

## First response: your number, not ours

This unit ships no response-time target. That is a deliberate refusal, and it needs stating plainly,
because every number in circulation would have been easy to copy.

The lead-response literature everybody quotes traces back to one study of business-to-business web
forms answered by telephone in the United States, funded by a company selling dialling software. It
may well be right. It was not measured on a Zalo thread about a birthday cake, and this corpus holds
no measurement of chat commerce in Vietnam.

The attempt to verify platform-published thresholds — Shopee's chat response rate, the Meta
responsiveness badge, Zalo reply windows — returned nothing citable on the retrieval date. So those
numbers are absent here rather than approximated.

`lifecycle-retention.md` set the precedent for send frequency: an imported rule of thumb about two
sends a week is a deliverability opinion wearing a legal coat. A five-minute reply target would be
the same opinion wearing a stopwatch.

So you declare the target and the hours it applies inside, and the script holds you to what you
declared and certifies nothing. Read your own platform dashboard for what the surface measures you
on. That number is real. It is about your account, and it is the one with consequences attached.

One gate here is not about speed at all. `reply_is_human_written` exists because an auto-greeting
satisfies a platform response metric without answering anybody. The metric improves. The conversation
does not.

## The ladder, and the rule that ends it

A follow-up ladder is a declared number of touches with a declared gap before each. The script checks
that the shape is coherent, one gap per touch and every gap a positive number of hours, and prints
the span in days. It does not tell you the touch count. The widely repeated figures trace to vendor
content citing other vendor content, and a ladder built on one of those is a guess with a footnote.

`stop_rule` is the field that matters most and the one most often left empty. Without it, nothing
ends. A ladder that runs until you get bored is not a rule and cannot be handed to anybody else.

Whether you may send those touches at all is a different question. Legality is not tactics. Stored
personal data plus scheduled repeat contact is what Điều 10.1.b regulates, and the test there is the
consumer's wishes rather than your unsubscribe list. `lifecycle-duties.csv` answers it; this script
counts the touches and names that file.

## Quoting in chat, and what it costs to do it loosely

Most prices here are given inside a chat thread, which means the quote has no document behind it
unless you make one. `quote_in_writing` asks whether the scope sits beside the price. Write the scope
down. They will remember the number and you will remember the conditions, and you will lose it.

`quote_expires` is the other half. A quote that never expires cannot be followed up without inventing
a reason to follow up.

Haggling is expected here and is not an objection. What deserves suspicion is a discount given with
nothing asked in return: volume, timing, a review, a referral, payment before dispatch instead of
cash on delivery. `pricing-and-offers.md` holds the arithmetic for what a concession actually costs.

## Why the loss log says price

Price is the reason buyers give. It ends the conversation politely, and it blames nobody in the room,
which is the same reason sellers write it down. A loss log where price dominates is usually a log
that stopped asking.

So declaring price as the loss reason requires the gap and what else was true. Ask for the gap. This
is a house-rule caution rather than a cited finding: no measurement in this corpus establishes the
bias, and the practice of interviewing lost buyers instead of trusting the seller's note is not
something this skill can point at a source for. It is still the gate that turns a loss log into
something you can read six months later.

## The funnel, and the rate that is not a rate

`--funnel` takes a CSV of `state,count` and chains the stages: reply rate, then qualification, then
quote, then close, then contact to won overall. It also does two things a spreadsheet will not.

It refuses a percentage below a base of thirty. Thirty is the floor. Under it the script prints the
count and a 95% Wilson interval instead, because two of three reported as 67% is how a quiet week
becomes a strategy. The interval is Wilson rather than the textbook one so that it keeps a width when
the numerator is zero or equals the base, which is exactly where a small business lives.

And a later state holding more contacts than the one it is entered from does not warn. It fails
outright. That shape usually means marketplace chat was never counted at the top: Shopee and TikTok
Shop chat cannot be exported, so `manual_tally` is a gate rather than a question. Without the tally
those contacts are missing from the base and every rate below reads as a collapse that did not happen.

No lead value is computed anywhere. `tracking-events.csv` already refuses one unless a verified
average exists, and inventing it is how an assumption becomes a reported number.

## Running it

```
python scripts/plan_lead_flow.py --states
python scripts/plan_lead_flow.py --template sheet.csv
python scripts/plan_lead_flow.py --audit sheet.csv
python scripts/plan_lead_flow.py --funnel counts.csv
```

Exit 0 is clean, 2 is a failed gate, 3 is computable but unsettled. A blank field fails its gate,
because the fastest way to pass a declaration sheet is to leave it empty.

## What this does not establish

The audit grades whether your process is defined, not whether it is good. Nothing here measures
whether your criteria pick the right customers, whether your target is fast enough for your market,
or whether your close rate is normal for your category. That last one would need a benchmark, and
`marketing-benchmarks.csv` carries none for Vietnamese chat commerce.

It does not manage contacts either. Not a CRM. This is a definition and an arithmetic, and it stores
nothing about any person.

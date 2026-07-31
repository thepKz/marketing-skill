# Specificity: counting what a competitor could not copy

## Why this is a separate check from cadence

`rewrite_human.py` measures the shape of prose. It can pass this:

> Chúng tôi cam kết mang đến trải nghiệm tốt nhất cho khách hàng. Đội ngũ chuyên nghiệp, tận tâm sẽ
> đồng hành cùng bạn trên mọi hành trình.

Good length variance, no pictograph, one address register, no em dash. It is also the single commonest
machine-written line in Vietnamese marketing, and it contains nothing. `rewrite-human.md` already
concedes this: a draft can pass every gate there and still be unpublishable, because those gates
cannot tell you whether the copy is true or whether the claim is provable.

The rule was already written down. Step 1 of the repair sequence says to list every checkable thing in
the draft, and that under three the problem is not cadence. Until `check_specificity.py` there was
nothing that counted, and a rule with no instrument is a rule that gets skipped - counting facts by eye
in your own draft is exactly the task people are worst at, because the writer knows what they meant.

There is a second, worse failure this prevents. Rhythm work deletes specifics, because a specific is
the awkward part of a sentence. `Giao trong 2 giờ ở Gò Vấp` has a lumpy middle; `Giao hàng nhanh
chóng, tận tâm` flows. Run the cadence gate on its own and it will reward the second one. Run this
first and the trade is visible.

## What counts as a fact

Four classes, and the test is whether a competitor could publish the sentence unchanged:

| Class | Counts | Does not count |
|---|---|---|
| `quantity` | A number carrying a unit or a currency: `2 giờ`, `45.000đ`, `250ml`, `40kg`, `87%` | A bare number: `3 lý do`, `bước 2`, `top 5`. That is how a listicle is built, not evidence |
| `date` | `ngày 12 tháng 3`, `thứ hai`, `Q3`, `12/03/2026`, `2026` | A season with no year, `sắp tới`, `hiện nay` |
| `name` | A place, person, brand or acronym mid-sentence: `Gò Vấp`, `GHTK`, `Nguyễn Văn A` | A name at the start of a sentence, or a title-cased line |
| `contact` | A phone number, an email, a URL, a domain | `liên hệ ngay`, `inbox để biết thêm` |

Two deliberate blind spots, both erring toward reporting less specificity than the draft has, because
a gate whose failure blocks shipping should not fail on work that is fine:

- **A name at the start of a sentence is invisible.** There is no way to distinguish `Gò Vấp là nơi
  rang` from `Chúng tôi là đơn vị` without a gazetteer. Vietnamese writes each syllable of a name as
  its own token, so dropping only the first capital would count `Vấp` as a name in every sentence that
  opens with one.
- **A title-cased line contributes no names at all.** `Cà Phê Rang Mộc Nguyên Chất` is five capitals
  and nothing checkable. Counting it would mean a writer could clear the fact floor by capitalising a
  headline, and `translation-tells.csv` already flags that habit as `title-case-vi`.

## The gates

| Gate | Threshold | What it catches |
|---|---|---|
| `fact-floor` | at least 3 checkable things | The draft has no content. Every rhythm edit from here makes it read better while still saying nothing, which is worse, because it removes the signal that it is empty |
| `fact-density` | at least 1.5 per 150 units | Three facts in a headline is dense. Three in a thousand words is decoration around a claim nobody has to stand behind |
| `brand-swap` | at most 50% of sentences carrying nothing | Cover the brand name. A sentence with no number, date, place or name is one a rival could ship unchanged, which means it is not about this business |
| `empty-adjective` | at most 1.0 per 150 | An evidence adjective alone in its sentence, standing in for the fact it replaced |
| `hedge-stack` | at most 1 hedge per sentence | Two hedges make the claim unfalsifiable, which is how a draft avoids ever being wrong and also ever being believed |
| `sourced-number` | 0 unsourced statistics | A percentage or a multiplier with no source nameable in the same sentence |

Below 40 units the check is **skipped, not passed**. A headline or a button carries its fact in the
frame around it, and demanding one inside the string would fail every good caption.

### Every threshold here is a house rule

No standard governs how specific marketing copy has to be. The contrast ratios in `colour-gates.csv`
are WCAG's and carry `standard-requirement`; every number in the table above is `house-rule`, is this
skill's own, and is open to argument. Dressing them up with a citation would be the exact failure this
unit exists to catch, one level up.

## The two gates worth understanding properly

### `empty-adjective`: the word is not the defect, the substitution is

`slop-tells.csv` calls `adjective-substitute` critical. But look at these two:

- `Cà phê premium này ủ lạnh 80 giờ ở Gò Vấp` - `premium` summarises a fact standing right beside it.
- `Cà phê của chúng tôi là loại premium, chất lượng đảm bảo` - `premium` is what replaced the fact.

Same word, opposite defect. A phrase list matching one string at a time cannot tell them apart; only
something reading the whole sentence can. That is why this gate lives in a script and why the script
reads its adjective list out of `translation-tells.csv` rather than carrying a copy - the table is
where a new tell gets added, and a second list here would drift from it within a month.

So the fix for a failing `empty-adjective` is almost never to delete the adjective. It is to put the
fact back and then decide whether the adjective is still doing anything.

### `sourced-number`: only a claim about the world needs a citation

Four shapes stay exempt, and the exemptions are the reason this gate is usable:

- **A price.** `45.000đ` is the brand's own fact.
- **A plain count.** `mỗi tuần chỉ 200 chai` is its own inventory.
- **A discount.** `giảm giá 20%` is its own offer.
- **A concentration or a composition.** `axit azelaic 10%`, `cotton 95%` is what is in the bottle or
  the fabric.

That last one was a false positive this gate was caught producing on the first real draft it ever ran
on, and it is why the logic is inverted. The default for a percentage is **exempt**; it only counts as
a claim when the sentence also quantifies a person or an outcome - `87% khách quay lại`, `hiệu quả lên
tới 90%`. A multiplier needs no such test, because `nhanh hơn 3 lần` is comparative by construction.

If the source cannot be named in the same clause, the number is decoration: delete it, or go and
measure it.

A checker that demanded a citation for `200 chai` would be right about nothing and would teach the
copywriter to stop running it, after which nothing is measured at all. That is the failure mode the
four-status vocabulary exists for, and it is why a price list comes back `review` rather than failing
`brand-swap`: a spec table has no connective sentences, and judging it as prose is judging the wrong
document.

## Running it

```
python scripts/check_specificity.py --check draft.md
python scripts/check_specificity.py --text "Giao trong 2 giờ ở Gò Vấp, 45.000đ một ly."
python scripts/check_specificity.py --check draft.md --json
python scripts/check_specificity.py --targets
```

Exit codes: 0 clean, 1 usage error, 2 a gate failed, 3 computable but unsettled. Run it **before**
`rewrite_human.py`, not after. Fixing content changes the cadence; fixing cadence does not add content,
and doing it in the wrong order means measuring the rhythm of prose you are about to rewrite anyway.

The report ends with the sentences carrying nothing checkable, listed verbatim. That list is the work:
each line gets a number, a date, a place or a name, or it gets cut.

## What this does not establish

It counts specifics. It cannot tell you a specific is **true** - `giao trong 2 giờ` counts whether or
not anything arrives in two hours, and `87%` counts as sourced the moment the word `theo` appears in
front of it, regardless of what follows. Provable claims are `claims-proof-ledger.md`'s job and a claim
id is issued there, not here.

It also cannot tell you the facts are the *right* facts. A draft can clear every gate above with three
numbers nobody cares about. What the reader needs to know is a positioning question, and passing this
check means the copy is about something, not that it is about the correct thing.

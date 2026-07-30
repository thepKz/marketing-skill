# Rewrite human — one draft, worked end to end

A coffee roaster's About-us paragraph, the kind produced by asking a model for "professional
marketing copy". Every sentence is grammatical. The paragraph says nothing a buyer can check.

## Run it

```bash
python ../../../scripts/rewrite_human.py --check 01-draft-vi.md
python ../../../scripts/rewrite_human.py --check 02-rewrite-vi.md
python ../../../scripts/rewrite_human.py --check 03-transcreation-en.md
```

The first exits non-zero and names six blocking failures. The other two exit zero.

| File | What it is |
|---|---|
| `01-draft-vi.md` | The draft as received. Four sentences, no checkable fact |
| `02-rewrite-vi.md` | The rewrite. Same product, facts supplied from the shop |
| `03-transcreation-en.md` | English built from the same facts, not translated from the Vietnamese |

## What the numbers showed

The draft measured CV 0.10 against a target of 0.45 — four sentences within a syllable or two of
each other, which is the flatness a reread cannot see. It also had no landing beat at all: every
claim arrived mid-sentence, so nothing landed. Four calques fired, including `một trong những
đơn vị hàng đầu` and `chất lượng cao`.

Both were symptoms of the same thing. The draft had nothing to say, so no sentence had a reason
to be short and no claim had a place to land. Rhythm could not have been fixed first. The facts
came from the shop — batch size, roast date on the bag, the price, the seven-day swap — and the
cadence followed from where those facts needed a beat.

Note the length. The rewrite carries seven checkable facts and is barely longer than the draft
that carried none.

## Why the English is not a translation

The Vietnamese middle paragraph is three sentences; the English is four. `Không thấy ngày rang
thì đừng mua, của ai cũng vậy` became two sentences in English, because English wants the
aside to stand on its own — `No date, no sale. That goes for anyone's beans, not just ours.`

That is the test. If the sentence count had survived intact, the words were translated and the
decisions behind them were thrown away. Prices, the roast mechanism and the swap window match
exactly. Rhythm and sentence boundaries do not, and should not.

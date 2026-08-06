# Output contract: how a deliverable reads

## The layer the sentence gates could not see

A draft can pass every sentence instrument — specific facts, human cadence, one register — and
still be recognised as machine-written from across the room, because the tell has moved up a
level: the document's *shape*. An announced opening ("Dưới đây là kế hoạch toàn diện..."), three
symmetric sections with three bold-led bullets each, headers that name categories every document
has, a closing paragraph that restates the page above it. No sentence in that document is wrong.
The document is.

This contract is the positive spec for that level, and `scripts/check_output_shape.py` is its
gate. The calibration model, named by the owner (2026-08-06), is the answer format Perplexity
made normal: the answer arrives first, every claim carries its evidence at the point it is made,
and the structure exists to be scanned by someone who has already decided how much they care.
What is borrowed is that discipline. What is not borrowed is the source-dump — a bibliography
block is chrome, not evidence; the citation belongs inside the sentence it supports, which is
already core rule 6.

## The contract

1. **The first sentence answers.** Not the topic, not the method, not what the document is about
   to do — the verdict, the number, or the decision. Everything after the first sentence is
   evidence for it. A reader who stops after one line has the answer; a reader who keeps going is
   choosing depth, not hunting for the point.
2. **Headers assert.** "Giá 89.000đ đứng giữa phân khúc" is a finding; "Phân tích giá" is a
   drawer label. A header that could sit unchanged on a competitor's document is the header-level
   brand-swap test, and it fails the same way. Assertive headers also make the document scannable
   as a chain of claims — the header sequence alone should read as the argument.
3. **Evidence rides the claim.** The number, its source, and its date live in the sentence that
   uses them — "12 quán khảo sát ngày 2026-08-01 tính 75.000–120.000đ" — never in a "Nguồn"
   section the reader must join against the prose. A claim and its evidence separated by a page
   is a claim the reader has to take on faith twice.
4. **Form follows content.** A table carries a comparison across items; prose carries reasoning;
   a bullet list carries a true enumeration — short, parallel, seven items or fewer. The bold-led
   bullet grid ("**Tiết kiệm:** tối ưu ngân sách") is banned outright: it is prose wearing a
   list's clothes, and it is the single most recognisable AI page shape. If the bold labels read
   as a sentence when joined, write the sentence.
5. **Sections are as unequal as the knowledge is.** The section with the strongest evidence is
   the longest; the section where nothing is known is one honest line, not padded to match its
   siblings. Symmetric section lengths and identical bullet counts mean the content was cut to
   fit a rhythm — which is the model's rhythm, not the argument's.
6. **No overture, no recap.** Cut the first paragraph if it announces what the document will do;
   cut the last if it summarises what the page just said. In a one-page deliverable the recap is
   the reader's second reading of the same claims, and it is where the hedged, softened,
   slop-flavoured restatement lives. The document ends on its most concrete instruction —
   a date, a next action, a number to watch.
7. **The reader's decision sets the length.** A pricing call is one page even when the research
   was a week; the depth goes into the run workspace, not the deliverable. Length that tracks
   effort instead of the decision is the producer billing the reader for hours.

Chat replies follow the same contract at smaller scale: result in the first line, a table when
facts enumerate, no narration of process, done.

## The banned shapes, mechanically

| Shape | Gate | Severity |
|---|---|---|
| Opening that announces the document | `announce-open` | critical |
| Closing paragraph that restates the page | `recap-close` | critical |
| Headers from the universal-category set (Tổng quan, Lợi ích, Kết luận, Introduction, Overview...) | `generic-headers` | high |
| Bold-label bullet grid | `bold-led-bullets` | high |
| Sections sized by symmetry | `uniform-sections` | review |
| Every list the same length | `uniform-bullet-counts` | review |
| No checkable fact in the opening | `verdict-missing` | review |
| Short noun-label headers throughout | `label-headers` | review |

Exit 0 clean, 2 failed, 3 unsettled. Review findings are findings, not passes: `verdict-missing`
on a document whose answer genuinely sits in paragraph four is the contract's first rule failing,
found by its weakest detector.

## One decision, written twice

Machine-shaped: *"Dưới đây là phân tích giá toàn diện cho quán. ## Tổng quan — **Thị trường:**
cạnh tranh cao. **Khách hàng:** nhạy cảm về giá. ## Kết luận — Tóm lại, quán nên cân nhắc điều
chỉnh giá phù hợp."* Every sentence survivable, nothing said, and the reader still does not know
the price.

Contract-shaped: *"Giữ 89.000đ — quán đứng giữa phân khúc Gò Vấp (12 quán khảo sát ngày
2026-08-01 tính 75.000–120.000đ) và biên đóng góp 41% chịu được khuyến mãi 15% mà không lỗ."*
One sentence, and the reader can already act; the sections after it exist for the reader who
wants to check.

## Where it runs

Stage 2 of the anti-slop layer (`anti-slop-index.md`): after `check_specificity.py`, because an
empty document is not worth shaping, and before `rewrite_human.py`, because restructuring
rewrites sentences and cadence measured first is a wasted pass.

```
python scripts/check_output_shape.py --check deliverable.md
```

## What this does not establish

Shape is necessary, not sufficient: a document can open with a verdict that is wrong, assert
headers over fabricated numbers, and pass this gate while failing core rule 1. Truth stays
upstream. And the gate reads markdown and plain text only — an HTML artifact's shape is judged
by looking at the render, which no regex replaces.

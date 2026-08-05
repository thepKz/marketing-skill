# Rewrite human

Take a draft that reads machine-written or machine-translated, and make it read like a person wrote it in that language first. This is not editing for grammar. Grammatical prose is exactly what fails here.

Two distinct failures arrive looking the same.

**Machine cadence.** Every sentence is a similar length, every paragraph a similar shape, every list three items long, connected by `furthermore` and `moreover`. Each sentence passes on its own. The paragraph reads flat because uniformity is the signal, and uniformity is invisible when you reread sentence by sentence. This is why `scripts/rewrite_human.py` exists: you cannot see a standard deviation by looking.

**Word-by-word translation.** A Vietnamese draft rendered clause by clause from an English one, or the reverse. It stays grammatical and reads foreign. `Điều này có nghĩa là` is a relative clause English needs and Vietnamese does not. `uy tín, chuyên nghiệp, tận tâm` is standard Vietnamese business copy that becomes `prestigious, professional, dedicated` — grammatical English that says nothing and signals nothing except that someone ran a dictionary over it.

A third failure travels with them and is checked here too: **decoration nobody chose**. See below.

In Vietnamese there is a fourth, and it is the loudest of all: the copy never decides who it is talking to. That has its own unit, [address-register.md](address-register.md), because it is grammar rather than rhythm and it needs a different verdict vocabulary.

## The rule that does most of the work

Translate the decision, not the sentence.

A sentence is the output of a decision somebody made about what the reader needs to know next. Word-by-word translation copies the output and throws the decision away, which is why the result is grammatical and dead. So go back one step: what fact does this sentence carry, what does the reader do with it, and how would somebody who has only ever spoken the target language deliver that fact?

Do this and the sentence boundaries move. Five English sentences become three Vietnamese ones. One Vietnamese sentence becomes two English ones with a fragment between them. If the sentence count survived intact, you translated words.

## Which language is the original

Default: **Vietnamese is written first, English is transcreated from it.** Two reasons. Most of this skill's work is aimed at Vietnamese buyers, and a Vietnamese draft translated out of English carries the calques in the table below no matter how carefully it is edited. Write Vietnamese to Vietnamese rhythm, then rebuild the English from the same facts.

Override when the brand's own voice was established in English, or the deliverable's primary audience reads English. Say which direction you chose in the run. Never present the transcreated version as a translation of the original. It is a second original built from the same truth map, and it will not be sentence-for-sentence parallel.

Claims, numbers, prices, and offers must match exactly. Rhythm, sentence count, and metaphors will not.

## Procedure

1. **Extract the facts.** List every checkable thing in the draft: numbers, dates, addresses, mechanisms, prices, guarantees. If the draft has fewer than three, the problem is not cadence — the copy has no content and rewriting it prettier makes it worse. Go back to the truth map and get facts. Prose without facts cannot be saved by rhythm.
2. **Measure the original.** `python scripts/rewrite_human.py --check draft.md`. Read the gate table and the tell table. Note which failures are cadence and which are calque; they need different repairs.
3. **Repair calques first.** Each row in `data/translation-tells.csv` carries the specific fix. Do them before touching rhythm, because deleting `Trong thế giới ngày nay` and `Hơn nữa` changes every length measurement downstream. Repairing cadence first means measuring it twice.
4. **Rebuild rhythm deliberately.** Not by adding variety at random. Decide where each claim lands, and put a short sentence there. Long sentences carry mechanism, because mechanism has subordinate parts. Short sentences carry consequence. A four-word sentence after a twenty-four-word one is where the reader believes you.
5. **Read three sentences aloud, in order.** The fastest tell in copy is rhythm, faster than vocabulary. If the same shape repeats, the ear catches it before any script does.
6. **Check what the sentences now have, not only what they lost.** The report's spoken-register section is the only one that reads for presence. On a channel where somebody is being spoken to, zero markers means step 4 rearranged a translation instead of replacing it.
7. **Measure again, and check the facts survived.** Compare the fact list from step 1 against the rewrite. A rewrite that reads better and lost the address is a worse deliverable. Rhythm work quietly deletes specifics, because specifics are the awkward part of a sentence.
8. **In Vietnamese, check the register.** `python scripts/check_address_register.py --check draft.md --channel social`. Do it after the cadence work, because splitting and merging sentences is where an address form gets dropped or a second one gets introduced. [address-register.md](address-register.md) explains the verdicts.
9. **Gate.** `scripts/rewrite_human.py` exits non-zero while any critical or high gate fails. Do not ship past it, and do not lower the target to pass.

`assets/examples/rewrite-human/` runs this procedure on one draft: the failing original, the
Vietnamese rewrite, and the English built from the same facts. Read it before your first rewrite;
the numbers in its README are the ones the script actually prints.

## Decoration: the emoji is not the defect

A rocket opening every bullet is the single most recognisable sign that nobody edited the output. But the defect is not the pictograph. It is that the pictograph arrived in a slot nobody chose.

That distinction is the whole rule. An emoji a writer put inside a sentence is a decision, and it can be the right one. An emoji opening every line of a list is a template.

So the script counts **structural** use — a pictograph in a heading, or the first thing on a line after the bullet or number — separately from **inline** use, and holds them to different budgets. A run of three lines opening on the *same* icon fails on every channel, including the ones where emoji are native, because a writer choosing an icon per line would have varied them.

Channels differ in kind, not in degree. On this skill's own deliverables, and on web, email, PR, decks and marketplace listings, the structural budget is zero: the reader is not expecting a pictograph, so there is no native use to protect. On social and chat, structure is unbounded and only density is held. A Vietnamese seller bulleting a Facebook post with a tick is doing what the surface does, and a gate that calls that a machine tell is simply wrong about the channel.

`python scripts/rewrite_human.py --check draft.md --channel social`. The default channel is `deliverable`, which allows none.

Meaning-bearing signs are never counted: `© ® ™ ° № ℃ ℉`. Every one of them sits in the same Unicode category as the rocket, so the allow-list is unavoidable — and a gate that flags the registered-trademark sign in brand copy is a gate that gets switched off in week one.

Two limits worth stating rather than discovering. The detector is Unicode general category `So` minus that allow-list, which is the honest thing the standard library can do. It is *not* UTS #51 `Extended_Pictographic`, a property Python's `unicodedata` does not expose at all, so keycap sequences slip through. And arrows and bullets are deliberately out of scope — `→` and `•` are ordinary typography with centuries behind them, and a gate that fires on correctly typeset copy stops being read.

## Structure above the sentence

Everything above this line measures sentences. That leaves a hole the size of a brief, because `prose_only()` blanks every list line before any cadence measurement runs. It has to: a bullet is not a sentence, and counting it as one wrecks the length statistics.

The cost is that list shape is invisible to every gate that reads prose, and a brief, a playbook or a checklist is mostly lists. Feed the script a document built entirely of bullets and it reports that there is not enough prose to measure. True, and useless.

So one structural measurement reads the raw text instead: **the share of lists holding exactly three items.** Above 0.60 it fails, at `high`. Under four lists the gate is not reported at all.

Not reported as passing, either. A file with two lists, both of three, scores 1.00 and has done nothing wrong, and a gate that claims "pass" on no evidence teaches you to trust it where you should not.

Three is the most rhetorically satisfying count in either language, which is exactly how it stops being a count and becomes a template. One list of three is three things somebody had. Nine lists of three is a form somebody filled in.

The 0.60 was measured rather than chosen. It came from this skill's own reference files, the only corpus to hand where every document was written by a person and then argued with, and there the share sat at 0.43 or below in every file but one.

The exception scored 0.80, and reading it confirmed the number instead of excusing it. Eight of its ten sections carried the identical `Core proofs / Useful scenes / Reject` triple, and the file turned out to duplicate `product-category-playbooks.md`, which covered the same categories and three more. So it was folded in and deleted rather than reshaped to pass. The threshold now sits mid-gap between 0.43 and 0.80 instead of at the edge of a narrow one, which is the only kind worth shipping.

One more thing to know before you read the tell tables. `data/translation-tells.csv` and `data/slop-tells.csv` carry the same sentence, *everything arrives in threes*, as two separate rows. They are two different defects.

`tricolon-default` is `scope: prose`, and its regex matches three comma-separated phrases inside one sentence. That is a cadence habit and often correct: it fires on "physics, claim, or rights failure" in `anti-ai-quality.md`, which is a writer counting three real things. `tricolon-everywhere` counts list lengths across the whole document, which is a structural habit and rarely correct. The regex cannot reach it, because the list lines are gone before it looks, so the second row named a measurement for a long time before anything performed it.

### Measured, then deliberately not shipped

Written down because the next person here will have the same two ideas, and they cost a morning each.

**Uniformity inside a single list.** Three or more items, length CV at or below 0.25, every item opening on a bold label. It tripped twenty-five blocks across twenty reference files, and every one of them was correct writing: the nine rejection codes in `anti-ai-quality.md`, the verdict vocabularies, the channel budget tables.

A glossary is uniform because it is a specification, and so is a rejection-code list. Gate that and your first twenty-five findings are wrong. Nobody runs that gate twice.

**A shared opening word across a list** tripped `human-imagery.md`, where six consecutive lines begin `No ` on purpose. Deliberate anaphora and generated filler are the same shape from outside. No regex separates them, so the ear keeps that one.

**Paragraph-length CV**, as a companion to sentence CV, went for a duller reason. On three realistic generated samples it added nothing at all: each already failed four sentence-level cadence gates. A signal that only ever fires next to signals you already have is noise in the report.

### The limit worth knowing

Flatten the template into paragraphs and this gate goes blind.

`product-category-playbooks.md` is the honest example, in this repository, right now: twelve sections, most of them running the same `Prioritize, then use, then reject` move as prose. Same three-part form as the file that was deleted for it, no list to count, so the gate passes it. Nothing here replaces reading two sections in a row and noticing they are the same section.

## Naming a word is not using it

Word tells are matched with inline code spans removed, and fenced blocks are out of the decoration
and list gates entirely. Put a word in backticks and the gate stops seeing it, which is the only way
a file can tell a writer to delete `seamless` without failing for the word `seamless`. Every
replacement table, glossary and worked bad example in this skill depends on it.

The convention that follows: when you are quoting a word rather than claiming it, backtick it. A word
in double quotes still counts as asserted, because quotation marks in marketing copy are usually
emphasis and sometimes sarcasm, and neither is a citation. Before this, the gate was failing files for
the words they were telling the reader to remove. That is backwards.

Two things this deliberately does not soften. A fenced block still counts toward nothing, so hiding a
paragraph in a fence hides it from every gate - that is a hole, and the only defence is that it is
obvious in review. And the cadence gates ignore all of this: a code span occupies its slot in a
sentence and the reader's eye lands on it, so length and rhythm are measured with it in place.

## A web page is read as a web page

Point `--check` at a file that declares a doctype and the script reads it as markup instead of prose. This
is not a convenience. Before it existed, `docs/index.html` reported a mean sentence length of 110.5
syllables against a target of 22, and a long/short ratio of 996 against a target of 3, because
`class="button primary copy-button"` has no full stop, so one tag ran into the next until something
finally ended in a period. Those numbers described nothing a writer could fix.

What it drops, and the reason is different in each case. `script`, `style`, `svg` and `template` are not
prose. `pre` and `code` are the page *quoting* something, which is the same rule the backtick convention
above already applies one level down - and it is the whole reason the reader exists. All three blocking
tells the old report found on that page (`Chúng tôi tự hào`, `một trong những`, `chất lượng cao`) were
real strings inside the `<pre>` of the before/after demo, which is the deliberately terrible draft the
page exists to hold up as terrible. The instrument was failing the exhibit for being the exhibit.

Copy that lives in an attribute is measured for `alt`, `title`, `aria-label`, `placeholder`, `content`
and the house `data-copy` / `data-toast` pair, and nowhere else. On this repository's landing page the
brief the visitor copies to their clipboard and the toast they get back both live in attributes, so they
are copy by any honest reading and were going unmeasured.

Each text node is measured as its own paragraph. Web copy is written in nodes and met in nodes: a heading
carries no full stop and a button label carries no verb, so a punctuation-driven splitter glues `Cài skill`
to whatever sentence follows it. Splitting by node moved `landing-beats` on that page from 0.04 per 150 to
13.4, which is the truth - a four-syllable heading is a landing beat.

One gate is absent rather than passing on markup, on the same terms as `LIST_BLOCKS_MIN` and the
formal-channel spoken floor. `mean-length-low` cannot be computed on a page: `docs/index.html` measures a
mean of 7.0 with a median of 4, because most of a page is labels (`Cài skill`, `Sản phẩm`, `01 / MẺ RANG`).
The gate exists to catch body prose that has been chopped up, and a mean over a population that is mostly
nav items is not a measurement of body prose. Its own escape hatch does not help either: `SHORT_FORM_UNITS`
lets a short *document* through, and a page is not short, it is short-nodded. Every other length gate
survives the split, and two get better for it.

It is not a parser. No HTML tree, no handling of `<` inside an attribute value, and a tag that a formatter
has split across two lines reads as text. Good enough for the pages in this repository, pinned by the tests
that measure them, and the sniff is deliberately narrow so it never claims to be a general extractor.

## Every gate above this line is subtractive

Delete `Hơn nữa`. Delete the em dash. Delete the icon. Break the flat run. That was a complete
description of this unit until 2026-08-05, and it has a hole in the middle of it.

A draft can pass every gate above, match no row in either tell table, and still be clean flat
translationese — because nothing here had ever asked what a Vietnamese sentence *has* when a
Vietnamese person wrote it. The hole was found by a reader on this repository's own landing page,
after the subtractive gates had all gone green, in three words: `word by word`.

`data/spoken-markers.csv` is the positive side, Vietnamese first. Twenty rows, fourteen Vietnamese and
six English, each carrying what it makes the sentence carry and the flat form that arrives in its
place when the sentence was translated instead of written.

| Marker | Human | Translated instead |
|---|---|---|
| final particle `nhé/nha` | `Để mình gói riêng phần đá nha.` | `Vui lòng giữ phần đá riêng biệt.` |
| topic fronted with `thì` | `Tiền vận chuyển thì shop chịu.` | `Shop sẽ chịu chi phí vận chuyển.` |
| aspect closing on `rồi` | `Ba giờ chiều là hết rồi.` | `Sản phẩm đã được bán hết vào lúc 15 giờ.` |
| `bị` with the affected party as subject | `Có hai đơn bị trễ, cả hai đều gọi trước.` | `Hai đơn hàng đã được giao trễ bởi đơn vị vận chuyển.` |

The right-hand column is grammatical. That is the point: none of those sentences is an error, and no
subtractive gate can object to any of them.

Three rows carry no regex — a serial verb chain, a benefactive `cho`, a concrete measure standing
where a degree adjective would go. The shape genuinely has none, and an empty pattern matches
everything silently, so those rows are marked `detect: manual` and the report says so rather than
claiming a check it never made.

### The floor is a count, because the rate was backwards

The first version of this gate measured distinct markers per 150 units. Measured on 2026-08-05:

| Text | Distinct per 150 | Distinct, whole document |
|---|---|---|
| ND87 advertising law, 2925 syllables | 0.00 | 0 |
| this file, its own English prose | 0.00 | 0 |
| `README.vi.md`, 5986 syllables | 0.15 | 6 |
| `docs/index.html`, 2635 syllables | 0.17 | 3 |
| a flat translated ad, 154 syllables | **0.97** | 1 |

The rate ranked the translationese six times above the hand-written page. It had to: the numerator is
capped at eleven matchable Vietnamese rows while the denominator grows without limit, so any
per-length normalisation of a bounded count inverts on long text. The count separates the same five
samples cleanly. The floor is two distinct markers, one under 60 units, and the margin is thin enough
to state — the landing page clears it with three.

### Two limits, both declared

**Not frequency-calibrated.** There is no human-written conversational Vietnamese corpus in this
repository. The markers are graded `grammar-descriptive` and `native-usage-sample`, which asserts
that each is a real structure of the language and asserts nothing about how often it should appear.
Nobody should read `>= 2 distinct` as a linguistic finding. It is a house floor that separates the
samples above and will move when there is something better to measure against.

**Formal human Vietnamese scores zero.** The ND87 text is written by a ministry, is unambiguously
human, and carries not one marker in 2925 syllables. So the gate is scoped to the channels where
somebody is being spoken to — `social`, `chat`, `email`, `web`, `marketplace`. On `deliverable`, `pr`
and `sales-deck` the measurement still prints, because a writer should see a zero, but no gate is
emitted. A floor that fails a ministry is a floor somebody switches off in week one.

### This does not license a texture pass

The last section of this file says not to rewrite by adding texture, and a floor on spoken markers is
exactly the instruction a lazy reader would break it with: put `nhé` on the end of five sentences and
the count is satisfied. So the second gate holds variety — past half the hits on one marker, once
there are four, something is being sprinkled rather than said. That gate exists to enforce the last
section of this file, not to contradict it.

The repair is never to add a particle. It is to find the sentence whose decision was translated, and
make that decision again in Vietnamese. The marker shows up because the decision did.

## What the script does not check

It measures cadence and matches known tells. It cannot tell you whether the copy is true, whether the claim is provable, whether the offer is legal in Vietnam, or whether the reader cares. Those stay with `claims-proof-ledger.md`, `rights-and-claims.md`, and the message architecture. A draft can pass every gate here and still be unpublishable.

It also cannot tell you the copy is any *good*. All a pass means is that the copy does not read machine-written, which is a floor and not a standard. The tension ladder in `data/copy-formulas.csv` is what raises it.

## Repair patterns

| Failure | Repair |
|---|---|
| CV below 0.45 | Find the longest sentence. Split it at the clause that stands alone. Then cut one adjacent sentence to under five words. Two edits usually clear the gate; twelve small edits do not. |
| Long/short ratio below 3.0 | You have no long sentence or no short one. Add the short one first — it is nearly always available by splitting off a consequence. |
| No landing beats | Every claim currently arrives mid-sentence. Pick the one claim that matters and give it its own line. A beat is four words or fewer in English, six syllables or fewer in Vietnamese — the same length, counted the way each language is written. |
| Flat run of 3+ | Three near-equal sentences in a row. Merge two of them, or split one. Do not adjust all three. |
| Same opener repeated | Usually `Chúng tôi` or `We` opening every sentence. Move the reader to the subject: what they get, what they do. |
| Most lists hold exactly three items | Not a list problem. Each three-item list is the visible end of a three-move template — usually claim, evidence, exclusion — applied to every section in turn. Pick the two sections that carry the most weight and rewrite those to whatever length the content is: one has five things, one has two, one is a sentence and no list at all. If every section genuinely has three, you are describing the template rather than the product. |
| Which-chain in English | `X, which is Y, which means Z` becomes three sentences. Order them so each earns the next. |
| Nominalisation stack in Vietnamese | `việc tối ưu hoá` back to the verb, with the agent in front of it. |
| Trust-adjective stack | Each adjective replaced by one verifiable thing, or deleted. Four adjectives rarely become four facts; usually two facts and a shorter paragraph. |
| Em dash in Vietnamese | Comma, colon, or full stop. The em dash arrived with the English draft. |
| Icon opening every bullet | Delete all of them, then ask whether any single line earns one back. Usually none does, and the list reads faster without. |
| No spoken markers at all | The copy was translated rather than written, and no single edit fixes it. Take the three sentences carrying the most weight and ask what decision each one made, then make that decision again in Vietnamese. Front the topic before its comment with `thì`. Point at one real thing with a classifier and a demonstrative — `cái tô đó`, not `sản phẩm này`. Close a clause on `rồi` where the English closed on a past tense. Do not add a particle to the sentences you left flat. |
| One marker holds most of the hits | A texture pass, not a rewrite. Delete every instance of that marker, then redo the paragraph from step 4 of the procedure. What comes back will be varied because the content chose it. |
| Same icon three lines running | Not a variety problem. The list is generated; rewrite the lines so they differ in content, and the icons stop being the only thing distinguishing them. |

## The one thing to avoid

Do not rewrite by adding texture. Inserting a fragment, an aside, a rhetorical question, and a contraction into flat prose produces prose that reads machine-written and *fussy*. The variation has to come from the content deciding where it needs a beat, not from a texture pass applied on top.

If a rewrite makes the copy longer, it probably failed. Human cadence is mostly a matter of what got cut.

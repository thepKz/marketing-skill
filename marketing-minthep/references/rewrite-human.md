# Rewrite human

Take a draft that reads machine-written or machine-translated, and make it read like a person wrote it in that language first. This is not editing for grammar. Grammatical prose is exactly what fails here.

Two distinct failures arrive looking the same.

**Machine cadence.** Every sentence is a similar length, every paragraph a similar shape, every list three items long, connected by furthermore and moreover. Each sentence passes on its own. The paragraph reads flat because uniformity is the signal, and uniformity is invisible when you reread sentence by sentence. This is why `scripts/rewrite_human.py` exists: you cannot see a standard deviation by looking.

**Word-by-word translation.** A Vietnamese draft rendered clause by clause from an English one, or the reverse. It stays grammatical and reads foreign. `Điều này có nghĩa là` is a relative clause English needs and Vietnamese does not. `uy tín, chuyên nghiệp, tận tâm` is standard Vietnamese business copy that becomes `prestigious, professional, dedicated` — grammatical English that says nothing and signals nothing except that someone ran a dictionary over it.

A third failure travels with them and is checked here too: **decoration nobody chose**. See below.

In Vietnamese there is a fourth, and it is the loudest of all: the copy never decides who it is talking to. That has its own unit, [address-register.md](address-register.md), because it is grammar rather than rhythm and it needs a different verdict vocabulary.

## The rule that does most of the work

Translate the decision, not the sentence.

A sentence is the output of a decision somebody made about what the reader needs to know next. Word-by-word translation copies the output and throws the decision away, which is why the result is grammatical and dead. So go back one step: what fact does this sentence carry, what does the reader do with it, and how would somebody who has only ever spoken the target language deliver that fact?

Do this and the sentence boundaries move. Five English sentences become three Vietnamese ones. One Vietnamese sentence becomes two English ones with a fragment between them. If the sentence count survived the translation intact, you translated words.

## Which language is the original

Default: **Vietnamese is written first, English is transcreated from it.** Two reasons. Most of this skill's work is aimed at Vietnamese buyers, and a Vietnamese draft translated out of English carries the calques in the table below no matter how carefully it is edited. Write Vietnamese to Vietnamese rhythm, then rebuild the English from the same facts.

Override when the brand's own voice was established in English, or the deliverable's primary audience reads English. Say which direction you chose in the run. Never present the transcreated version as a translation of the original — it is a second original built from the same truth map, and it will not be sentence-for-sentence parallel. Claims, numbers, prices, and offers must match exactly. Rhythm, sentence count, and metaphors will not.

## Procedure

1. **Extract the facts.** List every checkable thing in the draft: numbers, dates, addresses, mechanisms, prices, guarantees. If the draft has fewer than three, the problem is not cadence — the copy has no content and rewriting it prettier makes it worse. Go back to the truth map and get facts. Prose without facts cannot be saved by rhythm.
2. **Measure the original.** `python scripts/rewrite_human.py --check draft.md`. Read the gate table and the tell table. Note which failures are cadence and which are calque; they need different repairs.
3. **Repair calques first.** Each row in `data/translation-tells.csv` carries the specific fix. Do them before touching rhythm, because deleting `Trong thế giới ngày nay` and `Hơn nữa` changes every length measurement downstream. Repairing cadence first means measuring it twice.
4. **Rebuild rhythm deliberately.** Not by adding variety at random. Decide where each claim lands, and put a short sentence there. Long sentences carry mechanism, because mechanism has subordinate parts. Short sentences carry consequence. A four-word sentence after a twenty-four-word one is where the reader believes you.
5. **Read three sentences aloud, in order.** The fastest tell in copy is rhythm, faster than vocabulary. If the same shape repeats, the ear catches it before any script does.
6. **Measure again, and check the facts survived.** Compare the fact list from step 1 against the rewrite. A rewrite that reads better and lost the address is a worse deliverable. Rhythm work quietly deletes specifics, because specifics are the awkward part of a sentence.
7. **In Vietnamese, check the register.** `python scripts/check_address_register.py --check draft.md --channel social`. Do it after the cadence work, because splitting and merging sentences is where an address form gets dropped or a second one gets introduced. [address-register.md](address-register.md) explains the verdicts.
8. **Gate.** `scripts/rewrite_human.py` exits non-zero while any critical or high gate fails. Do not ship past it, and do not lower the target to pass.

`assets/examples/rewrite-human/` runs this procedure on one draft: the failing original, the
Vietnamese rewrite, and the English built from the same facts. Read it before your first rewrite;
the numbers in its README are the ones the script actually prints.

## Decoration: the emoji is not the defect

A rocket opening every bullet is the single most recognisable sign that nobody edited the output. But the defect is not the pictograph. It is that the pictograph arrived in a slot nobody chose.

That distinction is the whole rule. An emoji a writer put inside a sentence is a decision, and it can be the right one. An emoji opening every line of a list is a template. So the script counts **structural** use — a pictograph in a heading, or the first thing on a line after the bullet or number — separately from **inline** use, and holds them to different budgets. A run of three lines opening on the *same* icon fails on every channel, including the ones where emoji are native, because a writer choosing an icon per line would have varied them.

Channels differ in kind, not in degree. On this skill's own deliverables, and on web, email, PR, decks and marketplace listings, the structural budget is zero: the reader is not expecting a pictograph, so there is no native use to protect. On social and chat, structure is unbounded and only density is held. A Vietnamese seller bulleting a Facebook post with a tick is doing what the surface does, and a gate that calls that a machine tell is simply wrong about the channel.

`python scripts/rewrite_human.py --check draft.md --channel social`. The default channel is `deliverable`, which allows none.

Meaning-bearing signs are never counted: `© ® ™ ° № ℃ ℉`. Every one of them sits in the same Unicode category as the rocket, so the allow-list is unavoidable — and a gate that flags the registered-trademark sign in brand copy is a gate that gets switched off in week one.

Two limits worth stating rather than discovering. The detector is Unicode general category `So` minus that allow-list, which is the honest thing the standard library can do; it is *not* UTS #51 `Extended_Pictographic`, which Python's `unicodedata` does not expose, so keycap sequences slip through. And arrows and bullets are deliberately out of scope — `→` and `•` are ordinary typography with centuries behind them, and a gate that fires on correctly typeset copy stops being read.

## What the script does not check

It measures cadence and matches known tells. It cannot tell you whether the copy is true, whether the claim is provable, whether the offer is legal in this market, or whether the reader cares. Those stay with `claims-proof-ledger.md`, `rights-and-claims.md`, and the message architecture. A draft can pass every gate here and still be unpublishable.

It also cannot tell you the copy is *good*. Passing means it does not read machine-written. The tension ladder in `data/copy-formulas.csv` is what makes it work.

## Repair patterns

| Failure | Repair |
|---|---|
| CV below 0.45 | Find the longest sentence. Split it at the clause that stands alone. Then cut one adjacent sentence to under five words. Two edits usually clear the gate; twelve small edits do not. |
| Long/short ratio below 3.0 | You have no long sentence or no short one. Add the short one first — it is nearly always available by splitting off a consequence. |
| No landing beats | Every claim currently arrives mid-sentence. Pick the one claim that matters and give it its own line. A beat is four words or fewer in English, six syllables or fewer in Vietnamese — the same length, counted the way each language is written. |
| Flat run of 3+ | Three near-equal sentences in a row. Merge two of them, or split one. Do not adjust all three. |
| Same opener repeated | Usually `Chúng tôi` or `We` opening every sentence. Move the reader to the subject: what they get, what they do. |
| Which-chain in English | `X, which is Y, which means Z` becomes three sentences. Order them so each earns the next. |
| Nominalisation stack in Vietnamese | `việc tối ưu hoá` back to the verb, with the agent in front of it. |
| Trust-adjective stack | Each adjective replaced by one verifiable thing, or deleted. Four adjectives rarely become four facts; usually two facts and a shorter paragraph. |
| Em dash in Vietnamese | Comma, colon, or full stop. The em dash arrived with the English draft. |
| Icon opening every bullet | Delete all of them, then ask whether any single line earns one back. Usually none does, and the list reads faster without. |
| Same icon three lines running | Not a variety problem. The list is generated; rewrite the lines so they differ in content, and the icons stop being the only thing distinguishing them. |

## The one thing to avoid

Do not rewrite by adding texture. Inserting a fragment, an aside, a rhetorical question, and a contraction into flat prose produces prose that reads machine-written and *fussy*. The variation has to come from the content deciding where it needs a beat, not from a texture pass applied on top.

If a rewrite makes the copy longer, it probably failed. Human cadence is mostly a matter of what got cut.

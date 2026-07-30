# Rewrite human

Take a draft that reads machine-written or machine-translated, and make it read like a person wrote it in that language first. This is not editing for grammar. Grammatical prose is exactly what fails here.

Two distinct failures arrive looking the same.

**Machine cadence.** Every sentence is a similar length, every paragraph a similar shape, every list three items long, connected by furthermore and moreover. Each sentence passes on its own. The paragraph reads flat because uniformity is the signal, and uniformity is invisible when you reread sentence by sentence. This is why `scripts/rewrite_human.py` exists: you cannot see a standard deviation by looking.

**Word-by-word translation.** A Vietnamese draft rendered clause by clause from an English one, or the reverse. It stays grammatical and reads foreign. `Điều này có nghĩa là` is a relative clause English needs and Vietnamese does not. `uy tín, chuyên nghiệp, tận tâm` is standard Vietnamese business copy that becomes `prestigious, professional, dedicated` — grammatical English that says nothing and signals nothing except that someone ran a dictionary over it.

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
7. **Gate.** `scripts/rewrite_human.py` exits non-zero while any critical or high gate fails. Do not ship past it, and do not lower the target to pass.

`assets/examples/rewrite-human/` runs this procedure on one draft: the failing original, the
Vietnamese rewrite, and the English built from the same facts. Read it before your first rewrite;
the numbers in its README are the ones the script actually prints.

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

## The one thing to avoid

Do not rewrite by adding texture. Inserting a fragment, an aside, a rhetorical question, and a contraction into flat prose produces prose that reads machine-written and *fussy*. The variation has to come from the content deciding where it needs a beat, not from a texture pass applied on top.

If a rewrite makes the copy longer, it probably failed. Human cadence is mostly a matter of what got cut.
